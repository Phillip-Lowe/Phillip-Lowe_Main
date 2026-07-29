import { workflow, node, trigger, ifElse } from '@n8n/workflow-sdk';

// ============================================================
// SAOS Automation Audit v2 — Simple Orchestrator Workflow
// Calls local Python orchestrator at http://127.0.0.1:9877/audit
// ============================================================

const auditWebhook = trigger({
  type: 'n8n-nodes-base.webhook',
  version: 2.1,
  config: {
    name: 'Audit Webhook',
    position: [240, 300],
    parameters: {
      httpMethod: 'POST',
      path: 'saos-automation-audit-v2',
      authentication: 'none',
      responseMode: 'responseNode',
      options: {
        allowedOrigins: '*',
      },
    },
  },
  output: [{
    headers: {},
    body: {
      website: 'https://example.com',
      email: 'test@example.com',
      business_name: 'Example Inc',
      industry: 'hvac',
      employees: '1-10',
      pain_point: '',
    },
  }],
});

const callOrchestrator = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.4,
  config: {
    name: 'Call Audit Orchestrator',
    position: [540, 300],
    parameters: {
      method: 'POST',
      url: 'http://127.0.0.1:9877/audit',
      sendBody: true,
      contentType: 'json',
      specifyBody: 'json',
      jsonBody: '={{ JSON.stringify($json.body) }}',
      sendHeaders: true,
      specifyHeaders: 'json',
      jsonHeaders: '={{ JSON.stringify({ "X-Forwarded-For": $json.headers["x-forwarded-for"] || $json.headers["x-real-ip"] || "0.0.0.0", "User-Agent": $json.headers["user-agent"] || "" }) }}',
      options: {
        timeout: 90000,
        response: { response: { responseFormat: 'json', neverError: true } },
      },
    },
  },
  output: [{ json: { status: 'ok', score: 50, grade: 'Needs Work' } }],
});

const returnAuditResult = node({
  type: 'n8n-nodes-base.respondToWebhook',
  version: 1.5,
  config: {
    name: 'Return Audit Result',
    position: [1080, 200],
    parameters: {
      respondWith: 'firstIncomingItem',
      options: { responseCode: 200 },
    },
  },
});

const checkRateLimit = ifElse({
  version: 2.3,
  config: {
    name: 'Rate Limited?',
    position: [840, 300],
    parameters: {
      conditions: {
        combinator: 'and',
        options: { caseSensitive: false, leftValue: '', typeValidation: 'strict', version: 1 },
        conditions: [
          {
            id: 'r1',
            leftValue: '={{ $json.error }}',
            rightValue: 'Rate limit reached',
            operator: { type: 'string', operation: 'equals' },
          },
        ],
      },
    },
  },
});

const rateLimitResponse = node({
  type: 'n8n-nodes-base.respondToWebhook',
  version: 1.5,
  config: {
    name: 'Return Rate Limit Message',
    position: [1080, 400],
    parameters: {
      respondWith: 'json',
      responseBody: {
        status: 'rate_limited',
        message: "You've reached the daily audit limit for this website or email. Please try again tomorrow, or email plowe@systack.net to request a manual audit.",
        retry_after: '24 hours',
      },
      options: { responseCode: 200 },
    },
  },
});

const buildEmail = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Build Email',
    position: [840, 520],
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: `
const input = $input.first().json;
const audit = input;
const email = audit.email;
const business_name = audit.business_name;
const findings = (audit.findings || []).slice(0, 6);
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/\u0026/g, '\u0026amp;')
    .replace(/\u003c/g, '\u0026lt;')
    .replace(/\u003e/g, '\u0026gt;')
    .replace(/"/g, '\u0026quot;')
    .replace(/'/g, '\u0026#039;');
}
const findingsHtml = findings.map(f => \`
  <div style="margin-bottom:18px; padding-bottom:18px; border-bottom:1px solid #2a2a3a;">
    <div style="font-size:1.2rem; margin-bottom:4px;">${escapeHtml(f.icon)}</div>
    <div style="font-weight:600; color:#e0e0e0;">${escapeHtml(f.title)} <span style="color:#888; font-size:0.8rem;">(${escapeHtml(f.confidence)})</span></div>
    <div style="color:#a0a0b0; font-size:0.9rem; margin-top:4px;">${escapeHtml(f.evidence)}</div>
    <div style="color:#ff7043; font-weight:600; font-size:0.9rem; margin-top:4px;">${escapeHtml(f.cost)}</div>
    <div style="color:#4fc3f7; font-size:0.9rem; margin-top:4px;">→ ${escapeHtml(f.recommendation)}</div>
  </div>
\`).join('');
const htmlBody = \`<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="background:#0a0a0f; color:#e0e0e0; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif; margin:0; padding:0;">
  <div style="max-width:600px; margin:0 auto; padding:32px 20px;">
    <div style="text-align:center; background:#15151f; border:1px solid #2a2a3a; border-radius:16px; padding:32px; margin-bottom:24px;">
      <div style="font-size:3rem; font-weight:800; color:${escapeHtml(audit.grade_color)};">${audit.score}/100</div>
      <div style="font-size:0.85rem; color:#666; text-transform:uppercase; letter-spacing:1px; margin-top:8px;">Automation Score</div>
      <div style="font-size:1.2rem; font-weight:600; color:${escapeHtml(audit.grade_color)}; margin-top:12px;">${escapeHtml(audit.grade)}</div>
      <div style="font-size:0.9rem; color:#888; margin-top:8px;">Confidence: ${audit.confidence}%</div>
    </div>
    <div style="text-align:center; background:linear-gradient(135deg,rgba(244,67,54,0.1),rgba(255,152,0,0.1)); border:1px solid rgba(244,67,54,0.2); border-radius:16px; padding:28px; margin-bottom:24px;">
      <div style="font-size:1.8rem; font-weight:800; color:#ff7043;">${escapeHtml(audit.revenue_impact)}</div>
      <div style="color:#a0a0b0; margin-top:4px;">Estimated Annual Revenue Impact</div>
    </div>
    <div style="background:#15151f; border:1px solid #2a2a3a; border-radius:16px; padding:28px; margin-bottom:24px;">
      <h3 style="margin-top:0; color:#e0e0e0;">What We Found</h3>
      ${findingsHtml}
    </div>
    <div style="text-align:center; background:linear-gradient(135deg,rgba(79,195,247,0.1),rgba(41,182,246,0.1)); border:1px solid rgba(79,195,247,0.2); border-radius:16px; padding:28px;">
      <h3 style="margin-top:0;">Ready to Fix These?</h3>
      <p style="color:#a0a0b0;">Book a free 30-minute strategy call. We'll show you exactly how to plug these revenue leaks.</p>
      <a href="mailto:plowe@systack.net?subject=Strategy%20Call%20Request%20%E2%80%94%20Automation%20Audit" style="display:inline-block; padding:14px 32px; background:#4fc3f7; color:#0a0a0f; border-radius:12px; text-decoration:none; font-weight:700;">Book My Strategy Call</a>
    </div>
    <p style="text-align:center; color:#555; font-size:0.8rem; margin-top:24px;">Generated by SyStack · Evidence-based automation audit</p>
  </div>
</body>
</html>\`;
const textBody = \`Your Automation Audit Score: ${audit.score}/100 (${audit.grade})
Confidence: ${audit.confidence}%
Estimated Annual Revenue Impact: ${audit.revenue_impact}

What We Found:
${findings.map(f => \`- ${f.title} (${f.confidence})
  ${f.evidence}
  Cost: ${f.cost}
  → ${f.recommendation}\`).join('\\n\\n')}

Ready to fix these? Reply to this email or email plowe@systack.net to book a free 30-minute strategy call.

Generated by SyStack · Evidence-based automation audit\`;
return [{
  json: {
    emailTo: email,
    emailSubject: `${escapeHtml(business_name)} — Your Automation Audit Score: ${audit.score}/100`,
    emailHtml: htmlBody,
    emailText: textBody,
  }
}];
      `,
    },
  },
});

const sendEmail = node({
  type: 'n8n-nodes-base.emailSend',
  version: 2.1,
  config: {
    name: 'Email Report to Prospect',
    position: [1080, 520],
    parameters: {
      fromEmail: 'SyStack <support@systack.net>',
      toEmail: '={{ $json.emailTo }}',
      subject: '={{ $json.emailSubject }}',
      emailFormat: 'both',
      html: '={{ $json.emailHtml }}',
      text: '={{ $json.emailText }}',
      options: { appendAttribution: false, replyTo: 'plowe@systack.net' },
    },
  },
  credentials: { smtp: { id: 'U7QjoOL2sgu4KLs6', name: 'Support Systack SMTP account' } },
});

const errorTrigger = trigger({
  type: 'n8n-nodes-base.errorTrigger',
  version: 1,
  config: {
    name: 'Error Trigger',
    position: [240, 900],
  },
  output: [{ error: { message: 'Error', node: { name: 'Node' } }, execution: { id: 'test' } }],
});

const buildErrorEmail = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Build Error Email',
    position: [540, 900],
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: `
const err = $input.first().json;
const msg = [
  'Workflow: SAOS Automation Audit v2',
  'Execution ID: ' + (err.execution?.id || 'unknown'),
  'Node: ' + (err.error?.node?.name || 'unknown'),
  'Time: ' + new Date().toISOString(),
  'Error: ' + (err.error?.message || 'unknown'),
].join('\\n');
return [{ json: { errorText: msg } }];
      `,
    },
  },
});

const notifyGreenOnError = node({
  type: 'n8n-nodes-base.emailSend',
  version: 2.1,
  config: {
    name: 'Notify Green on Error',
    position: [840, 900],
    parameters: {
      fromEmail: 'SyStack <support@systack.net>',
      toEmail: 'plowe@systack.net',
      subject: 'SAOS Automation Audit v2 Error',
      emailFormat: 'text',
      text: '={{ $json.errorText }}',
      options: { appendAttribution: false },
    },
  },
  credentials: { smtp: { id: 'U7QjoOL2sgu4KLs6', name: 'Support Systack SMTP account' } },
});

export default workflow('saos-automation-audit-v2', 'SAOS Automation Audit v2 (Real Scanner)')
  .add(auditWebhook)
  .to(callOrchestrator)
  .to(checkRateLimit
    .onTrue(rateLimitResponse)
    .onFalse(returnAuditResult.to(buildEmail).to(sendEmail))
  )
  .add(errorTrigger)
  .to(buildErrorEmail)
  .to(notifyGreenOnError);
