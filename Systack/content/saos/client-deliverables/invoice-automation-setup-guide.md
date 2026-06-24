# Invoice Automation — Setup Guide

**Client ID:** 1  
**Prepared by:** SOL (System Operations Liaison)  
**Date:** 2026-06-23  
**Status:** ✅ READY FOR CLIENT ONBOARDING

---

## What You Get

An end-to-end invoice automation pipeline that:

1. **Receives invoices** via email (PDF attachments) or API upload
2. **Extracts data** automatically — vendor, line items, totals, dates
3. **Normalizes** everything into a standard format (AR vs AP auto-detected)
4. **Stores** in a searchable database with dashboard
5. **Notifies** you when action is needed

**No more manual data entry.**

---

## System Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│   Email     │────▶│  IMAP Trigger│────▶│ PDF Parser  │────▶│  Normalize  │
│  (PDF att)  │     │   (n8n)      │     │  (Python)   │     │  (LRFO)     │
└─────────────┘     └──────────────┘     └─────────────┘     └──────┬──────┘
                                                                     │
┌─────────────┐     ┌──────────────┐     ┌─────────────┐            │
│  Web Upload │────▶│  API Endpoint│────▶│   Extract   │─────────────┘
│  (Drag PDF) │     │  (port 9001) │     │   + Parse   │
└─────────────┘     └──────────────┘     └─────────────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │   SQLite    │
                                       │  Database   │
                                       │(invoice_data│
                                       │    .db)     │
                                       └──────┬──────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │   Web       │
                                       │  Dashboard  │
                                       │ (port 8766) │
                                       └─────────────┘
```

---

## Live Endpoints

| Service | URL | Status |
|---------|-----|--------|
| **Extractor API** | `http://localhost:9001/extract` | ✅ RUNNING |
| **Dashboard API** | `http://localhost:8766/api/summary` | ✅ RUNNING |
| **Health Check** | `http://localhost:9001/health` | ✅ RUNNING |

### Test the API

```bash
# Upload a PDF invoice
curl -X POST http://localhost:9001/extract \
  -F "invoice=@/path/to/your/invoice.pdf"
```

---

## Invoice Formats Supported

The parser handles **7 invoice formats** out of the box:

| Format | Example | Detection |
|--------|---------|-----------|
| Standard | "Invoice #123 from VendorCo" | Keyword-based |
| FROM/BILL TO | "FROM: Acme \| BILL TO: You" | Header pattern |
| POS Receipt | "Qty \| Item \| Price" | Table pattern |
| Subscription | "Monthly Plan - $49" | Recurring keywords |
| Professional | "Services rendered..." | Services keywords |
| Contractor | "Hours: 40 @ $75/hr" | Time-based |
| International VAT | "VAT ID: EU123..." | Tax ID pattern |

---

## Database Schema

### Tables

| Table | Purpose |
|-------|---------|
| `invoices` | Raw extracted data |
| `invoice_items` | Line items per invoice |
| `invoices_normalized` | Canonical format (AR/AP) |
| `accounts_receivable` | Money owed TO you |
| `accounts_payable` | Money you OWE |
| `review_queue` | Items needing human check |

### Key Fields (Normalized)

```json
{
  "direction": "INBOUND" | "OUTBOUND",
  "entity_issuer": "Vendor Name",
  "entity_receiver": "Your Business",
  "financials": {
    "total_due": 1250.00,
    "currency": "USD"
  },
  "ledger_entry": {
    "debit_account": "expense",
    "credit_account": "accounts_payable"
  },
  "confidence": 0.92
}
```

---

## Dashboard Features

The web dashboard (`invoice-dashboard.html`) shows:

- **Total invoices** processed
- **AR vs AP** summary with net position
- **Payment status** breakdown (paid/unpaid/pending)
- **Top vendors** by volume
- **Recent activity** (7-day, 24-hour)
- **Review queue** count

---

## n8n Email Pipeline (Optional Add-On)

A pre-built n8n workflow (`Ny4kzzf1bN4NODGn`) can:

1. Poll IMAP inbox for new emails
2. Detect PDF attachments
3. Download and parse automatically
4. Log to database
5. Email you a summary

**Requires:** IMAP credentials, SMTP credentials, Postgres connection

---

## Setup Checklist for New Client

### Step 1: Core System (Required)
- [ ] Install Python 3.9+
- [ ] Install dependencies: `pip install pypdf2 pdfplumber`
- [ ] Copy parser files to client environment
- [ ] Run `python3 invoice_api.py` (starts on port 9001)
- [ ] Verify: `curl http://localhost:9001/health`

### Step 2: Database (Required)
- [ ] Run `python3 -c "from invoice_db import init_db; init_db()"`
- [ ] Verify tables created

### Step 3: Dashboard (Optional)
- [ ] Run `python3 invoice_dashboard_api.py` (port 8766)
- [ ] Open `invoice-dashboard.html` in browser
- [ ] Point dashboard to `http://localhost:8766/api/summary`

### Step 4: Email Automation (Optional)
- [ ] Import n8n workflow JSON
- [ ] Configure IMAP credential
- [ ] Configure SMTP credential
- [ ] Set polling interval (recommend: 5 minutes)
- [ ] Test with sample invoice email

### Step 5: Cloudflare Tunnel (For Remote Access)
- [ ] Install cloudflared
- [ ] Create tunnel: `cloudflared tunnel create invoice-system`
- [ ] Configure ingress rules
- [ ] Run tunnel

---

## Files Included

| File | Purpose | Size |
|------|---------|------|
| `invoice_parser_production.py` | PDF text extraction + format detection | ~400 lines |
| `invoice_normalizer.py` | Raw → canonical LRFO format | ~300 lines |
| `invoice_api.py` | HTTP API server (port 9001) | ~200 lines |
| `invoice_db.py` | SQLite database layer | ~150 lines |
| `invoice_dashboard_api.py` | Dashboard data API (port 8766) | ~300 lines |
| `invoice-dashboard.html` | Web UI (no server needed) | ~500 lines |

---

## Pricing (Systack Service)

| Tier | What's Included | Price |
|------|----------------|-------|
| **Basic** | Parser + API + SQLite | $500 setup |
| **Standard** | + Email automation + Dashboard | $500 setup + $50/mo |
| **Business** | + Postgres + Review queue + Cloud hosting | $1,500 setup + $100/mo |

---

## Next Steps

1. **Test with your invoices** — Upload 5-10 real PDFs to validate format detection
2. **Tune parser** — If format not detected, add custom rules
3. **Connect to accounting** — Export to QuickBooks/Xero via API
4. **Add users** — Multi-tenant dashboard with login

---

## Support

- **Dashboard:** `http://localhost:8766/api/summary`
- **API Docs:** See `invoice_api.py` header comments
- **Issues:** Check `review_queue` table for low-confidence extractions

---

*Generated by SOL | Systack Automation Systems*
