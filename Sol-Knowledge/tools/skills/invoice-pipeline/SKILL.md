---
name: invoice-pipeline
description: "Build end-to-end invoice ingestion systems: email trigger → PDF extraction → data normalization → database storage → dashboard API. Supports both Postgres and SQLite backends."
---

# Invoice Pipeline

Build complete invoice ingestion systems from scratch: IMAP email monitoring → PDF/OCR extraction → structured data storage → REST API → HTML dashboard.

## When to Use
- Client needs to ingest supplier/vendor invoices automatically
- Business receives bills via email attachment (PDF, image)
- Need searchable invoice database with spend analytics
- Building bookkeeping automation for small business

## Pipeline

1. **Email Trigger** — n8n IMAP node watching inbox (format="resolved", downloadAttachments=true)
2. **PDF Extract** — Parse PDF with pdfplumber, fallback to OCR (Tesseract/pytesseract)
3. **Normalize** — Standardize vendor names, dates, currencies, line items
4. **Store** — Insert into database (Postgres preferred, SQLite fallback)
5. **API** — FastAPI/HTTP server for dashboard queries
6. **Dashboard** — HTML frontend showing invoices, totals, vendor breakdown
7. **Notify** — Email summary of new invoices with month-to-date totals

## Requirements

| Component | Tool |
|---|---|
| PDF text | `pdfplumber` |
| PDF OCR | `pytesseract` + `Pillow` |
| Database | `psycopg2` (Postgres) or `sqlite3` |
| API server | Python `HTTPServer` or FastAPI |
| Email trigger | n8n IMAP node |

## Critical Config

### n8n IMAP Node
```json
{
  "format": "resolved",
  "downloadAttachments": true,
  "options": {
    "customEmailConfig": "[{\"key\":\"since\",\"value\":\"1 day ago\"}]"
  }
}
```

### Postgres Schema
```sql
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    invoice_number TEXT,
    vendor_name TEXT,
    invoice_date DATE,
    subtotal DECIMAL(10,2),
    tax DECIMAL(10,2),
    total DECIMAL(10,2),
    source_email TEXT,
    extraction_method TEXT,
    processed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE invoice_items (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER REFERENCES invoices(id),
    item_name TEXT,
    price DECIMAL(10,2),
    quantity INTEGER
);
```

## Common Gotchas

- **Binary key mismatch**: Use `$binary.attachment_0.mimeType` not `fileName`
- **Filename string match fails**: `"Phone bill .pdf"` doesn't `endsWith ".pdf"` — check mimeType instead
- **Gmail app passwords revoked silently**: Check credential status before saying "it works"
- **API key shell corruption**: Use Python file I/O to read keys, never shell variable expansion

## Quick Start

```bash
# 1. Create database
python3 -c "import psycopg2; conn = psycopg2.connect(...); cursor = conn.cursor(); cursor.execute(open('schema.sql').read()); conn.commit()"

# 2. Start API server
python3 invoice_api.py 9001

# 3. Test extraction
curl -X POST http://localhost:9001/extract \
  -F "invoice=@test_invoice.pdf"
```

## Output Files

- `invoice_api.py` — REST API (POST /extract, GET /invoices)
- `invoice_parser.py` — PDF extraction engine
- `invoice_dashboard.py` — HTML dashboard server
- `schema.sql` — Database schema
- `n8n-invoice-workflow.json` — n8n trigger workflow

## Variables

Set in `.env` or credential files:
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `SMTP_APP_PASSWORD` — Gmail app password for IMAP
- `API_PORT` — Dashboard port (default 9001)
