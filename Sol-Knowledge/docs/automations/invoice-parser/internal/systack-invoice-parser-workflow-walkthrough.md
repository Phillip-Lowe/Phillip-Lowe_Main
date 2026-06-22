# Systack — Invoice Parser
## Workflow Walkthrough

**Document ID:** `SY-IP-WF-001`  
**Version:** 1.0  
**Status:** Internal — Systack Only  
**Source System:** Systack Invoice Pipeline (Live since 2026-06-10)  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## Brand Reference

| Role | Color | Hex |
|------|-------|-----|
| Headers, CTAs | Navy | `#001a2d` |
| Navy Light | Navy Light | `#002845` |
| Secondary accents | Teal | `#007da9` |
| Primary buttons, links | Cyan | `#00a1db` |
| Gradients | Cyan Bright | `#00c5e0` |
| Backgrounds | Gray 50 | `#f8fafc` |
| Cards | Gray 100 | `#f1f5f9` |
| Borders | Gray 200 | `#e2e8f0` |
| Muted text | Gray 400 | `#94a3b8` |
| Body text | Gray 600 | `#475569` |
| Headings | Gray 800 | `#1e293b` |
| Success | Green | `#22c55e` |
| Error | Red | `#ef4444` |
| Accent highlights | Purple | `#8b5cf6` |

---

## Workflow: Invoice Email Pipeline

**Workflow ID:** `Ny4kzzf1bN4NODGn`  
**Name:** "Systack Private — Invoice Email Pipeline"

---

### Node 1 — IMAP Trigger

**Type:** IMAP Email Trigger

Monitors configured inbox for new emails.

**Critical settings:**

| Setting | Value |
|---------|-------|
| Format | `resolved` |
| Download attachments | `true` |

⚠️ Format MUST be `resolved` — "shallow" drops attachments.

---

### Node 2 — Filter: Has PDF Attachment?

**Type:** IF Node

**Condition:** `$json.mimeType === "application/pdf"`

⚠️ Check MIME type, NOT filename. Filename can be anything. MIME type identifies actual PDF content.

- **TRUE:** Continue to extraction
- **FALSE:** Skip (not an invoice)

---

### Node 3 — Extract Attachment

**Type:** Extract Attachment Node

**Binary key:** `attachment_0`

⚠️ MUST use `attachment_0` — NOT `attachment_`. Wrong key = file not found.

Saves PDF to disk for API processing.

---

### Node 4 — Call Invoice Parser API

**Type:** HTTP Request Node

**Endpoint:** `POST https://invoices.systack.net/extract`  
**Content-Type:** `multipart/form-data`  
**Body:** `file=@invoice.pdf`

**Response (JSON):**

```json
{
  "vendor": "AT&T",
  "invoice_number": "12345",
  "date": "2026-06-01",
  "line_items": [
    {"name": "Wireless Plan", "qty": 1, "price": 85.00, "total": 85.00}
  ],
  "subtotal": 100.00,
  "tax": 8.50,
  "total": 108.50,
  "email_subject": "Invoice Summary",
  "email_html": "<table>...</table>"
}
```

⚠️ Use Merge nodes before and after HTTP Request — HTTP Request drops all input data.

---

### Node 5 — Log to Postgres

**Type:** Postgres Node

Inserts extracted invoice data:

- Vendor name
- Invoice number
- Date
- Line items (as JSON)
- Subtotal, tax, total
- Timestamp

---

### Node 6 — Send Summary Email

**Type:** Email Send (SMTP)

Sends summary to owner:

**Subject:** `Invoice Processed: {{vendor}} — {{invoice_number}}`

**Body:**

```
New invoice processed:
Vendor: {{vendor}}
Invoice #: {{invoice_number}}
Date: {{date}}
Total: ${{total}}

Items:
{{line_items}}
```

---

## Node Chain Summary

```
IMAP Trigger (format=resolved)
  → IF: Has PDF Attachment? (mimeType check)
    → Extract Attachment (binary key: attachment_0)
      → HTTP Request: Call Parser API
        → Postgres: Log Invoice Data
          → Email: Send Summary to Owner
```

---

## Error Handling

| Error | Detection | Response |
|-------|-----------|----------|
| No PDF attachment | IF node (mimeType) | Skip email |
| Wrong binary key | Extract node fails | Check key is `attachment_0` |
| API down | HTTP timeout | Queue for retry |
| OCR failure | API returns partial data | Log for manual review |
| Postgres down | Insert fails | Alert, retry |

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
