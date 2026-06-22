---
name: green-n8n-monitor
description: Monitor n8n workflows for failures and alert Green. Pings n8n API, checks execution status, and sends alerts via email or webhook when workflows fail. Built for Green's n8n instance.
---

# Green n8n Monitor

Monitor n8n workflows for failures and alert Green. Pings n8n API, checks execution status, and sends alerts via email or webhook when workflows fail.

## Pipeline

1. **Fetch executions** — Query n8n API for recent workflow runs
2. **Filter failures** — Identify failed, crashed, or error executions
3. **Alert** — Send notification via email, webhook, or Slack
4. **Log** — Write status to CSV for historical tracking
5. **Dashboard** — Optional HTML dashboard of workflow health

## Requirements

- Node.js 18+
- n8n API key (from n8n Settings → API)
- n8n instance URL
- Alert destination: email (Resend), webhook, or Slack

## Quick Start

```bash
# Set credentials
export N8N_API_KEY=n8n_api_xxx
export N8N_URL=https://n8n.systack.net
export RESEND_API_KEY=re_xxx
export ALERT_EMAIL=green@systack.net

# Run once
node scripts/monitor.js

# Run with webhook alert
node scripts/monitor.js --webhook https://hooks.slack.com/services/xxx

# Generate dashboard
node scripts/monitor.js --dashboard dashboard.html

# Run continuously (every 5 min)
node scripts/monitor.js --interval 300000
```

## Configuration

Edit `scripts/config.json`:
- `n8nUrl`: n8n instance URL
- `n8nApiKey`: API key (or use env var)
- `alertEmail`: Where to send alerts
- `webhookUrl`: Optional webhook for alerts
- `checkInterval`: How often to check (ms)
- `maxExecutions`: How many executions to fetch (default: 50)
- `includeSuccessful`: Also log successful runs (default: false)

## Output

### Status Log CSV
```csv
timestamp,workflow_id,workflow_name,execution_id,status,duration,error_message
2026-06-05T06:00:00Z,IW27pwPj5DBYQdcq,Payment Confirmed,12345,error,1500,"Connection refused"
```

### Alert Format
```json
{
  "alert": "n8n_workflow_failure",
  "timestamp": "2026-06-05T06:00:00Z",
  "workflow": {
    "id": "IW27pwPj5DBYQdcq",
    "name": "Payment Confirmed Email"
  },
  "execution": {
    "id": "12345",
    "status": "error",
    "startedAt": "2026-06-05T05:59:00Z",
    "stoppedAt": "2026-06-05T06:00:00Z",
    "error": "Connection refused"
  }
}
```

## Scripts

- `scripts/monitor.js` — Main monitoring engine
- `scripts/dashboard.js` — Generate HTML dashboard
- `scripts/config.json` — Configuration

## Alert Channels

### Email (Resend)
Set `RESEND_API_KEY` and `ALERT_EMAIL`.

### Webhook
Pass `--webhook URL` or set in config. Payload is JSON.

### Slack
Use webhook URL from Slack app settings.

## Safety

- API key never logged
- Rate limiting on n8n API (max 1 request per 5 seconds)
- No modification of workflows — read-only monitoring

## References

- See `references/n8n-api.md` for n8n API documentation
