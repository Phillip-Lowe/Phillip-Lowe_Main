# Invoice Ingestion Workflow — Test Plan

## Test Environment
- **n8n Version:** Latest Docker image (`n8nio/n8n:latest`)
- **SOL Webhook:** Running on `host.docker.internal:9000`
- **SQLite DB:** `systack-invoices.db` (mounted at `/data/systack-invoices.db`)
- **Test Gmail Account:** [To be configured]

---

## Test Cases

### TC-01: Health Check — SOL Webhook
**Goal:** Verify SOL extraction service is reachable from n8n.

**Steps:**
1. Open n8n workflow canvas
2. Manually execute the "SOL: Extract Invoice" node with a test payload
3. Or use the test curl command from `sol-webhook-api.md`

**Expected Result:**
- HTTP 200 response
- JSON response with `status: "success"`

**Pass Criteria:** Response received within 10 seconds, no timeout errors.

---

### TC-02: Gmail Trigger — Poll for PDF Attachments
**Goal:** Verify Gmail node correctly filters emails with PDF attachments.

**Steps:**
1. Configure Gmail OAuth credential
2. Set Gmail node to search: `has:attachment filename:pdf`
3. Send a test email to the monitored inbox with a PDF attachment
4. Trigger manual execution or wait for poll interval

**Expected Result:**
- Workflow triggers on the test email
- Attachment data is present in the node output

**Pass Criteria:**
- Email is detected
- `attachments` array is non-empty
- `filename` ends with `.pdf`

---

### TC-03: Save PDF Attachment
**Goal:** Verify the Code node saves the PDF to `/tmp/n8n-invoices/`.

**Steps:**
1. Execute the workflow with a test email containing a PDF
2. SSH into the n8n container or check the mounted volume
3. List files in `/tmp/n8n-invoices/`

**Expected Result:**
- File exists with timestamp prefix
- File size matches original attachment

**Pass Criteria:**
- File is readable
- Filename is sanitized (no special characters)
- Directory is created if it didn't exist

---

### TC-04: SOL Extraction — Valid PDF
**Goal:** Verify the HTTP Request node successfully sends the PDF to SOL and receives structured data.

**Steps:**
1. Provide a valid invoice PDF (use `test-data/sample-invoice-acme.pdf`)
2. Execute the "SOL: Extract Invoice" node

**Expected Result:**
- HTTP 200
- Response contains `extracted_data` with:
  - `vendor_name`
  - `invoice_number`
  - `invoice_date`
  - `total_amount`
  - `line_items` (array)

**Pass Criteria:**
- All required fields are present
- `total_amount` is a number
- `line_items` is parseable JSON array

---

### TC-05: SOL Extraction — Error Handling
**Goal:** Verify workflow handles extraction failures gracefully.

**Steps:**
1. Provide an invalid or non-PDF file path
2. Execute the "SOL: Extract Invoice" node

**Expected Result:**
- Response contains `status: "error"`
- The "Parse Extraction Result" node throws an error
- Error workflow (if configured) is triggered

**Pass Criteria:**
- Workflow does not silently fail
- Error message is descriptive

---

### TC-06: SQLite Insert
**Goal:** Verify the SQLite node writes extracted data to the database.

**Steps:**
1. Execute the full workflow with a valid invoice PDF
2. Query the database:
   ```sql
   SELECT * FROM invoices ORDER BY id DESC LIMIT 1;
   ```

**Expected Result:**
- New row inserted with all fields populated
- `extracted_at` is a valid timestamp
- `processed` is `0`

**Pass Criteria:**
- Row count increases by 1
- `invoice_number` matches extracted data
- `line_items` is valid JSON string

---

### TC-07: Confirmation Email
**Goal:** Verify the Gmail node sends a confirmation email to the sender.

**Steps:**
1. Execute the full workflow
2. Check the sender's inbox

**Expected Result:**
- Email received within 1 minute
- Subject contains the invoice number
- Body contains vendor name and total amount

**Pass Criteria:**
- Email is not marked as spam
- Content is correctly rendered

---

### TC-08: End-to-End — Full Workflow
**Goal:** Verify the entire pipeline from Gmail → SQLite → Confirmation Email.

**Steps:**
1. Send an email with a sample invoice PDF to the monitored inbox
2. Wait for workflow execution (or trigger manually)
3. Check database for new entry
4. Check sender inbox for confirmation

**Expected Result:**
- Workflow completes without errors
- Database has new invoice record
- Confirmation email is sent

**Pass Criteria:**
- All nodes execute successfully
- No timeout or credential errors
- Data integrity is maintained end-to-end

---

## Performance Benchmarks

| Metric | Target |
|--------|--------|
| Gmail poll → trigger | < 60 seconds (based on polling interval) |
| SOL extraction | < 30 seconds per PDF |
| SQLite insert | < 2 seconds |
| Confirmation email | < 10 seconds |
| Total pipeline (manual) | < 60 seconds |

---

## Known Limitations

1. **Gmail Polling:** The workflow uses polling, not real-time push. Emails may take up to 1 minute to be detected depending on n8n trigger settings.
2. **Single Attachment:** The current Code node processes only the first PDF attachment per email. Multi-invoice emails require enhancement.
3. **File Cleanup:** `/tmp/n8n-invoices/` is not automatically purged. A cleanup job should be scheduled.
4. **Error Workflow:** Must be configured separately for failure notifications.

---

## Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| Tester | | | |
| SOL Review | | | |
| GREEN Approval | | | |
