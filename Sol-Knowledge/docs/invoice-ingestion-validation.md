# Invoice Ingestion Workflow v1 — Validation Report

**Generated:** 2026-05-20
**Status:** ✅ READY FOR REVIEW

---

## Workflow File
- **Path:** `n8n-workflows/invoice-ingestion-v1.json`
- **Name:** Invoice Ingestion v1 — Gmail → SOL → SQLite
- **Status:** Inactive (pending credential setup and SOL approval)

---

## Node Inventory (6 nodes)

| # | Node Name | Type | Purpose |
|---|-----------|------|---------|
| 1 | Gmail: Invoice Emails | `n8n-nodes-base.gmail` | Trigger: Poll Gmail for emails with PDF attachments |
| 2 | Save PDF Attachment | `n8n-nodes-base.code` | Save PDF(s) to `/tmp/n8n-invoices/` |
| 3 | SOL: Extract Invoice | `n8n-nodes-base.httpRequest` | POST to SOL webhook for AI extraction |
| 4 | Parse Extraction Result | `n8n-nodes-base.code` | Validate and format SOL response |
| 5 | SQLite: Insert Invoice | `n8n-nodes-base.sqlite` | Write extracted data to local database |
| 6 | Send Confirmation Email | `n8n-nodes-base.gmail` | Acknowledge receipt to sender |

---

## Connection Flow

```
Gmail: Invoice Emails
    ↓
Save PDF Attachment
    ↓
SOL: Extract Invoice (POST http://host.docker.internal:9000/invoice/extract)
    ↓
Parse Extraction Result
    ↓
SQLite: Insert Invoice
    ↓
Send Confirmation Email
```

---

## Credential Requirements

| Credential | Node(s) | Status |
|------------|---------|--------|
| Gmail OAuth 2.0 API | Gmail trigger, Confirmation email | ⬜ Placeholder: `GMAIL_OAUTH_CRED_ID` |
| SQLite | SQLite insert | ⬜ Placeholder: `SQLITE_CRED_ID` |

**Action required:** Replace placeholder IDs with actual n8n credential IDs before activation.

---

## Schema Compatibility

| DB Column | Workflow Field | Type | Status |
|-----------|---------------|------|--------|
| `invoice_number` | `invoice_number` | TEXT | ✅ Mapped |
| `vendor_name` | `vendor_name` | TEXT | ✅ Mapped |
| `invoice_date` | `invoice_date` | TEXT | ✅ Mapped |
| `total_amount` | `total_amount` | REAL | ✅ Mapped |
| `line_items` | `line_items` (JSON string) | TEXT | ✅ Mapped |
| `source_email` | `source_email` | TEXT | ✅ Mapped |
| `file_path` | `file_path` | TEXT | ✅ Mapped |
| `extraction_method` | `extraction_method` | TEXT | ✅ Mapped |
| `extracted_at` | `extracted_at` | TIMESTAMP | ✅ Mapped |
| `processed` | `processed` (default 0) | BOOLEAN | ✅ Mapped |

---

## API Compliance

✅ Uses correct SOL webhook endpoint: `POST /invoice/extract`
✅ Sends required fields: `file_path`, `source_email`
✅ Expects response format: `{ status, extracted_data, ... }`
✅ Handles error responses: throws on `status === "error"`

---

## Files Delivered

| File | Purpose |
|------|---------|
| `n8n-workflows/invoice-ingestion-v1.json` | Production workflow definition |
| `docs/invoice-ingestion-credentials.md` | Step-by-step credential setup guide |
| `docs/invoice-ingestion-test-plan.md` | 8 test cases with pass criteria |
| `docs/sol-webhook-api.md` (updated) | Added n8n integration pattern reference |

---

## Known Limitations

1. **Polling delay:** Gmail trigger uses polling, not instant push
2. **Single attachment focus:** Code node processes all PDFs but pipeline is optimized for single-invoice emails
3. **No automatic cleanup:** `/tmp/n8n-invoices/` grows over time
4. **Error workflow not configured:** Placeholder `ERROR_WORKFLOW_ID` needs replacement

---

## Next Steps (SOL Approval Required)

1. ⬜ Configure Gmail OAuth credential in n8n
2. ⬜ Configure SQLite credential in n8n
3. ⬜ Update placeholder IDs in workflow JSON
4. ⬜ Mount `systack-invoices.db` into n8n Docker container (if applicable)
5. ⬜ Run TC-01 through TC-08 from test plan
6. ⬜ Set workflow `active: true` after successful testing

---

**Approved by:** _______________  **Date:** _______________
