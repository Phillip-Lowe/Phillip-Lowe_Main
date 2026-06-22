# SOL Invoice Webhook API Reference

**Base URL:** `http://localhost:9000` (local) or via Tailscale

## Endpoints

### POST /invoice/extract
Extract structured data from an invoice PDF.

**Request:**
```json
{
  "file_path": "/absolute/path/to/invoice.pdf",
  "source_email": "sender@example.com"
}
```

**Response (success):**
```json
{
  "status": "success",
  "source_email": "sender@example.com",
  "file_path": "/path/to/invoice.pdf",
  "extracted_data": {
    "vendor_name": "Acme Supplies",
    "invoice_number": "INV-2024-001",
    "invoice_date": "2024-01-15",
    "total_amount": 1250.00,
    "line_items": [
      {
        "description": "Office Chairs",
        "quantity": 5,
        "unit_price": 200.00,
        "subtotal": 1000.00
      },
      {
        "description": "Shipping",
        "quantity": 1,
        "unit_price": 250.00,
        "subtotal": 250.00
      }
    ]
  }
}
```

**Response (error):**
```json
{
  "status": "error",
  "message": "File not found: /path/to/invoice.pdf"
}
```

### GET /health
Server health check.

**Response:**
```json
{
  "status": "ok",
  "service": "sol-invoice-webhook",
  "port": 9000
}
```

## n8n Integration Pattern

### n8n → SOL (Invoice Extraction)

**Production Workflow:** `n8n-workflows/invoice-ingestion-v1.json`

```
[Gmail Trigger] → [Save Attachment] → [HTTP Request to SOL] → [Parse JSON] → [SQLite Insert] → [Confirmation Email]
```

**Nodes:**
1. **Gmail: Invoice Emails** — Polls Gmail for emails with PDF attachments
2. **Save PDF Attachment** — Code node saves attachment to `/tmp/n8n-invoices/`
3. **SOL: Extract Invoice** — HTTP Request POST to `http://host.docker.internal:9000/invoice/extract`
4. **Parse Extraction Result** — Code node validates and formats SOL response
5. **SQLite: Insert Invoice** — Writes extracted data to `systack-invoices.db`
6. **Send Confirmation Email** — Gmail node sends acknowledgment to sender

**See also:**
- Credential setup: `docs/invoice-ingestion-credentials.md`
- Test plan: `docs/invoice-ingestion-test-plan.md`

### Legacy Pattern (Google Sheets)
```
[Email Trigger] → [Save Attachment] → [HTTP Request to SOL] → [Parse JSON] → [Google Sheets]
```

**HTTP Request node config:**
- Method: POST
- URL: `http://host.docker.internal:9000/invoice/extract` (if n8n in Docker)
- URL: `http://localhost:9000/invoice/extract` (if n8n native)
- Body: JSON
```json
{
  "file_path": "{{$json.attachmentPath}}",
  "source_email": "{{$json.sender}}"
}
```

### SOL → n8n (Future: Trigger n8n from SOL)
When SOL needs to trigger an n8n workflow:
- Use n8n Webhook trigger URL
- POST from SOL to `https://n8n.theutopiadeli.com/webhook/<path>`

## Testing

```bash
# Health check
curl http://localhost:9000/health

# Test extraction (with sample PDF)
curl -X POST http://localhost:9000/invoice/extract \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/sample-invoice.pdf", "source_email": "test@example.com"}'
```
