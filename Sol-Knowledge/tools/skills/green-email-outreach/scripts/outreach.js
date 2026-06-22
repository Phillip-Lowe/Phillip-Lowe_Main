#!/usr/bin/env node
/**
 * Green Email Outreach — Main send engine
 * 
 * Usage:
 *   node outreach.js --source leads.csv --template templates/systack-intro.txt --from "Green <green@systack.net>"
 *   node outreach.js --source leads.csv --template templates/systack-intro.txt --dry-run
 *   node outreach.js --drip --days 3 --template templates/systack-followup.txt
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const configPath = path.join(__dirname, 'config.json');
const config = fs.existsSync(configPath) ? JSON.parse(fs.readFileSync(configPath, 'utf8')) : {};

const RESEND_KEY = process.env.RESEND_API_KEY;
const DRY_RUN = process.argv.includes('--dry-run');
const IS_DRIP = process.argv.includes('--drip');

function parseArgs() {
  const args = {};
  for (let i = 2; i < process.argv.length; i++) {
    if (process.argv[i] === '--source') args.source = process.argv[++i];
    if (process.argv[i] === '--template') args.template = process.argv[++i];
    if (process.argv[i] === '--from') args.from = process.argv[++i];
    if (process.argv[i] === '--days') args.days = parseInt(process.argv[++i]);
    if (process.argv[i] === '--tag') args.tag = process.argv[++i];
  }
  return args;
}

function httpPost(url, body, headers = {}) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const data = JSON.stringify(body);
    const req = https.request({
      hostname: u.hostname, path: u.pathname, method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data), ...headers }
    }, res => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => resolve({ status: res.statusCode, data: d }));
    });
    req.on('error', reject);
    req.write(data); req.end();
  });
}

// Parse CSV
function parseCSV(filepath) {
  const content = fs.readFileSync(filepath, 'utf8');
  const lines = content.trim().split('\n');
  const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
  return lines.slice(1).map(line => {
    const values = line.match(/(".*?"|[^,]+)/g) || [];
    const obj = {};
    headers.forEach((h, i) => { obj[h] = (values[i] || '').replace(/"/g, '').trim(); });
    return obj;
  });
}

// Load template
function loadTemplate(filepath) {
  return fs.readFileSync(filepath, 'utf8');
}

// Fill template variables
function fillTemplate(template, lead, sender) {
  let filled = template;
  const vars = { ...lead, ...sender };
  for (const [key, val] of Object.entries(vars)) {
    filled = filled.replace(new RegExp(`\\{${key}\\}`, 'g'), val || '');
  }
  return filled;
}

// Extract subject from template
function extractSubject(filled) {
  const match = filled.match(/^Subject:\s*(.+)/i);
  if (match) {
    return { subject: match[1].trim(), body: filled.replace(/^Subject:.+\n+/i, '').trim() };
  }
  return { subject: 'Quick question', body: filled.trim() };
}

// Load suppression list
function loadSuppression() {
  const file = config.suppressionFile || path.join(__dirname, 'suppression.txt');
  if (!fs.existsSync(file)) return new Set();
  return new Set(fs.readFileSync(file, 'utf8').split('\n').map(e => e.trim().toLowerCase()).filter(Boolean));
}

// Log send
function logSend(lead, status, messageId, template) {
  const file = config.trackingFile || path.join(__dirname, 'send-log.csv');
  const exists = fs.existsSync(file);
  if (!exists) fs.writeFileSync(file, 'timestamp,email,company,status,template,message_id,campaign_tag\n');
  const tag = (process.argv.find(a => a === '--tag') && process.argv[process.argv.indexOf('--tag') + 1]) || '';
  fs.appendFileSync(file, `${new Date().toISOString()},${lead.email},${lead.company || ''},${status},${template || ''},${messageId || ''},${tag}\n`);
}

// Send via Resend
async function sendResend(from, to, subject, body) {
  if (DRY_RUN) { console.log(`  [DRY] Would send to ${to}: ${subject}`); return { id: 'dry-run' }; }
  const res = await httpPost('https://api.resend.com/emails', {
    from, to: [to], subject, text: body
  }, { 'Authorization': 'Bearer ' + RESEND_KEY });
  const json = JSON.parse(res.data);
  return json;
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// Auto-generate pain point from domain
async function generatePainPoint(lead) {
  if (lead.pain_point) return lead.pain_point;
  const domain = lead.domain || lead.company?.toLowerCase().replace(/\s+/g, '') + '.com';
  if (!domain) return 'might benefit from better automation';
  return 'could save time with automated systems';
}

// Drip follow-up logic
async function runDrip(args) {
  const file = config.trackingFile || path.join(__dirname, 'send-log.csv');
  if (!fs.existsSync(file)) { console.log('No send log found. Run initial campaign first.'); return; }
  
  const days = args.days || 3;
  const cutoff = new Date(Date.now() - days * 86400000);
  const log = parseCSV(file);
  
  // Find leads sent X days ago with no reply
  const initialSends = log.filter(l => {
    const sent = new Date(l.timestamp);
    return l.status === 'sent' && sent < cutoff && !l.campaign_tag?.includes('followup');
  });
  
  console.log(`Found ${initialSends.length} leads eligible for ${days}-day follow-up`);
  
  if (!args.template) { console.log('⚠️  No follow-up template specified. Use --template'); return; }
  const template = loadTemplate(args.template);
  
  let sent = 0;
  for (const entry of initialSends) {
    const lead = { email: entry.email, company: entry.company, first_name: entry.email.split('@')[0] };
    const painPoint = await generatePainPoint(lead);
    const filled = fillTemplate(template, { ...lead, pain_point: painPoint }, { sender_name: 'Green', sender_title: 'Systack Automation' });
    const { subject, body } = extractSubject(filled);
    
    try {
      const result = await sendResend(args.from || config.from || 'Green <green@systack.net>', lead.email, subject, body);
      if (result.id) {
        sent++;
        logSend(lead, 'sent', result.id, path.basename(args.template));
        console.log(`✅ Follow-up ${sent}. ${lead.email} — "${subject}"`);
      }
    } catch (e) {
      logSend(lead, 'failed', '', path.basename(args.template));
      console.log(`❌ Failed: ${lead.email} — ${e.message}`);
    }
    
    await sleep(config.delayBetweenMs || 3000);
  }
  
  console.log(`\n📊 Drip done: ${sent} follow-ups sent`);
}

// Main
async function main() {
  const args = parseArgs();
  
  if (IS_DRIP) { await runDrip(args); return; }
  
  if (!args.source) { console.log('Usage: node outreach.js --source leads.csv --template template.txt --from "Name <email>" [--dry-run]'); return; }
  if (!RESEND_KEY && !DRY_RUN) { console.error('Set RESEND_API_KEY environment variable'); return; }

  const leads = parseCSV(args.source);
  const template = args.template ? loadTemplate(args.template) : config.defaultTemplate || 'Hi {first_name}, I wanted to reach out about {company}.';
  const from = args.from || config.from || 'Green <green@systack.net>';
  const suppression = loadSuppression();
  const maxPerDay = config.maxPerDay || 25;
  const delay = config.delayBetweenMs || 3000;
  const templateName = args.template ? path.basename(args.template) : 'default';

  console.log(`\n🟢 Green Email Outreach`);
  console.log(`Leads: ${leads.length} | Max/day: ${maxPerDay} | Delay: ${delay}ms | ${DRY_RUN ? 'DRY RUN' : 'LIVE'}\n`);

  let sent = 0, skipped = 0, failed = 0;

  for (const lead of leads) {
    if (sent >= maxPerDay) { console.log(`\n⚠️  Daily limit (${maxPerDay}) reached. Resume tomorrow.`); break; }
    if (!lead.email) { skipped++; continue; }
    if (suppression.has(lead.email.toLowerCase())) { console.log(`  ⏭️  Suppressed: ${lead.email}`); skipped++; continue; }

    const painPoint = await generatePainPoint(lead);
    const filled = fillTemplate(template, { ...lead, pain_point: painPoint }, { sender_name: 'Green', sender_title: 'Systack Automation' });
    const { subject, body } = extractSubject(filled);

    try {
      const result = await sendResend(from, lead.email, subject, body);
      if (result.id) {
        sent++;
        logSend(lead, 'sent', result.id, templateName);
        console.log(`✅ ${sent}. ${lead.email} — "${subject}"`);
      } else {
        failed++;
        logSend(lead, 'failed', '', templateName);
        console.log(`❌ Failed: ${lead.email}`);
      }
    } catch (e) {
      failed++;
      logSend(lead, 'error', '', templateName);
      console.log(`❌ Error: ${lead.email} — ${e.message}`);
    }

    if (sent < leads.length) await sleep(delay);
  }

  console.log(`\n📊 Done: ${sent} sent, ${skipped} skipped, ${failed} failed`);
}

main().catch(e => { console.error('Error:', e.message); process.exit(1); });
