# Invoice Ingestion Workflow — Credential Requirements

## Overview
This document lists the credentials required to run the `invoice-ingestion-v1.json` n8n workflow.

## Required Credentials

### 1. Gmail OAuth 2.0 API
**Used by:** Gmail trigger node, Send Confirmation Email node

**Setup Steps:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable the **Gmail API**
4. Create OAuth 2.0 credentials (Desktop app or Web app)
5. Add the following OAuth scopes:
   - `https://www.googleapis.com/auth/gmail.readonly` (read emails)
   - `https://www.googleapis.com/auth/gmail.send` (send confirmation)
6. Download `client_id` and `client_secret`
7. In n8n, go to **Settings → Credentials → Add Credential**
8. Select **Google OAuth2 API**
9. Enter `client_id` and `client_secret`
10. Complete the OAuth consent flow

**Credential ID placeholder in workflow:** `GMAIL_OAUTH_CRED_ID`

---

### 2. SQLite Database Connection
**Used by:** SQLite insert node

**Setup Steps:**
1. In n8n, go to **Settings → Credentials → Add Credential**
2. Select **SQLite**
3. Configure:
   - **Database file path:** `/data/systack-invoices.db` (mounted Docker volume path)
   - Or if running n8n natively: `/Users/philliplowe/.openclaw/workspaces/sol/systack-invoices.db`
4. Ensure the database file exists and the `invoices` table is created (see schema below)

**Credential ID placeholder in workflow:** `SQLITE_CRED_ID`

---

## Database Schema (Prerequisite)

Ensure the SQLite database has this table before activating the workflow:

```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT,
    vendor_name TEXT,
    invoice_date TEXT,
    total_amount REAL,
    line_items TEXT,
    source_email TEXT,
    file_path TEXT,
    extraction_method TEXT,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT 0
);
```

---

## n8n Docker Volume Mount (If applicable)

If running n8n in Docker, mount the host database into the container:

```yaml
volumes:
  - /Users/philliplowe/.openclaw/workspaces/sol/systack-invoices.db:/data/systack-invoices.db
```

This ensures the SQLite node can write to the same database file used by SOL.

---

## Optional: Error Workflow

The workflow references an error workflow (`ERROR_WORKFLOW_ID`). To configure:
1. Create a simple error notification workflow in n8n
2. Copy its workflow ID
3. Replace `ERROR_WORKFLOW_ID` in the workflow settings

---

## Security Notes

- Store credentials in n8n's built-in credential vault, never in the workflow JSON
- Rotate OAuth tokens periodically
- Use separate Gmail accounts for ingestion vs. personal email
- Ensure `/tmp/n8n-invoices/` is periodically cleaned to avoid disk bloat
