# Invoice Parser — System Status (2026-06-07)

## Components Built

### 1. Invoice Parser (`invoice_parser_production.py`)
- Extracts text from PDFs and plain text files
- Auto-detects 6 invoice formats:
  - Standard (Vendor:/Date:/Total:)
  - FROM:/BILL TO: (NovaTech style)
  - POS/Receipt (The Utopia Deli style)
  - Subscription/SaaS (NovaCloud style)
  - Professional Services (bullet points)
  - Contractor/Messy (unstructured)
  - International/VAT (Shenzhen Apex style)

### 2. Invoice Normalizer (`invoice_normalizer.py`)
- Converts raw parsed data → canonical LRFO schema
- Resolves direction (INBOUND=AR, OUTBOUND=AP)
- Generates ledger entries
- Calculates confidence scores
- Extracts entities, payment info, tax IDs

### 3. Invoice API (`invoice_api.py`)
- HTTP endpoint: `https://invoices.systack.net/extract`
- Accepts PDF uploads via multipart/form-data
- Returns normalized LRFO with raw data included
- CORS enabled for web clients

### 4. Database (`invoice_db.py`)
- SQLite with 5 tables:
  - `invoices` — raw extracted data
  - `invoice_items` — line items
  - `invoices_normalized` — canonical schema
  - `accounts_receivable` — AR entries
  - `accounts_payable` — AP entries
  - `review_queue` — unknown/flagged invoices

### 5. Dashboard (`invoice_dashboard.py`)
- CLI tool showing AR/AP summary
- Payment status breakdown
- Top unpaid invoices
- Net position calculation

## Dataset

### Synthetic Training Data (120 invoices)
- **Source:** ORACLE (M365 Copilot)
- **File:** `Invoice Parser Examples/synthetic-invoices-120.json`
- **AR:** 67 invoices ($190,850.25)
- **AP:** 53 invoices ($149,709.13)
- **Net Position:** +$41,141.12

### Real Examples (7 files)
- `INVOICE (Sample for Invoice Extractor).pdf` — FROM:/BILL TO: format
- `International Manufacturing Invoice` — VAT + currency
- `Messy Contractor Invoice` — OCR stress test
- `Professional Services Invoice` — minimal clean
- `Retail POS-Style Invoice` — receipt hybrid
- `Subscription SaaS Invoice` — recurring billing
- `real-invoice-test.pdf` — standard format

## Live Endpoints

| Service | URL | Status |
|---------|-----|--------|
| Web Demo | https://systack.net/services/invoice-extractor.html | ✅ Live |
| API | https://invoices.systack.net/extract | ✅ Live |
| Health | https://invoices.systack.net/health | ✅ Live |
| n8n Email | Workflow `IqNgw6kgIkWVCLp5` | ✅ Active |

## Next Steps

1. ✅ Parser handles 7 invoice formats
2. ✅ Normalizer creates LRFO with direction
3. ✅ API serves normalized data
4. ✅ Database has AR/AP tables
5. ✅ Dashboard shows summary
6. 🔄 Web dashboard (not CLI)
7. 🔄 n8n workflow integration
8. 🔄 Review queue UI
9. 🔄 Payment status updates
10. 🔄 Bank sync integration
