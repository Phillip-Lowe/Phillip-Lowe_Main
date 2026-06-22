# V2 Workflow Deployment Log

**Date:** 2026-06-05 07:34 UTC
**Status:** ✅ DEPLOYED (Inactive — needs activation in n8n UI)

---

## Deployment Details

| Field | Value |
|-------|-------|
| **Workflow ID** | `29ebdb3c-6dac-4d3a-a119-5cdcc5707e48` |
| **Name** | Utopia Deli HTML Order v2 — CART_STATE Aligned |
| **Version ID** | `v2-initial-29ebdb3c` |
| **Active** | `false` (user must toggle in UI) |
| **Project** | `LPFVmXe92Be2P99s` (phillip lowe) |
| **Webhook** | `POST /webhook/utopia-deli-html-order-v2` |
| **Webhook ID** | `utopia-deli-html-order-v2` |

---

## Database Entries Created

### 1. workflow_entity
- Full workflow definition (14 nodes, connections, settings)
- Status: `active = 0` (inactive)

### 2. workflow_history
- Version snapshot for execution
- Author: `import`
- Autosaved: `0`

### 3. workflow_published_version
- Published version: `v2-initial-29ebdb3c`
- n8n will execute from this version

### 4. shared_workflow
- Project: `LPFVmXe92Be2P99s`
- Role: `workflow:owner`
- Same project as all other deli workflows

### 5. webhook_entity
- Path: `utopia-deli-html-order-v2`
- Method: `POST`
- Node: `Webhook Trigger`
- Webhook ID: `utopia-deli-html-order-v2`

---

## Credentials Used (Same as Existing Workflows)

| Service | Credential | ID | Status |
|---------|-----------|-----|--------|
| **SMTP / Email** | `deli gmail` | `ZOvYr6kSP7zE8tBv` | ✅ Shared in project |
| **Square API** | `Square API` | `9FQ7SQhaUqssIJJb` | ✅ Shared in project |
| **Google Sheets** | OAuth (auto) | — | ✅ Project has access |

---

## Node Count: 14

```
1.  Webhook Trigger
2.  Validate JSON
3.  Valid? (if/else)
4.  Normalize HTML → CART_STATE
5.  Write CART_STATE → Sheets
6.  Build cart_html
7.  Email Template
8.  Create Payment Link (Square)
9.  Normalize Payment Response
10. Update CART_STATE → LOCKED
11. Compose Final Email
12. Send Payment Email
13. Success Response
14. Error Response
```

---

## Required Next Steps

### 1. Activate in n8n UI
```
n8n UI → Workflows → "Utopia Deli HTML Order v2 — CART_STATE Aligned"
→ Toggle Active (top right)
```

### 2. Test with curl
```bash
curl -X POST https://n8n.systack.net/webhook/utopia-deli-html-order-v2 \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Test Customer",
    "email": "test@example.com",
    "phone": "(501) 555-9999",
    "order_items": [
      {"name": "The Cowboy", "qty": 1, "price": 10.99, "modifiers": ["+ Avocado ($0.50)", "no onions"]}
    ],
    "subtotal": 10.99,
    "tax": 1.05,
    "total": 12.04,
    "pickup_time": "14:30"
  }'
```

### 3. Verify CART_STATE in Google Sheets
- New row should appear with `status = OPEN`
- After payment link creation, `status = LOCKED`

### 4. Update Frontend
Change frontend POST URL from:
```
/webhook/utopia-deli-html-order-v1
```
to:
```
/webhook/utopia-deli-html-order-v2
```

---

## Rollback

If issues occur:
```sql
-- Deactivate
UPDATE workflow_entity SET active = 0 WHERE id = '29ebdb3c-6dac-4d3a-a119-5cdcc5707e48';

-- Or delete entirely
DELETE FROM workflow_entity WHERE id = '29ebdb3c-6dac-4d3a-a119-5cdcc5707e48';
DELETE FROM workflow_history WHERE workflowId = '29ebdb3c-6dac-4d3a-a119-5cdcc5707e48';
DELETE FROM workflow_published_version WHERE workflowId = '29ebdb3c-6dac-4d3a-a119-5cdcc5707e48';
DELETE FROM shared_workflow WHERE workflowId = '29ebdb3c-6dac-4d3a-a119-5cdcc5707e48';
DELETE FROM webhook_entity WHERE workflowId = '29ebdb3c-6dac-4d3a-a119-5cdcc5707e48';
```

---

## V1 vs V2 Comparison

| Aspect | V1 (Active) | V2 (Deployed, Inactive) |
|--------|------------|------------------------|
| Database | None | ✅ CART_STATE registry |
| Email | Plain text | ✅ Branded HTML (deli gmail SMTP) |
| Square auth | httpBearerAuth | ✅ httpHeaderAuth (matches WKFL 4) |
| Modifier handling | Strings | ✅ Structured objects |
| cart_html | Basic | ✅ Branded with categories |
| Status tracking | None | ✅ OPEN → LOCKED → PAID |
| Lifecycle | ❌ | ✅ Full participation |

---

**Deployed by:** SOL (agent)
**Source files:** `~/utopia-deli-revamp/workflow-study/`
