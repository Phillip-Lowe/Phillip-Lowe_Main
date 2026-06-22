# Systack — Invoice Parser
## Internal Implementation Guide

**Document ID:** `SY-IP-IMPL-001`  
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

## 1. System Architecture

```
Email with PDF arrives
  → IMAP Trigger (format=resolved)
    → Extract PDF Attachment
      → Save PDF to disk
        → Call Invoice Parser API
          → API returns structured JSON
            → Log to Postgres
              → Send Summary Email
```

---

## 2. Core Components

### IMAP Email Trigger

| Setting | Value | Notes |
|---------|-------|-------|
| **Format** | `resolved` | ⚠️ NOT shallow — shallow drops attachments |
| **Download attachments** | `true` | Required |
| **Binary key** | `attachment_0` | ⚠️ NOT `attachment_` — wrong key = no file |
| **IF node check** | `mimeType` = `application/pdf` | ⚠️ Check MIME type, NOT filename |

---

### Invoice Parser API

- **URL:** `https://invoices.systack.net/extract`
- **Method:** POST (multipart/form-data)
- **Body:** `file=@invoice.pdf`
- **Response:** Structured JSON (vendor, items, totals)

---

### Database

- **Type:** PostgreSQL
- **Credential ID:** `iVuy7e5WTC05Hqwe`
- **Stores:** All extracted invoice data

---

### n8n Workflow

- **ID:** `Ny4kzzf1bN4NODGn`
- **Name:** "Systack Private — Invoice Email Pipeline"
- **Status:** ACTIVE

---

## 3. Setup Process (Replication)

### Step 1 — Configure IMAP

1. Create Gmail app password (or use existing)
2. Configure n8n IMAP credential:
   - **Format:** `resolved`
   - **Download attachments:** `true`
3. Set trigger to monitor specific inbox

---

### Step 2 — Deploy Parser API

- Python FastAPI application
- 9 vendor format handlers
- Tesseract OCR for scanned PDFs
- Deploy to `invoices.systack.net/extract`

---

### Step 3 — Configure n8n Workflow

Key nodes:

| # | Node | Critical Config |
|---|------|-----------------|
| 1 | IMAP Trigger | Format: resolved |
| 2 | IF (mimeType) | Check `application/pdf` |
| 3 | Extract Attachment | Binary key: `attachment_0` |
| 4 | HTTP Request | POST to parser API |
| 5 | Postgres Insert | Log extracted data |
| 6 | Email Send | Summary to owner |

---

### Step 4 — Set Up Postgres

- Create `invoices` table
- Configure n8n Postgres credential
- Test insert with sample extraction

---

### Step 5 — Configure Summary Email

- SMTP credential for sending
- Template: vendor, invoice #, date, items, totals
- Recipient: business owner or finance email

---

## 4. Critical Constraints

| Constraint | Detail | Consequence If Violated |
|------------|--------|------------------------|
| **IMAP format** | MUST be `resolved` | Attachments not downloaded |
| **Binary key** | MUST be `attachment_0` | File not found, API call fails |
| **MIME check** | Check `mimeType`, NOT filename | Non-PDF files processed, errors |
| **Gmail passwords** | May be revoked silently | IMAP stops working, no invoices processed |

---

## 5. Configuration Requirements

### Credentials

| Credential | ID | Purpose |
|------------|-----|---------|
| IMAP | `uZXvyt7Wd0RbQreY` | Read invoice emails |
| SMTP | `jL1iF7fhyhTe5tCp` | Send summaries |
| Postgres | `iVuy7e5WTC05Hqwe` | Store invoice data |

---

## 6. Testing Procedure

| Step | Action | Verify |
|------|--------|--------|
| 1 | Forward test invoice PDF | IMAP trigger fires |
| 2 | Check attachment extracted | Binary key correct |
| 3 | Check API response | Structured JSON returned |
| 4 | Check Postgres | Row inserted |
| 5 | Check summary email | Delivered to owner |

---

## 7. Maintenance

- Monitor IMAP credential status (Gmail may revoke)
- Check API response times (< 30s target)
- Review extraction success rate (> 95% target)
- Add new vendor formats as needed

---

## 8. Known Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| Gmail password revoked | IMAP stops | Regenerate app password |
| Multiple attachments | Only first processed | Forward one invoice at a time |
| Forwarded emails | Nested MIME structure | Send directly when possible |
| Password-protected PDF | Extraction fails | Remove password, resend |

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
