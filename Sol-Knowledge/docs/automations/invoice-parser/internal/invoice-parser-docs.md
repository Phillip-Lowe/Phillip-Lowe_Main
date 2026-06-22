# Invoice Parser — Documentation

**Automation ID:** `invoice-parser`  
**Version:** 2.0  
**Status:** `live` — needs full documentation  
**Built:** 2026-06-08 (parser API), 2026-06-10 (email pipeline)  
**Last Updated:** 2026-06-11  
**Owner:** Systack (internal + client service)  
**Builder:** SOL

---

## 1. Executive Summary

### What It Does
Automated invoice processing: forward any PDF invoice to our system, extract structured data (vendor, line items, totals, tax), log to database, send summary email. Handles 9+ vendor formats + OCR for scanned PDFs.

### Business Value
| Metric | Before | After |
|--------|--------|-------|
| Processing time | 5-10 min/manual | < 60 seconds |
| Data entry errors | Common | Eliminated |
| Format support | 1-2 vendors | 9+ vendors + OCR |
| Data security | Cloud processing | 100% local |

### URLs
- API: https://invoices.systack.net/extract
- Demo: https://systack.net/services/invoice-extractor.html

---

## 2. System Architecture

### Flow Diagram
```
Email with PDF arrives
    ↓
[IMAP Trigger (format=resolved)]
    ↓
[Extract PDF Attachment]
    ↓
[Save PDF to disk]
    ↓
[Call Invoice Parser API]
    ↓
[API returns structured JSON]
    ├── Vendor, Invoice #, Date
    ├── Line items (name, qty, price, total)
    ├── Subtotal, Tax, Total
    └── Monthly running totals
    ↓
[Log to Postgres]
    ↓
[Send Summary Email]
    ↓
[Owner sees: "New invoice from {vendor}: ${total}"]
```

### Components
| Component | Technology | Purpose |
|-----------|------------|---------|
| Email Trigger | n8n IMAP | Captures invoice emails |
| PDF Extractor | Python + pytesseract | OCR if needed |
| Parser API | Python FastAPI | Structured extraction |
| Database | Postgres | Invoice storage |
| Notifier | n8n Email | Summary to owner |

---

## 3. Technical Specifications

### IMAP Configuration
| Setting | Value |
|---------|-------|
| Format | `resolved` (NOT shallow) |
| Download attachments | `true` |
| Binary key | `attachment_0` (NOT `attachment_`) |
| IF node check | `mimeType` = `application/pdf` |

### API Endpoint
```
POST https://invoices.systack.net/extract
Content-Type: multipart/form-data
Body: file=@invoice.pdf

Response:
{
  "vendor": "AT&T",
  "invoice_number": "12345",
  "date": "2026-06-01",
  "line_items": [...],
  "subtotal": 100.00,
  "tax": 8.50,
  "total": 108.50,
  "email_subject": "Invoice Summary",
  "email_html": "<table>...</table>"
}
```

### n8n Workflow
- **ID:** `Ny4kzzf1bN4NODGn`
- **Name:** "Systack Private — Invoice Email Pipeline"
- **Status:** ACTIVE in database

---

## 4. Configuration

### Credentials
| Credential | ID | Purpose |
|------------|-----|---------|
| IMAP | `uZXvyt7Wd0RbQreY` | Read invoice emails |
| SMTP | `jL1iF7fhyhTe5tCp` | Send summaries |
| Postgres | `iVuy7e5WTC05Hqwe` | Store data |

### Email Subject Parsing
- Trigger on: invoices@, bills@, or specific vendor addresses
- Ignore: newsletters, ads, personal email

---

## 5. Operational Runbook

### Daily Checks
- [ ] Invoices processed in last 24h
- [ ] API response time < 30s
- [ ] No failed extractions
- [ ] Summary emails sent

### Monitoring
| Metric | Expected | Alert If |
|--------|----------|----------|
| Extraction success rate | > 95% | < 90% |
| API response time | < 30s | > 60s |
| OCR fallback rate | < 20% | > 40% |
| Email delivery | > 98% | < 95% |

### Failure Scenarios
| Scenario | Response |
|----------|----------|
| IMAP credential expired | Check Gmail app password (may be revoked by Google) |
| PDF unreadable | Log for manual review, notify owner |
| API down | Queue for retry, alert Systack |

---

## 6. Build Log

### Phase 1: Parser API (2026-06-08)
- Built Python API with 9 format handlers
- Added Tesseract OCR for scanned PDFs
- Tested with real AT&T phone bill

### Phase 2: Email Pipeline (2026-06-10)
- Fixed IMAP format to `resolved`
- Fixed binary key to `attachment_0`
- Fixed IF node to check mimeType
- Built summary email template
- Renamed from deli-specific to generic pipeline

---

## 7. Known Issues

1. **Gmail app passwords revoked silently** — check credential status regularly
2. **Multiple attachments** — currently assumes single attachment
3. **Forwarded emails** — may have nested MIME structure

---

## Appendix: Quick Reference

```
START:     Verify IMAP credential + API health
STOP:      Disable IMAP trigger in n8n
CHECK:     Last invoice processed timestamp
FIX:       If no invoices → check IMAP credential status
ESCALATE:  If API returning errors → check parser logs
```

---

**Last Updated:** 2026-06-11  
**Status:** Live — operational
