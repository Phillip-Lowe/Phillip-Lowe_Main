import { workflow, trigger, node, ifElse } from '@n8n/workflow-sdk';

// Webhook: receives AI Visibility Audit form submissions from systack.net/geo/audit.html
const geoAuditWebhook = trigger({
  type: 'n8n-nodes-base.webhook',
  version: 2.1,
  config: {
    name: 'GEO Audit Webhook',
    position: [240, 300],
    parameters: {
      httpMethod: 'POST',
      path: 'GEO_AUDIT_V1',
      authentication: 'none',
      responseMode: 'responseNode'
    }
  },
  output: [{
    headers: {},
    params: {},
    query: {},
    body: {
      businessName: 'Smith Law Firm',
      website: 'https://www.smithlaw.com',
      city: 'Little Rock',
      industry: 'Law Firm',
      email: 'prospect@example.com',
      source: 'systack.net/geo/audit.html',
      submittedAt: '2026-07-24T12:00:00.000Z'
    }
  }]
});

// Respond immediately so the browser can show the preview result
const respondToWebhook = node({
  type: 'n8n-nodes-base.respondToWebhook',
  version: 1.5,
  config: {
    name: 'Acknowledge Submission',
    position: [540, 300],
    parameters: {
      respondWith: 'json',
      responseBody: {
        success: true,
        message: 'Audit request received. Check your email within 24 hours for the full report.'
      },
      options: { responseCode: 200 }
    }
  },
  output: [{ success: true }]
});

// Normalize lead fields and set defaults
const normalizeLead = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Normalize Lead',
    position: [840, 300],
    parameters: {
      mode: 'manual',
      assignments: {
        assignments: [
          { id: 'a1', name: 'businessName', value: "={{ $('GEO Audit Webhook').item.json.body.businessName || $('GEO Audit Webhook').item.json.body.business_name || '' }}", type: 'string' },
          { id: 'a2', name: 'website', value: "={{ $('GEO Audit Webhook').item.json.body.website || '' }}", type: 'string' },
          { id: 'a3', name: 'city', value: "={{ $('GEO Audit Webhook').item.json.body.city || '' }}", type: 'string' },
          { id: 'a4', name: 'industry', value: "={{ $('GEO Audit Webhook').item.json.body.industry || '' }}", type: 'string' },
          { id: 'a5', name: 'email', value: "={{ $('GEO Audit Webhook').item.json.body.email || '' }}", type: 'string' },
          { id: 'a6', name: 'source', value: "={{ $('GEO Audit Webhook').item.json.body.source || 'systack.net/geo/audit.html' }}", type: 'string' },
          { id: 'a7', name: 'submittedAt', value: "={{ $('GEO Audit Webhook').item.json.body.submittedAt || $now.toISO() }}", type: 'string' },
          { id: 'a8', name: 'leadSummary', value: "={{ 'New AI Visibility Audit request from ' + ($('GEO Audit Webhook').item.json.body.businessName || 'Unknown') + ' (' + ($('GEO Audit Webhook').item.json.body.industry || 'Unknown') + ') in ' + ($('GEO Audit Webhook').item.json.body.city || 'Unknown') }}", type: 'string' }
        ]
      }
    }
  },
  output: [{
    businessName: 'Smith Law Firm',
    website: 'https://www.smithlaw.com',
    city: 'Little Rock',
    industry: 'Law Firm',
    email: 'prospect@example.com',
    source: 'systack.net/geo/audit.html',
    submittedAt: '2026-07-24T12:00:00.000Z',
    leadSummary: 'New AI Visibility Audit request from Smith Law Firm (Law Firm) in Little Rock'
  }]
});

// Validate required fields
const validateLead = ifElse({
  version: 2.3,
  config: {
    name: 'Valid Lead?',
    position: [1140, 300],
    parameters: {
      conditions: {
        combinator: 'and',
        options: { caseSensitive: true, leftValue: '', typeValidation: 'strict', version: 1 },
        conditions: [
          { id: 'v1', leftValue: '={{ $json.businessName }}', rightValue: '', operator: { type: 'string', operation: 'isNotEmpty' } },
          { id: 'v2', leftValue: '={{ $json.email }}', rightValue: '', operator: { type: 'string', operation: 'isNotEmpty' } }
        ]
      }
    }
  }
});

// Email Green / SyStack owner about new lead
const notifyOwner = node({
  type: 'n8n-nodes-base.emailSend',
  version: 2.1,
  config: {
    name: 'Email Owner',
    position: [1380, 120],
    credentials: { smtp: 'NEW_SMTP' },
    parameters: {
      resource: 'email',
      operation: 'send',
      fromEmail: 'support@systack.net',
      toEmail: 'plowe@systack.net',
      subject: '🎯 New AI Visibility Audit Lead',
      emailFormat: 'html',
      html: "={{ '<h2>New AI Visibility Audit Request</h2>' + '<p><strong>Business:</strong> ' + $json.businessName + '</p>' + '<p><strong>Website:</strong> ' + $json.website + '</p>' + '<p><strong>City:</strong> ' + $json.city + '</p>' + '<p><strong>Industry:</strong> ' + $json.industry + '</p>' + '<p><strong>Email:</strong> ' + $json.email + '</p>' + '<p><strong>Source:</strong> ' + $json.source + '</p>' + '<p><strong>Submitted:</strong> ' + $json.submittedAt + '</p>' + '<hr><p>Next step: generate and send the AI Visibility Audit PDF.</p>' }}",
      options: { appendAttribution: false }
    }
  },
  output: [{ sent: true }]
});

// Send auto-reply to prospect
const autoReplyProspect = node({
  type: 'n8n-nodes-base.emailSend',
  version: 2.1,
  config: {
    name: 'Auto-Reply Prospect',
    position: [1620, 120],
    credentials: { smtp: 'NEW_SMTP' },
    parameters: {
      resource: 'email',
      operation: 'send',
      fromEmail: 'support@systack.net',
      toEmail: '={{ $json.email }}',
      subject: 'Your AI Visibility Audit is in progress — SyStack',
      emailFormat: 'html',
      html: "={{ '<div style=\"font-family:Arial,sans-serif;max-width:600px;margin:0 auto;\"\u003e' + '<div style=\"background:#001a2d;color:#fff;padding:24px;text-align:center;border-radius:8px 8px 0 0;\"\u003e' + '<h2 style=\"margin:0;\"\u003eAI Visibility Audit</h2>' + '</div>' + '<div style=\"padding:24px;border:1px solid #e2e8f0;border-top:none;border-radius:0 0 8px 8px;\"\u003e' + '<p>Hi there,</p>' + '<p>Thanks for requesting an AI Visibility Audit for <strong>' + $json.businessName + '</strong>.</p>' + '<p>We are analyzing how ChatGPT, Copilot, Gemini, Perplexity, and Google AI find and recommend businesses like yours in <strong>' + $json.city + '</strong>.</p>' + '<p>You will receive your full audit report via email within <strong>24 hours</strong>.</p>' + '<p>In the meantime, you can learn more about our AI Visibility services at <a href=\"https://systack.net/geo/\"\u003esystack.net/geo</a>.</p>' + '<p>— SyStack AI Visibility Team</p>' + '</div>' + '</div>' }}",
      options: { appendAttribution: false }
    }
  },
  output: [{ sent: true }]
});

// Log invalid submissions
const logInvalid = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Log Invalid Lead',
    position: [1380, 480],
    parameters: { mode: 'runOnceForAllItems' }
  },
  output: [{ invalid: true, reason: 'Missing businessName or email' }]
});

// Export workflow
export default workflow('geo-audit-v1', 'GEO Audit Lead Capture v1')
  .add(geoAuditWebhook)
  .to(respondToWebhook)
  .to(normalizeLead)
  .to(validateLead
    .onTrue(notifyOwner.to(autoReplyProspect))
    .onFalse(logInvalid)
  );
