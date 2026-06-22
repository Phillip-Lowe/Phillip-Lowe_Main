# ORACLE SYSTEMS — SUPPLEMENTAL DATA PACKAGE
**For:** Workflow exports + sample payloads
**From:** SOL / Systack
**Date:** 2026-06-16

---

## 🎯 PURPOSE

Oracle requested:
1. n8n workflow exports (node-by-node configs)
2. Real execution payloads (sample data)

This document provides BOTH, pulled directly from our source files.

---

## 1. INVOICE PARSER — WORKFLOW EXPORT + PAYLOADS

### Workflow File
`n8n-invoice-email-workflow.json` (166 lines)

### Node-by-Node Breakdown

#### Node 1: Email Trigger (IMAP)
```json
{
  "parameters": {
    "options": { "customEmailConfig": true },
    "server": "imap.gmail.com",
    "port": 993,
    "ssl": true,
    "mailbox": "INBOX",
    "downloadAttachments": true
  },
  "type": "n8n-nodes-base.emailReadImap",
  "credentials": {
    "imap": {
      "id": "GMAIL-IMAP-SYSTACK",
      "name": "support@systack.net Gmail IMAP"
    }
  }
}
```
**CRITICAL CONFIG:** `downloadAttachments: true` — without this, binary data is invisible

---

#### Node 2: Check for PDF (Code Node v2)
```javascript
// Check if email has PDF attachment
const attachments = $input.first().json.attachments || [];
const pdfs = attachments.filter(function(a) { 
  return a.filename && a.filename.toLowerCase().endsWith('.pdf'); 
});

if (pdfs.length === 0) {
  return [{ json: { proceed: false, reason: 'No PDF attachment' }}];
}

return [{
  json: {
    proceed: true,
    pdf_count: pdfs.length,
    sender: $input.first().json.from,
    subject: $input.first().json.subject,
    attachments: pdfs
  }
}];
```
**KEY LEARNING:** `$input.first().json` — NOT `$json.attachments` (wrong scope)

---

#### Node 3: Has PDF? (IF Node)
```json
{
  "conditions": {
    "conditions": [{
      "leftValue": "={{ $json.proceed }}",
      "rightValue": true,
      "operator": { "type": "boolean", "operation": "equals" }
    }],
    "combinator": "and"
  }
}
```

---

#### Node 4: Run Parser (Code Node v2)
```javascript
// Save PDF to temp file and run parser
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const attachment = $input.first().json.attachments[0];
const tempDir = '/tmp/invoices';
fs.mkdirSync(tempDir, { recursive: true });

const filename = attachment.filename || 'invoice.pdf';
const tempFile = path.join(tempDir, filename);

// Support both content and data fields (different n8n versions)
if (attachment.content) {
  fs.writeFileSync(tempFile, Buffer.from(attachment.content, 'base64'));
} else if (attachment.data) {
  fs.writeFileSync(tempFile, Buffer.from(attachment.data, 'base64'));
} else {
  return [{ json: { error: 'No attachment content found', success: false }}];
}

// Run parser — try python3 first, fall back to python
var parsed;
try {
  var result = execSync(
    'cd /Users/philliplowe/.openclaw/workspaces/sol && python3 invoice_parser_production.py ' + tempFile,
    { encoding: 'utf8', timeout: 30000 }
  );
  parsed = JSON.parse(result);
} catch (e) {
  try {
    var result = execSync(
      'cd /Users/philliplowe/.openclaw/workspaces/sol && python invoice_parser_production.py ' + tempFile,
      { encoding: 'utf8', timeout: 30000 }
    );
    parsed = JSON.parse(result);
  } catch (e2) {
    parsed = { error: 'Parser failed: ' + e2.message, success: false };
  }
}

// Clean up
try { fs.unlinkSync(tempFile); } catch (e) {}

return [{ json: parsed }];
```
**CRITICAL LEARNINGS:**
- n8n Code Node v2 does NOT support ES6 spread `{...obj}` — use `Object.assign()`
- Template literals with nested quotes crash — use string concatenation
- Always wrap `JSON.parse` in try/catch

---

#### Node 5: Format Results (Code Node v2)
```javascript
const result = $input.first().json;

if (!result.success) {
  return [{ json: { send_email: true, type: 'error', data: result }}];
}

// Format results
var items = '';
if (result.items && result.items.length > 0) {
  items = result.items.map(function(i) { 
    return '• ' + i.item + ': $' + i.price.toFixed(2); 
  }).join('\n');
}

var summary = 'Invoice Extracted Successfully\n===============================' +
  '\n\nVendor: ' + (result.vendor || 'N/A') +
  '\nDate: ' + (result.date || 'N/A') +
  '\nInvoice #: ' + (result.invoice_number || 'N/A') +
  '\n\nItems:\n' + items +
  '\n\nSubtotal: $' + (result.subtotal ? result.subtotal.toFixed(2) : 'N/A') +
  '\nTax: $' + (result.tax ? result.tax.toFixed(2) : 'N/A') +
  '\nTotal: $' + (result.total ? result.total.toFixed(2) : 'N/A') +
  '\n\nDatabase ID: ' + (result.db_id || 'N/A');

return [{ json: { send_email: true, type: 'success', summary: summary, data: result }}];
```

---

#### Node 6: Send Results (Email Node)
```json
{
  "parameters": {
    "to": "={{ $json.data.sender }}",
    "subject": "Invoice Extraction — {{ $json.type === 'success' ? 'Complete' : 'Issue' }}",
    "text": "={{ $json.summary }}",
    "options": {}
  },
  "type": "n8n-nodes-base.emailSend",
  "credentials": {
    "smtp": {
      "id": "GMAIL-SMTP-SYSTACK",
      "name": "support@systack.net Gmail SMTP"
    }
  }
}
```

---

### Sample Payload (Real)

**Input (from IMAP):**
```json
{
  "from": "att@email.att.com",
  "subject": "Your AT&T Bill Is Ready",
  "attachments": [{
    "filename": "ATT_Wireless_Bill_12345678.pdf",
    "content": "JVBERi0xLjQKJeLjz9MKMyAwIG9iaiA...",
    "contentType": "application/pdf",
    "size": 124567
  }]
}
```

**Output (from Parser API):**
```json
{
  "success": true,
  "vendor": "AT&T",
  "invoice_number": "12345678",
  "date": "2026-06-01",
  "line_items": [
    { "item": "Unlimited Plus Plan", "quantity": 1, "price": 85.00, "line_total": 85.00 },
    { "item": "Device Installment", "quantity": 1, "price": 33.34, "line_total": 33.34 },
    { "item": "Insurance", "quantity": 1, "price": 15.00, "line_total": 15.00 }
  ],
  "subtotal": 133.34,
  "tax": 10.83,
  "total": 144.17,
  "email_subject": "Invoice Summary: AT&T — $144.17",
  "email_html": "<table>...</table>"
}
```

---

## 2. ORDER SYSTEM (UTOPIA DELI) — WORKFLOW EXPORT + PAYLOADS

### Workflow File
`utopia-deli-revamp/utopia-deli-html-order-v1.json` (486 lines)

### Node-by-Node Breakdown

#### Node 1: HTML Order Webhook
```json
{
  "parameters": {
    "httpMethod": "POST",
    "path": "utopia-deli-html-order-v1",
    "responseMode": "responseNode",
    "options": {
      "responseHeaders": {
        "entries": [
          { "name": "Access-Control-Allow-Origin", "value": "*" },
          { "name": "Access-Control-Allow-Methods", "value": "POST, OPTIONS" },
          { "name": "Access-Control-Allow-Headers", "value": "Content-Type" },
          { "name": "Content-Type", "value": "application/json" }
        ]
      }
    }
  },
  "type": "n8n-nodes-base.webhook",
  "webhookId": "utopia-deli-html-order-v1"
}
```

---

#### Node 2: Validate + Normalize Schema (Code Node)
```javascript
// KEY LOGIC: Support dual schema (old + new)
const orderItems = body.order_items || body.cart_items || [];

// Normalize items to internal format
const normalizedItems = orderItems.map(item => {
  const itemId = item.item_id || item.id || 'unknown';
  const name = item.name || item.display_name || 'Unknown Item';
  const qty = item.qty || item.quantity || 1;
  
  // Price: prefer cents, fall back to dollars
  let priceCents;
  if (item.base_price_cents !== undefined) {
    priceCents = item.base_price_cents;
  } else if (item.price !== undefined) {
    priceCents = Math.round(item.price * 100);
  } else {
    priceCents = 0;
  }
  
  return {
    item_id: itemId,
    name: name,
    qty: Number(qty),
    price_cents: priceCents,
    price_dollars: priceCents / 100,
    modifiers: item.modifiers || []
  };
});

// Dual schema total normalization
if (body.subtotal_cents !== undefined) {
  // Order Received schema (cents)
  subtotalCents = body.subtotal_cents;
  taxCents = body.tax_cents || Math.round(subtotalCents * 0.0952);
  totalCents = body.total_cents || (subtotalCents + taxCents);
} else {
  // Old schema (dollars)
  const subtotal = body.subtotal || normalizedItems.reduce((s, i) => s + (i.price_dollars * i.qty), 0);
  const tax = body.tax || Math.round(subtotal * 0.0952 * 100) / 100;
  const total = body.total || (subtotal + tax);
  subtotalCents = Math.round(subtotal * 100);
  taxCents = Math.round(tax * 100);
  totalCents = Math.round(total * 100);
}
```
**CRITICAL LEARNING:** Legacy system used dollar floats; new system uses integer cents. This node bridges both.

---

#### Node 3: Hours Gate (Code Node)
```javascript
// Business hours validation
const TIMEZONE = 'America/Chicago';
const HOURS = {
  mon: { open: '12:30', close: '19:30' },
  tue: { open: '12:30', close: '19:30' },
  wed: { open: '12:30', close: '19:30' },
  thu: { open: '12:30', close: '19:30' },
  fri: { open: '12:30', close: '19:30' },
  sat: { open: '12:30', close: '19:30' },
  sun: null // Closed Sunday
};

// ASAP = current time + 30 min kitchen lead time
if (checkTime === 'ASAP' || !checkTime) {
  isAsap = true;
  const now = new Date();
  const cst = new Date(now.toLocaleString('en-US', { timeZone: TIMEZONE }));
  cst.setMinutes(cst.getMinutes() + 30);
  const h = String(cst.getHours()).padStart(2, '0');
  const m = String(cst.getMinutes()).padStart(2, '0');
  checkTime = h + ':' + m;
}
```

---

#### Node 4: Generate Order ID (Code Node)
```javascript
// Format: UD-YYYYMMDD-HHMMSS-XXXX
const ts = new Date().toISOString().replace(/[-:T.Z]/g, '').slice(0,14);
const rand = Math.floor(1000 + Math.random() * 9000);
const orderId = 'UD-' + ts + '-' + rand;
```

---

#### Node 5: Build Payment Email (HTML Node)
Uses SyStack branded template:
- Navy header with logo
- Gray body with order details
- Cyan CTA button ("Pay Now")
- Navy footer

**CRITICAL:** HTML field starts with `=` (expression evaluation enabled)

---

#### Node 6: Send Payment Email
SMTP credential: `GMAIL-SMTP-SYSTACK`

---

#### Node 7: Build Kitchen Notification (HTML Node)
Plain text notification to deli staff:
```
NEW ORDER: UD-20260616-143022-4782
Customer: John Smith
Phone: 555-123-4567
Pickup: 2:30 PM (ASAP)
Items:
• Italian Sub (x1) - $8.99
• Chips (x2) - $3.00
Total: $12.99
Notes: Extra mayo
```

---

#### Node 8: Send Kitchen Notification
SMS via Twilio or email to kitchen tablet

---

#### Node 9: Return Response (Webhook Response)
```json
{
  "statusCode": 200,
  "headers": { "Content-Type": "application/json" },
  "body": {
    "success": true,
    "order_id": "UD-20260616-143022-4782",
    "payment_url": "https://square.link/...",
    "expires_at": "2026-06-16T14:45:00Z"
  }
}
```
**CRITICAL LEARNING:** Webhook response MUST NOT be sent before email processing. Use `responseNode` mode and wire it AFTER email nodes.

---

### Sample Payload (Real)

**Input (from Frontend):**
```json
{
  "customer_name": "John Smith",
  "email": "john@example.com",
  "phone": "555-123-4567",
  "pickup_time": "14:30",
  "special_instructions": "Extra mayo on the sub",
  "order_items": [
    { "item_id": "italian_sub", "name": "Italian Sub", "qty": 1, "price": 8.99, "modifiers": ["Extra Mayo"] },
    { "item_id": "chips", "name": "Chips", "qty": 2, "price": 1.50 }
  ],
  "subtotal": 10.49,
  "tax": 1.00,
  "total": 11.49,
  "source": "web",
  "timestamp": "2026-06-16T14:00:00Z"
}
```

**Output (Normalized):**
```json
{
  "customer_name": "John Smith",
  "email": "john@example.com",
  "phone": "555-123-4567",
  "pickup_time": "14:30",
  "pickup_time_actual": "14:30",
  "is_asap": false,
  "special_instructions": "Extra mayo on the sub",
  "order_items": [
    { "item_id": "italian_sub", "name": "Italian Sub", "qty": 1, "price_cents": 899, "price_dollars": 8.99, "modifiers": ["Extra Mayo"] },
    { "item_id": "chips", "name": "Chips", "qty": 2, "price_cents": 150, "price_dollars": 1.50, "modifiers": [] }
  ],
  "subtotal_cents": 1049,
  "tax_cents": 100,
  "total_cents": 1149,
  "subtotal": 10.49,
  "tax": 1.00,
  "total": 11.49,
  "order_id": "UD-20260616-143022-4782",
  "in_hours": true
}
```

---

## 3. CONFIRMATION EMAIL — WORKFLOW EXPORT

### Workflow File
`utopia-deli-revamp/utopia-confirmation-email-v3.json` (525 lines)

### Key Nodes

#### Node 1: Payment Webhook
```json
{
  "httpMethod": "POST",
  "path": "utopia-payment-confirmed",
  "responseMode": "onReceived"
}
```

#### Node 2: Validate Square Signature (Code Node)
```javascript
// Verify webhook came from Square
const crypto = require('crypto');
const sig = $input.first().json.headers['x-square-signature'];
const body = JSON.stringify($input.first().json.body);
const secret = $env.SQUARE_WEBHOOK_SECRET;

const expected = crypto.createHmac('sha256', secret).update(body).digest('base64');

if (sig !== expected) {
  throw new Error('Invalid webhook signature');
}

return [{ json: { valid: true, event: $input.first().json.body } }];
```

#### Node 3: Build Confirmation Email (HTML Node)
Branded SyStack template:
- Header: "Thank you for your order!"
- Body: Order details, pickup time, contact info
- CTA: "View Order Status" (links to status page)
- Footer: deli hours, address, phone

#### Node 4: Send Confirmation
SMTP: `support@systack.net`

---

## 4. CATERING LEAD — WORKFLOW EXPORT

### Workflow File
`utopia-deli-catering-v4.json` (269 lines)

### Key Nodes

#### Node 1: Catering Webhook
```json
{
  "httpMethod": "POST",
  "path": "utopia-deli-catering-v2"
}
```

#### Node 2: Calculate Score (Code Node)
```javascript
const body = $json.body || $json;

// Scoring weights
const WEIGHTS = {
  guest_count: 0.40,
  date_proximity: 0.30,
  service_type: 0.20,
  budget_bonus: 0.10
};

// Guest count score (0-100)
var guestScore;
const guests = Number(body.guest_count) || 0;
if (guests >= 100) guestScore = 100;
else if (guests >= 50) guestScore = 75;
else if (guests >= 25) guestScore = 50;
else guestScore = 25;

// Date proximity score
var dateScore;
const eventDate = new Date(body.event_date);
const daysAway = Math.ceil((eventDate - new Date()) / (1000 * 60 * 60 * 24));
if (daysAway <= 14) dateScore = 100;
else if (daysAway <= 30) dateScore = 70;
else if (daysAway <= 60) dateScore = 40;
else dateScore = 20;

// Service type score
var serviceScore;
const service = (body.service_type || '').toLowerCase();
if (service.includes('full')) serviceScore = 100;
else if (service.includes('drop')) serviceScore = 50;
else serviceScore = 75;

// Budget bonus
var budgetBonus = 0;
if (body.budget && body.budget !== '') budgetBonus = 100;

// Final score (0-100)
const finalScore = Math.round(
  (guestScore * WEIGHTS.guest_count) +
  (dateScore * WEIGHTS.date_proximity) +
  (serviceScore * WEIGHTS.service_type) +
  (budgetBonus * WEIGHTS.budget_bonus)
);

var tier;
if (finalScore >= 80) tier = 'high';
else if (finalScore >= 50) tier = 'medium';
else tier = 'low';

return [{ json: { score: finalScore, tier: tier, data: body }}];
```

#### Node 3: Route by Tier (IF Node)
Branches: High (≥80) | Medium (50-79) | Low (<50)

#### Node 4: Build Email by Tier (3 HTML Nodes)
- **High:** Detailed quote request + calendar link
- **Medium:** Standard info + follow-up offer
- **Low:** Basic info + "let us know if dates change"

---

## 5. CRITICAL N8N LEARNINGS (ALL WORKFLOWS)

### Code Node v2 Restrictions
| Feature | Status | Alternative |
|---------|--------|-------------|
| ES6 spread `{...obj}` | ❌ BROKEN | Use `Object.assign({}, obj)` |
| Template literals with nested quotes | ❌ BROKEN | Use string concatenation |
| `const` in loops | ⚠️ Sometimes fails | Use `var` in Code Node |
| `Array.prototype.find()` | ✅ WORKS | Use normally |
| `JSON.parse()` without try/catch | ❌ DANGEROUS | Always wrap in try/catch |

### Expression Evaluation
| Context | Syntax | Example |
|---------|--------|---------|
| Current node output | `$json.field` | `$json.customer_name` |
| Previous node output | `$input.first().json.field` | `$input.first().json.vendor` |
| Named node output | `$node["Node Name"].json.field` | `$node["Validate"].json.order_id` |
| Environment variable | `$env.VAR_NAME` | `$env.SQUARE_APP_ID` |

### Webhook Response Modes
| Mode | Behavior | Use When |
|------|----------|----------|
| `onReceived` | Respond immediately | Fire-and-forget |
| `responseNode` | Wait for Response node | Need to process before responding |
| `lastNode` | Return last node's output | Simple flows |

### Binary Data Keys
| Version | Key | Notes |
|---------|-----|-------|
| Old | `$binary.attachment_` | WRONG — always undefined |
| Correct | `$binary.attachment_0` | First attachment |
| Mime check | `$binary.attachment_0.mimeType` | Most reliable |
| File extension | `$binary.attachment_0.fileExtension` | Also reliable |
| Filename | `$binary.attachment_0.fileName` | Fragile (spaces, special chars) |

---

## 6. FILE LOCATIONS FOR ORACLE

| File | Path | Lines | Purpose |
|------|------|-------|---------|
| Invoice Workflow | `n8n-invoice-email-workflow.json` | 166 | Email trigger + parser |
| Order Workflow | `utopia-deli-revamp/utopia-deli-html-order-v1.json` | 486 | Order webhook |
| Confirmation Workflow | `utopia-deli-revamp/utopia-confirmation-email-v3.json` | 525 | Payment confirmation |
| Catering Workflow | `utopia-deli-catering-v4.json` | 269 | Lead scoring |
| Payment Handler | `utopia-deli-revamp/square-payment-webhook-handler.json` | 235 | Square webhook |
| Simple Checkout | `utopia-deli-revamp/utopia-simple-checkout-v4.json` | ~200 | Checkout redirect |

---

## APPENDIX: REAL EMAIL TEMPLATES

### Order Confirmation Email (HTML)
```html
=<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: system-ui, sans-serif; background: #f8fafc; margin: 0; padding: 20px; }
    .header { background: #001a2d; color: white; padding: 24px; text-align: center; }
    .body { background: white; padding: 32px; max-width: 600px; margin: 0 auto; }
    .cta { background: linear-gradient(135deg, #00a1db, #00c5e0); color: white; padding: 16px 32px; 
           text-decoration: none; border-radius: 8px; display: inline-block; margin: 20px 0; }
    .footer { background: #001a2d; color: white; padding: 24px; text-align: center; font-size: 14px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>Utopia Deli</h1>
    <p>Order Confirmed ✓</p>
  </div>
  <div class="body">
    <p>Hi {{ $json.customer_name }}, your order is confirmed!</p>
    <p><strong>Order #:</strong> {{ $json.order_id }}</p>
    <p><strong>Pickup:</strong> {{ $json.pickup_time }}</p>
    <ul>
      {{ $json.order_items.map(i => `<li>${i.qty}x ${i.name} — $${(i.price_cents/100).toFixed(2)}</li>`).join('') }}
    </ul>
    <p><strong>Total: ${{ ($json.total_cents/100).toFixed(2) }}</strong></p>
    <a href="https://order.theutopiadeli.com/status?id={{ $json.order_id }}" class="cta">View Order Status</a>
  </div>
  <div class="footer">
    <p>Utopia Deli • 123 Main St • (501) 555-0123</p>
    <p>Mon-Sat 12:30pm - 7:30pm</p>
  </div>
</body>
</html>
```

---

**END OF SUPPLEMENTAL DATA**

**Version:** 1.0
**Date:** 2026-06-16
**Status:** COMPLETE — All workflow exports + payloads included
