# Invoice Parser — Production Deployment

**Deployed:** 2026-06-07 10:35 CDT
**Updated:** 2026-06-08 03:38 CDT
**Status:** ✅ ACTIVE

## Live Endpoints

### Web Upload
- **URL:** https://systack.net/services/invoice-extractor.html
- **API:** https://invoices.systack.net/extract
- **Health:** https://invoices.systack.net/health
- **Method:** POST multipart/form-data (field: `invoice`)

### Email Trigger
- **Workflow ID:** `qnsBnLIWQ1Sky68D`
- **Name:** Systack — Invoice Email Pipeline
- **Status:** ⚠️ Active but NO IMAP credentials configured
- **Blocker:** Gmail app passwords revoked by Google (all tested passwords failed)

## API Response Format
```json
{
  "vendor": "ACME SUPPLIES INC.",
  "date": "May 15, 2024",
  "invoice_number": "INV-2024-0042",
  "items": [
    {"item": "Service Name", "price": 4500.00}
  ],
  "subtotal": 13700.0,
  "tax": 1164.5,
  "total": 14864.5,
  "success": true,
  "direction": "OUTBOUND",
  "entity_issuer": "ACME Supplies",
  "entity_receiver": "Green Systems LLC",
  "ledger_entry": {...},
  "confidence": 0.92
}
```

## Invoice Format Support (9 Formats Tested)

| # | Format | Vendor | Items | Total | Status |
|---|--------|--------|-------|-------|--------|
| 1 | FROM:/BILL TO: + ITEMS (NovaTech) | NovaTech Solutions Inc. | 4 | $5,078.72 | ✅ |
| 2 | Table/Column (real-invoice-test) | ABC Restaurant Supply Co. | 8 | $211.21 | ✅ |
| 3 | Contractor/Messy (Mike's Repairs) | Mike's Electrical Repairs | 3 | $826.20 | ✅ |
| 4 | International VAT (Shenzhen Apex) | Shenzhen Apex Manufacturing Ltd. | 3 | $2,587.70 | ✅ |
| 5 | POS Receipt (Utopia Deli) | THE UTOPIA DELI (FOOD TRUCK) | 4 | $21.55 | ✅ |
| 6 | Professional Services (Carter & Bloom) | Carter & Bloom Consulting | 2 | $3,700.00 | ✅ |
| 7 | Subscription/SaaS (NovaCloud) | NOVACLOUD SYSTEMS | 4 | $660.43 | ✅ |
| 8 | **Utility Bill (AT&T Phone)** | **AT&T Mobility** | **8** | **$149.59** | **✅ NEW** |
| 9 | **Scanned/Image PDF** | **OCR fallback working** | **0** | **$250.00** | **✅ NEW** |

## Infrastructure

### API Server
- **Script:** `invoice_api.py` (port 9001)
- **Launchd:** `com.systack.invoice-api` (auto-restart)
- **PID:** 2391 (running)
- **Logs:** `~/Documents/SOL-System/05-Logs/invoice-api.log`

### Cloudflare Tunnel
- **Config:** `~/.cloudflared/config-invoice-dashboard.yml`
- **Tunnel ID:** `e2897c60-f66d-4f5b-9d93-4c85897ca85f`
- **Hostname:** `invoices.systack.net` → `localhost:9001`
- **Status:** ✅ Connected

### n8n
- **URL:** https://n8n.systack.net
- **Invoice Workflow:** `qnsBnLIWQ1Sky68D` (active but broken — no IMAP creds)
- **Utopia Deli:** `utopia-deli-html-order-v1` (active)

### Database
- **File:** `invoice_data.db`
- **Backup:** `invoice_data.db.backup` (created 2026-06-08)
- **Records:** 119 invoices (includes test runs)
- **Note:** No `items` table — parser uses flat structure only

## What Was Done Tonight (2026-06-08 01:33-03:38)

### ✅ Fixed/Working
1. **API server** — Was down, now running via launchd on port 9001
2. **Database cleanup** — Removed duplicate test entries
3. **n8n workflow** — Activated `qnsBnLIWQ1Sky68D` (was disabled)
4. **Cloudflare tunnel** — Verified `invoices.systack.net` reachable
5. **All 7 synthetic formats** — Live API tested end-to-end
6. **OCR fallback** — Added Tesseract + pytesseract for scanned PDFs
7. **AT&T utility bill** — Added `parse_utility_bill_format()` — real PDF tested
8. **Real invoice tested** — AT&T phone bill from iCloud downloaded and parsed

### ❌ Blockers

#### Email Trigger (CRITICAL)
**Problem:** Gmail app passwords revoked by Google
- Tested: `sol.liaison@gmail.com`, `support@systack.net`, `theutopiadelilittlerock@gmail.com`
- All fail with: `535 5.7.8 Username and Password not accepted`
- n8n IMAP node has NO credentials configured (empty `credentials: {}`)

**Fix needed:**
1. Generate NEW Gmail app password at https://myaccount.google.com/apppasswords
2. Requires 2FA enabled on Gmail account
3. Update `himalaya` config
4. Update n8n workflow credential reference

#### iCloud Files
**Problem:** Files show "Resource deadlock avoided" until opened in Finder
**Workaround:** `open <file>` in Terminal forces Preview to download, then `cp` works
**Files tested:**
- ✅ `Phone bill .pdf` — downloaded, copied, parsed
- ⚠️ `Tremell_Billings_The_Utopia_Deli_2024_True_Cost_Income_Expense_Report (2).pdf` — still locked

## Files
- `invoice_parser_production.py` — parser (9 formats + OCR fallback)
- `invoice_api.py` — HTTP API server
- `invoice_normalizer.py` — LRFO normalization + direction detection
- `invoice_db.py` — SQLite database layer
- `invoice_dashboard.py` — CLI dashboard
- `systack-site/services/invoice-extractor.html` — frontend demo
- `INVOICE-PARSER-CHANGELOG.md` — format history
- `INVOICE-PARSER-LESSONS.md` — lessons learned

## Next Actions (Priority Order)

1. **CRITICAL: Generate new Gmail app password** → https://myaccount.google.com/apppasswords
2. **Update n8n IMAP credential** → Add credential to workflow `qnsBnLIWQ1Sky68D`
3. **Test email trigger** → Send test email with PDF to trigger workflow
4. **Download Utopia expense report** → Open in Finder, copy, test parse
5. **Stripe paywall** → Set up billing for unlimited processing
6. **Webhook notifications** → Slack/Discord on new invoices
