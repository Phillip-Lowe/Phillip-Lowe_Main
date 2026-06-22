# Systack — Invoice Parser
## Client Service Manual

**Document ID:** `SY-IP-CSM-001`  
**Version:** 1.0  
**Status:** Live  
**Prepared for:** Systack Clients  
**Prepared by:** Systack (systack.net)  
**Date:** 2026-06-16  
**Support:** support@systack.net | (501) 274-6231

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

## 1. Overview

The Systack Invoice Parser automatically extracts structured data from PDF invoices. Forward any invoice PDF by email, and within seconds you receive a summary with vendor name, line items, totals, and tax — all logged to your database.

No manual data entry. No cloud processing. Everything runs locally.

---

## 2. How the System Works

### Step 1 — Forward an Invoice

Forward any PDF invoice to your configured invoice email address. The system monitors this inbox for new messages with PDF attachments.

---

### Step 2 — Automatic Extraction

The system:

- Detects the PDF attachment
- Identifies the vendor from the document content
- Extracts: vendor name, invoice number, date, line items, subtotal, tax, total
- Falls back to OCR for scanned or image-based PDFs

---

### Step 3 — Structured Data

The extracted data is returned as structured JSON:

```json
{
  "vendor": "AT&T",
  "invoice_number": "12345",
  "date": "2026-06-01",
  "line_items": [
    {"name": "Wireless Plan", "qty": 1, "price": 85.00, "total": 85.00},
    {"name": "Device Payment", "qty": 1, "price": 15.00, "total": 15.00}
  ],
  "subtotal": 100.00,
  "tax": 8.50,
  "total": 108.50
}
```

---

### Step 4 — Database Logging

All extracted invoices are stored in a PostgreSQL database for:

- Historical reference
- Monthly spending reports
- Vendor cost tracking
- Tax preparation

---

### Step 5 — Summary Notification

You receive an email summary:

```
New invoice processed:
Vendor: AT&T
Invoice #: 12345
Date: 2026-06-01
Total: $108.50
```

---

## 3. What You See

### Summary Email

Example:

```
INVOICE PROCESSED
Vendor: AT&T
Invoice #: 12345
Date: June 1, 2026
Items:
• Wireless Plan — $85.00
• Device Payment — $15.00
Subtotal: $100.00
Tax: $8.50
Total: $108.50
```

---

### API Demo Page

**URL:** https://systack.net/services/invoice-extractor.html

Upload any PDF invoice to see extraction results in real time.

---

## 4. Supported Vendors

The system recognizes 9+ vendor formats out of the box:

- AT&T
- Verizon
- Utility providers
- Wholesale suppliers
- Service providers
- And more

For unrecognized formats, the system uses OCR to extract what it can. New vendor formats can be added on request.

---

## 5. Key Benefits

- **Zero manual data entry** — forward and forget
- **100% local processing** — no cloud, no data sharing
- **9+ vendor formats** — covers most common invoices
- **OCR fallback** — handles scanned and image-based PDFs
- **Database logging** — complete invoice history
- **Under 60 seconds** — from forward to summary

---

## 6. Common Questions

### What if the invoice format isn't recognized?

The system falls back to OCR (optical character recognition) to extract whatever data it can find. Results may be less precise than format-matched extraction.

---

### Can I add support for my vendors?

Yes — contact Systack with sample invoices. New vendor formats can be added to the parser.

---

### Where is my invoice data stored?

In a local PostgreSQL database. Data never leaves your infrastructure.

---

### What if the PDF is password-protected?

Password-protected PDFs cannot be processed. Remove the password and forward again.

---

### What if I forward multiple invoices at once?

The system processes the first PDF attachment. Forward invoices one at a time for best results.

---

## 7. Troubleshooting

### No summary email received

- Check the email was forwarded to the correct address
- Verify the email had a PDF attachment
- Check spam folder for summary emails
- Contact Systack if persistent

---

### Invoice data looks wrong

- The vendor format may not be fully supported
- Try the API demo page to see raw extraction
- Report issues with sample invoice to Systack

---

### "No attachment found" error

- Ensure the PDF is attached directly (not linked)
- Check the attachment is a .pdf file
- Forwarded emails with nested attachments may need to be sent directly

---

## 8. Support

| Channel | Detail |
|---------|--------|
| **Email** | support@systack.net |
| **Phone** | (501) 274-6231 |
| **Demo** | https://systack.net/services/invoice-extractor.html |

---

## 9. Summary

The Systack Invoice Parser provides:

- Automatic PDF invoice data extraction
- 9+ vendor format support with OCR fallback
- Local database logging for complete history
- Email summary notifications
- Zero manual data entry

Forward an invoice. Get structured data. Done.

---

*Document prepared by Systack.*  
*© 2026 Systack. All rights reserved.*
