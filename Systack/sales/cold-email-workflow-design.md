# Cold Email Workflow Design Doc

**Created:** 2026-07-07
**Author:** SOL 🛰️
**Status:** Ready for deployment (pending credentials)

---

## Overview

Two n8n workflows built for the SAOS outreach engine:

| # | Workflow | File | Nodes |
|---|----------|------|-------|
| 1 | SAOS Cold Email Sequence Sender | `n8n-workflows-v2/saos-cold-email-sequence-v2.json` | 11 |
| 2 | SAOS Pipeline Tracker Sync | `n8n-workflows-v2/saos-pipeline-sync-v2.json` | 13 |

Both are inactive, contain no embedded credentials, and are ready for import via n8n REST API.

---

## Workflow 1: Cold Email Sequence Sender

### What It Does

Sends a 3-touch cold email sequence to prospects:
- **Email 1 (Day 0):** Pain-driven cold email personalized with prospect's industry + pain points
- **Email 2 (Day 3):** Case study follow-up showing ROI
- **Email 3 (Day 10):** Breakup email with "later" / "no thanks" reply options

After the sequence completes, it updates the pipeline tracker via webhook.

### Triggers
- **Schedule Trigger:** Runs every Monday at 9 AM (configurable)
- **Manual Trigger:** Can be triggered manually for testing or one-off batches

### Node-by-Node Breakdown

| # | Node | Type | Purpose |
|---|------|------|---------|
| 1 | Weekly Monday Trigger | scheduleTrigger | Auto-starts sequence every Monday |
| 2 | Manual Start | manualTrigger | For manual batch sends / testing |
| 3 | Process Prospects | code | Filters uncontacted prospects, personalizes all 3 email templates per prospect |
| 4 | Send Email 1 (Initial) | gmail | Sends pain-driven email |
| 5 | Wait 3 Days | wait | Pauses 3 days before follow-up |
| 6 | Send Email 2 (Follow-up) | gmail | Sends case study email |
| 7 | Wait 7 Days | wait | Pauses 7 days before breakup |
| 8 | Send Email 3 (Breakup) | gmail | Sends breakup email |
| 9 | Update Pipeline Tracker | httpRequest | POSTs to pipeline API to update stage |
| 10 | Error Handler | errorTrigger | Catches workflow errors |
| 11 | Notify Green on Error | gmail | Sends error alert to green@systack.net |

### Email Personalization

The Code node (Process Prospects) takes prospect data and generates:
- Personalized subject lines using industry type
- Email body referencing company name + specific pain points
- Industry-appropriate messaging (restaurant, 3PL, accounting, healthcare, etc.)

### Prospect Data Source

Currently embedded as a JS array in the Code node (3 sample prospects). Production options:

| Source | How to Switch | Pros | Cons |
|--------|--------------|------|------|
| Google Sheets | Replace Code node with Google Sheets Read node | Live editing, Green can update | Needs Sheets API credential |
| PostgreSQL | Replace Code node with Postgres Read node | Integrated with SAOS DB | Needs connection string |
| Local JSON file | Point Code node to read a file | Simple, no external deps | Manual updates |

**Recommended:** Google Sheets — lets Green update prospects without touching n8n.

---

## Workflow 2: Pipeline Tracker Sync

### What It Does

Receives email engagement events (opens, clicks, replies, bounces, unsubscribes) via webhook and:
1. Updates the prospect's stage in the pipeline tracker
2. Notifies Green immediately when a prospect replies (via email)
3. Alerts Green on bounces (likely bad email address)
4. Silently logs opens and clicks (no notification)

### Node-by-Node Breakdown

| # | Node | Type | Purpose |
|---|------|------|---------|
| 1 | Webhook Trigger | webhook | Receives POST events at `/saos-pipeline-sync` |
| 2 | Parse Event | code | Extracts event_type, prospect info, reply content |
| 3 | Event Type Switch | switch | Routes to handler based on event type |
| 4 | Update Tracker (Reply) | httpRequest | Updates stage → "Discovery Scheduled" |
| 5 | Notify Green (Reply) | gmail | 🎉 alert with prospect's reply content |
| 6 | Update Tracker (Open) | httpRequest | Silently logs open event |
| 7 | Update Tracker (Click) | httpRequest | Logs click + link clicked |
| 8 | Update Tracker (Bounce) | httpRequest | Updates stage → "Closed Lost" |
| 9 | Notify Green (Bounce) | gmail | ⚠️ alert with bad email address |
| 10 | Update Tracker (Unsubscribe) | httpRequest | Updates stage → "Closed Lost" |
| 11 | Success Response | respondToWebhook | Returns 200 OK with status |
| 12 | Error Handler | errorTrigger | Catches workflow errors |
| 13 | Notify Green on Error | gmail | Error alert to green@systack.net |

### Webhook Payload Format

```json
{
  "event_type": "email_reply | email_open | email_click | email_bounce | email_unsubscribe",
  "prospect_email": "jim.harrison@midwestfulfillment.com",
  "prospect_name": "Jim Harrison",
  "company": "Midwest Fulfillment Partners",
  "timestamp": "2026-07-07T18:30:00Z",
  "reply_body": "Yes, let's talk. When are you free?",
  "link": "https://portal.systack.net/book"
}
```

### Event → Stage Mapping

| Event | Pipeline Stage | Green Notified? |
|-------|---------------|-----------------|
| email_open | Outreach Sent | No (silent) |
| email_click | Outreach Sent | No (silent) |
| email_reply | Discovery Scheduled | ✅ Yes — immediate |
| email_bounce | Closed Lost | ✅ Yes — bad address |
| email_unsubscribe | Closed Lost | No (silent) |

---

## Credentials Needed Before Activation

| # | Credential | n8n Type | Purpose |
|---|-----------|----------|---------|
| 1 | Gmail — SAOS Outreach | gmail OAuth2 | Sending cold emails + error/reply notifications |
| 2 | SAOS Internal API | httpRequest header | Pipeline tracker API auth (optional, can be added as header) |

**Gmail setup:**
1. Create or designate a sending account (green@systack.net or saos.outreach@systack.net)
2. In n8n → Settings → Credentials → Add → Google Gmail OAuth2
3. Authorize the account
4. Name the credential "Gmail - SAOS Outreach" (must match workflow reference)
5. Update the credential ID in the workflow JSON if different from placeholder

**Pipeline API:**
- The workflow POSTs to `https://portal.systack.net/api/v1/sales/pipeline-update`
- This endpoint needs to be added to the SAOS API (api.py)
- Auth via SAOS_INTERNAL_API_KEY header (can be added to HTTP Request node options)

---

## Deployment Commands

### Get the n8n API key
```bash
export N8N_API_KEY=$(sqlite3 ~/.n8n/database.sqlite \
  "SELECT apiKey FROM user_api_keys WHERE label='OPENCLAW' LIMIT 1")
```

### Import Workflow 1 (Cold Email Sequence)
```bash
# Create (inactive)
curl -s -X POST http://localhost:5678/api/v1/workflows \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d @Systack/content/saos/saos-data/n8n-workflows-v2/saos-cold-email-sequence-v2.json

# After credentials configured, activate:
# curl -s -X POST "http://localhost:5678/api/v1/workflows/{ID}/activate" \
#   -H "X-N8N-API-KEY: $N8N_API_KEY"
```

### Import Workflow 2 (Pipeline Sync)
```bash
# Create (inactive)
curl -s -X POST http://localhost:5678/api/v1/workflows \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d @Systack/content/saos/saos-data/n8n-workflows-v2/saos-pipeline-sync-v2.json

# After credentials configured, activate:
# curl -s -X POST "http://localhost:5678/api/v1/workflows/{ID}/activate" \
#   -H "X-N8N-API-KEY: $N8N_API_KEY"
```

### Post-Import: Run Prevention SQL
After any workflow import via API, run the prevention SQL from TOOLS.md to avoid the n8n UI blank workflow list bug.

---

## What's Ready vs What's Needed

### ✅ Ready Now
- Both workflow JSON files written and validated
- Pipeline tracker populated with all 20 prospects
- Email templates personalized for 5 industries
- Error handling on both workflows
- Design doc (this file)

### ⏳ Needs Green Before Launch
1. **Choose sending email address** — green@systack.net or dedicated
2. **Configure Gmail credential in n8n** — 5 min setup in UI
3. **Add pipeline-update API endpoint** to api.py — SOL can do this
4. **Set up Calendly link** — for discovery call booking
5. **Approve first 6 hot prospects** — give the go-ahead

### 🔲 After First Customer
- Connect prospect data source (Google Sheets recommended)
- Set up email tracking (opens/clicks) — requires either Gmail API extensions or a tracking pixel service
- Proposal auto-generation from templates

---

*SOL 🛰️ — 2026-07-07*