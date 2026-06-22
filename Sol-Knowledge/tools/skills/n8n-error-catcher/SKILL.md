---
name: n8n-error-catcher
description: "Cross-system error handling workflow that catches failures from all n8n workflows, routes to appropriate channels, retries with backoff, and escalates after thresholds."
---

# n8n Error Catcher

Centralized error handling for all n8n workflows. Catches failures → classifies → routes → retries → escalates.

## When to Use
- Any new n8n workflow going to production
- Existing workflows showing intermittent failures
- Setting up monitoring/alerting for automation health
- Client reporting "orders not coming through"

## Architecture

```
Any workflow fails
    ↓
Error Workflow (this one)
    ↓
Classify error type
    ↓
Route:
    ├── Network timeout → Retry (exponential backoff)
    ├── API rate limit → Wait + retry
    ├── Auth expired → Alert + pause workflow
    ├── Data validation → Log + skip
    └── Unknown → Escalate to human
```

## Error Classification

| Error Pattern | Action | Retry? |
|--------------|--------|--------|
| `ETIMEDOUT`, `ECONNRESET` | Retry with 30s, 60s, 120s backoff | Yes, 3x |
| `429 Too Many Requests` | Wait 60s, retry | Yes, 5x |
| `401 Unauthorized` | Alert admin, pause workflow | No |
| `403 Forbidden` | Alert admin, investigate | No |
| Validation failed | Log details, skip item | No |
| Webhook body empty | Log, retry once | Yes, 1x |
| Unknown / 500 | Log, alert, retry 3x | Yes, 3x |

## Workflow Setup

### Step 1: Import Error Catcher
Import `n8n-workflows/error-catcher-master-v2.json`

### Step 2: Set as Error Workflow
In each production workflow's settings:
- Error Workflow: Select "Error Catcher — Master"
- Save and activate

### Step 3: Configure Alert Channels
- **Slack/Discord** — Immediate alerts for auth failures
- **Email** — Daily digest of retried errors
- **Dashboard** — Real-time error stream

## Critical Rules

1. **Every production workflow MUST have error workflow set**
2. **Never silently drop errors** — always log, always notify
3. **Same workflow failing > 3x in 24h → PAUSE** — prevent spam
4. **Auth failures → IMMEDIATE ALERT** — don't waste retries
5. **Log error context** — payload that caused failure, timestamp, retry count

## Retry Logic

```javascript
// n8n Code node — exponential backoff
const retryCount = $json.retryCount || 0;
const maxRetries = 3;
const delays = [30000, 60000, 120000]; // 30s, 1m, 2m

if (retryCount < maxRetries) {
  return [{
    json: {
      retry: true,
      waitMs: delays[retryCount],
      retryCount: retryCount + 1
    }
  }];
} else {
  return [{ json: { retry: false, escalate: true } }];
}
```

## Error Log Schema

Each error logged to SQLite/Postgres:
```sql
CREATE TABLE error_logs (
    id INTEGER PRIMARY KEY,
    workflow_name TEXT,
    workflow_id TEXT,
    error_message TEXT,
    error_type TEXT, -- 'network', 'auth', 'validation', 'unknown'
    retry_count INTEGER DEFAULT 0,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Integration with Other Skills

- **Invoice Pipeline** — Failed extractions logged here, retried
- **Green Lead Scraper** — Rate limit errors auto-handled
- **VPS Provisioning** — Provisioning failures escalated immediately

## Testing

Test error handling:
1. Trigger intentional failure (bad API key)
2. Verify classification correct
3. Check retry count increments
4. Confirm escalation after threshold
5. Validate alert received

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Errors not caught | Error workflow not set | Set in workflow settings |
| Retry storm | No max retry limit | Cap at 3-5 with backoff |
| Missing context | Error not including payload | Include `$json` in error log |
| Auth loops | Retrying auth failures | Classify 401 → no retry |

## Files

- `n8n-workflows/error-catcher-master-v2.json` — Main workflow
- `docs/automations/error-catcher/` — Full documentation
