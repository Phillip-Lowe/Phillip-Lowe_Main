#!/usr/bin/env node
/**
 * Green n8n Monitor — Main monitoring engine
 * 
 * Usage:
 *   node monitor.js
 *   node monitor.js --webhook https://hooks.slack.com/services/xxx
 *   node monitor.js --dashboard dashboard.html
 *   node monitor.js --interval 300000
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const configPath = path.join(__dirname, 'config.json');
const config = fs.existsSync(configPath) ? JSON.parse(fs.readFileSync(configPath, 'utf8')) : {};

const N8N_KEY = process.env.N8N_API_KEY || config.n8nApiKey;
const N8N_URL = process.env.N8N_URL || config.n8nUrl;
const RESEND_KEY = process.env.RESEND_API_KEY;
const ALERT_EMAIL = process.env.ALERT_EMAIL || config.alertEmail;

function parseArgs() {
  const args = {};
  for (let i = 2; i < process.argv.length; i++) {
    if (process.argv[i] === '--webhook') args.webhook = process.argv[++i];
    if (process.argv[i] === '--dashboard') args.dashboard = process.argv[++i];
    if (process.argv[i] === '--interval') args.interval = parseInt(process.argv[++i]);
  }
  return args;
}

function httpRequest(method, url, body, headers = {}) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const client = u.protocol === 'https:' ? https : http;
    const data = body ? JSON.stringify(body) : null;
    const req = client.request({
      hostname: u.hostname,
      path: u.pathname + u.search,
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(data ? { 'Content-Length': Buffer.byteLength(data) } : {}),
        ...headers
      }
    }, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => resolve({ status: res.statusCode, data: d }));
    });
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

// Fetch executions from n8n API
async function fetchExecutions() {
  const url = `${N8N_URL}/api/v1/executions?limit=${config.maxExecutions || 50}&includeData=false`;
  const res = await httpRequest('GET', url, null, {
    'X-N8N-API-KEY': N8N_KEY
  });
  if (res.status !== 200) {
    throw new Error(`n8n API returned ${res.status}: ${res.data}`);
  }
  return JSON.parse(res.data);
}

// Fetch workflow details
async function fetchWorkflow(id) {
  const url = `${N8N_URL}/api/v1/workflows/${id}`;
  const res = await httpRequest('GET', url, null, {
    'X-N8N-API-KEY': N8N_KEY
  });
  if (res.status !== 200) return null;
  return JSON.parse(res.data);
}

// Log execution
function logExecution(exec, workflowName) {
  const file = config.trackingFile || path.join(__dirname, 'execution-log.csv');
  const exists = fs.existsSync(file);
  if (!exists) {
    fs.writeFileSync(file, 'timestamp,workflow_id,workflow_name,execution_id,status,duration,error_message\n');
  }
  const error = exec.data?.resultData?.error?.message || '';
  const duration = exec.stoppedAt && exec.startedAt
    ? new Date(exec.stoppedAt).getTime() - new Date(exec.startedAt).getTime()
    : 0;
  fs.appendFileSync(file, `${new Date().toISOString()},${exec.workflowId},${workflowName},${exec.id},${exec.status},${duration},"${error.replace(/"/g, '\"')}"\n`);
}

// Send email alert via Resend
async function sendEmailAlert(alert) {
  if (!RESEND_KEY || !ALERT_EMAIL) return;
  const body = `
🚨 n8n Workflow Failure

Workflow: ${alert.workflow.name}
Execution ID: ${alert.execution.id}
Status: ${alert.execution.status}
Error: ${alert.execution.error || 'Unknown error'}
Time: ${alert.execution.startedAt}
Duration: ${alert.execution.duration}ms

Check n8n: ${N8N_URL}/workflow/${alert.workflow.id}/executions/${alert.execution.id}
  `.trim();
  
  await httpRequest('POST', 'https://api.resend.com/emails', {
    from: 'n8n-monitor@systack.net',
    to: [ALERT_EMAIL],
    subject: `🚨 n8n: ${alert.workflow.name} failed`,
    text: body
  }, { 'Authorization': 'Bearer ' + RESEND_KEY });
}

// Send webhook alert
async function sendWebhookAlert(alert, webhookUrl) {
  if (!webhookUrl) return;
  await httpRequest('POST', webhookUrl, alert);
}

// Process executions
async function processExecutions(args) {
  console.log(`🟢 Green n8n Monitor`);
  console.log(`Fetching executions from ${N8N_URL}...\n`);
  
  const data = await fetchExecutions();
  const executions = data.data || [];
  
  const failed = executions.filter(e => e.status === 'error' || e.status === 'crashed');
  const successful = executions.filter(e => e.status === 'success');
  
  console.log(`Total executions: ${executions.length}`);
  console.log(`Successful: ${successful.length}`);
  console.log(`Failed: ${failed.length}\n`);
  
  // Log all or just failures
  const toLog = config.includeSuccessful ? executions : failed;
  
  for (const exec of toLog) {
    const workflow = await fetchWorkflow(exec.workflowId);
    const workflowName = workflow?.name || exec.workflowId;
    
    logExecution(exec, workflowName);
    
    if (exec.status === 'error' || exec.status === 'crashed') {
      const alert = {
        alert: 'n8n_workflow_failure',
        timestamp: new Date().toISOString(),
        workflow: {
          id: exec.workflowId,
          name: workflowName
        },
        execution: {
          id: exec.id,
          status: exec.status,
          startedAt: exec.startedAt,
          stoppedAt: exec.stoppedAt,
          duration: exec.stoppedAt && exec.startedAt
            ? new Date(exec.stoppedAt).getTime() - new Date(exec.startedAt).getTime()
            : 0,
          error: exec.data?.resultData?.error?.message || 'Unknown error'
        }
      };
      
      console.log(`🚨 ALERT: ${workflowName} failed (execution ${exec.id})`);
      console.log(`   Error: ${alert.execution.error}`);
      console.log(`   Link: ${N8N_URL}/workflow/${exec.workflowId}/executions/${exec.id}\n`);
      
      await sendEmailAlert(alert);
      if (args.webhook) {
        await sendWebhookAlert(alert, args.webhook);
        console.log(`   Webhook sent to ${args.webhook}`);
      }
    }
  }
  
  // Generate dashboard if requested
  if (args.dashboard) {
    await generateDashboard(args.dashboard, executions);
    console.log(`📊 Dashboard saved to ${args.dashboard}`);
  }
  
  return failed.length;
}

// Generate HTML dashboard
async function generateDashboard(outputPath, executions) {
  const workflows = {};
  executions.forEach(e => {
    if (!workflows[e.workflowId]) {
      workflows[e.workflowId] = { id: e.workflowId, runs: [], success: 0, failed: 0 };
    }
    workflows[e.workflowId].runs.push(e);
    if (e.status === 'success') workflows[e.workflowId].success++;
    else workflows[e.workflowId].failed++;
  });
  
  const workflowList = Object.values(workflows).map(w => {
    const total = w.runs.length;
    const rate = total > 0 ? ((w.success / total) * 100).toFixed(1) : 0;
    return `
    <tr>
      <td>${w.id}</td>
      <td>${w.success}</td>
      <td>${w.failed}</td>
      <td>${total}</td>
      <td>${rate}%</td>
    </tr>`;
  }).join('');
  
  const html = `<!DOCTYPE html>
<html><head><title>Green n8n Dashboard</title>
<style>
body{font-family:sans-serif;max-width:900px;margin:2em auto;padding:0 1em;}
table{width:100%;border-collapse:collapse;margin-top:1em;}
th,td{padding:8px 12px;text-align:left;border-bottom:1px solid #ddd;}
th{background:#2d5a3d;color:#fff;}
tr:hover{background:#f5f5f5;}
.status-ok{color:green;}.status-error{color:red;}
</style></head><body>
<h1>🟢 Green n8n Dashboard</h1>
<p>Generated: ${new Date().toISOString()}</p>
<h2>Workflow Health</h2>
<table>
<tr><th>Workflow</th><th>Success</th><th>Failed</th><th>Total</th><th>Success Rate</th></tr>
${workflowList}
</table>
<p><em>Auto-refreshes every 5 minutes</em></p>
</body></html>`;
  
  fs.writeFileSync(outputPath, html);
}

// Main
async function main() {
  const args = parseArgs();
  
  if (!N8N_KEY) { console.error('Set N8N_API_KEY environment variable'); return; }
  if (!N8N_URL) { console.error('Set N8N_URL environment variable'); return; }
  
  const run = async () => {
    try {
      const failed = await processExecutions(args);
      if (!args.interval) {
        console.log(`\n✅ Monitor complete. ${failed} failures detected.`);
      }
    } catch (e) {
      console.error(`❌ Monitor error: ${e.message}`);
    }
  };
  
  await run();
  
  if (args.interval) {
    console.log(`\n🔄 Running every ${args.interval}ms. Press Ctrl+C to stop.`);
    setInterval(run, args.interval);
  }
}

main().catch(e => { console.error('Error:', e.message); process.exit(1); });
