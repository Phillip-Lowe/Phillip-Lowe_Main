# 2026-06-30 — SAOS Service Workflows Built + iOS Cert Trust Plan

**Time:** ~20:10 CDT
**Status:** ✅ COMPLETE (workflows built) / ⏳ PLAN CREATED (iOS cert)

---

## What Was Built

### 3 Missing n8n Service Workflows (JSON Files)

| Workflow | File | Nodes | Purpose |
|----------|------|-------|---------|
| **Customer Support Drafting** | `n8n-customer-support-drafting.json` | 6 | Webhook receives support request → drafts AI response → queues for human review → notifies customer |
| **Document Classification Engine** | `n8n-document-classification.json` | 7 | Webhook on file upload → classifies by filename pattern (invoice/contract/form/report/other) → routes to appropriate task queue |
| **Scheduled Report Generator** | `n8n-scheduled-report-generator.json` | 8 | Daily cron → queries task_queue, chat_messages, usage_metrics → builds summary report → sends email + dashboard notification |

### Workflow Details

**Customer Support Drafting:**
- Trigger: POST to `/webhook/saos-support-request`
- Parses conversation_id, client_id, content, urgency, category
- Drafts contextual response based on category (billing/technical/general)
- Creates task in task_queue for human review
- Sends acknowledgment via chat webhook
- Returns 200 with draft preview

**Document Classification:**
- Trigger: POST to `/webhook/saos-doc-uploaded`
- Classifies by filename keywords and extension
- If invoice → routes to Invoice Processing Pipeline task queue
- Otherwise → routes to Document Classification Engine task queue
- Sends dashboard notification with classification result
- Returns 200 with classification type

**Scheduled Report:**
- Trigger: Daily schedule (every 24 hours)
- Queries 3 PostgreSQL tables: task_queue, chat_messages, usage_metrics
- Calculates: completed/pending/failed tasks, chat volume, n8n runs, API calls
- Sends email report to phillip@systack.net
- Posts dashboard notification with summary

### Technical Notes
- All workflows JSON-valid and import-ready for n8n
- Node types: webhook, code, httpRequest, postgres, emailSend, if, respondToWebhook, scheduleTrigger
- Active flag: true
- Tagged: SAOS
- Compatible with n8n 2.20.7-exp

### Bug Fix During Build
- `n8n-customer-support-drafting.json` initially had invalid JSON escape sequences (`\`` instead of `` ` ``)
- Fixed via Python regex replacement
- All 3 files now pass JSON validation

---

## iOS Safari `.ts.net` Certificate Trust

### Problem
iOS Safari blocks `*.ts.net` Tailscale URLs with "Certificate Invalid" error. macOS trusts these via Tailscale system extension; iOS does not.

### Plan Created
**File:** `IOS-CERT-TRUST-PLAN.md`

**Recommended Solution:** Cloudflare Tunnel (Option 2)
- Free, 1 hour setup
- Replaces `.ts.net` with real domain (e.g., `dashboard.systack.net`)
- Zero cert issues on any device
- Can run parallel with Tailscale

**Alternative:** Custom domain A record (Option 1)
- Requires public IP or VPS proxy
- More complex but fully independent

**Decision:** Awaiting Green's confirmation on which option to implement.

---

## Files Changed/Added

| File | Action | Size |
|------|--------|------|
| `n8n-customer-support-drafting.json` | ✅ Created | 5.0KB |
| `n8n-document-classification.json` | ✅ Created | 6.8KB |
| `n8n-scheduled-report-generator.json` | ✅ Created | 7.4KB |
| `IOS-CERT-TRUST-PLAN.md` | ✅ Created | 6.2KB |

---

## Next Steps

1. **Import workflows to n8n** — Use n8n UI Import or `n8n import:workflow`
2. **Test each workflow** — Trigger webhooks with curl, verify task creation
3. **Implement iOS fix** — Awaiting Green's decision on Cloudflare Tunnel vs custom domain
4. **Update dashboard services** — Mark the 3 services as "active" once workflows are imported

---

## Verification

```bash
# All JSON files validated:
python3 -c "import json; [json.load(open(f)) for f in ['n8n-customer-support-drafting.json', 'n8n-document-classification.json', 'n8n-scheduled-report-generator.json']]; print('All valid')"
# → All valid
```
