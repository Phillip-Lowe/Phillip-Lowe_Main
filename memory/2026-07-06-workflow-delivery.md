# Session — 2026-07-06 06:15 CDT
## ORACLE: Workflow Delivery Visibility System — Phase 1 Complete

---

## Architecture Decision

**Hybrid A → B** (per ORACLE directive):
- **Phase 1 (NOW)**: Shared n8n with strict customer isolation via database tenanting
- **Phase 2 (Later)**: Dedicated per-customer n8n for Enterprise tier
- **Phase 3 (Future)**: Bring-your-own n8n for advanced customers

---

## What Was Built

### 1. Database Schema
Created 3 tables in `scripts/add_workflow_tables.sql`:
- `customer_workflows` — Tenant-isolated workflow records (20 fields)
- `workflow_events` — Lifecycle audit trail
- `workflow_test_runs` — Customer-triggered webhook tests

### 2. API Routes (7 Endpoints)
- `GET /api/workflows` — Customer list
- `GET /api/workflows/<id>` — Customer detail + events + test history
- `POST /api/workflows/<id>/test` — Customer webhook test
- `POST /api/internal/workflows` — Agent creates record
- `PATCH /api/internal/workflows/<id>` — Agent updates status
- `POST /api/internal/workflows/<id>/notify` — Agent sends notifications
- `GET /api/internal/workflows/pending-deployments` — Ops queue

### 3. Portal Tab
- "⚙️ My Workflows" added to customer nav
- Full detail view with status, webhook, events, test history
- Actions: View Details, Test Webhook, Download Backup

### 4. Bug Fixes
- **Added `db_insert()` helper** — `db_query()` couldn't handle INSERTs (called `fetchall()` causing rollback)
- **Fixed SQL `NOT %s` bug** — `CASE WHEN NOT True` evaluated to False, skipping error_count increment
- **Added missing `require_internal_api_key`** — Was referenced but never defined, causing NameError

### 5. Notification Templates
- Dashboard: Rich status card with actions
- Email: Subject "✅ Workflow Delivered: {name}"
- iMessage: "{name} is live ✅" (urgent/enterprise only)

---

## Test Results

| Test | Result |
|------|--------|
| GET /api/workflows | ✅ Returns isolated list |
| GET /api/workflows/1 | ✅ Full detail + 4 events + 3 test runs |
| POST /api/workflows/1/test | ✅ Records test, updates error_count |
| Client isolation | ✅ WHERE client_id = current_client_id |
| Frontend rendering | ✅ Tab present, functions loaded |

---

## Files Changed
- `api.py` — 7 new routes, `db_insert()` helper, bug fixes
- `index.html` — "My Workflows" tab + JS functions
- `scripts/add_workflow_tables.sql` — Schema creation
- `WORKFLOW_DELIVERY_STATUS.md` — Implementation doc

---

## Known Issues
1. Webhook test gets 403 on demo URL (expected — fake webhook)
2. Internal API key requires env var `SAOS_INTERNAL_API_KEY`
3. Notifications queued but require n8n dispatcher to send

## Next Recommended Patch
Command Center workflow ops view — internal dashboard for monitoring all customer workflows.

## Update — Command Center Workflow Ops View BUILT
**Time:** 2026-07-06 06:47 CDT
**Status:** ✅ Complete
**Endpoint:** `GET /api/fleet/workflows` (Command Center)

### What's Now Visible in Command Center:
- **Stats summary**: total, active, draft, building, failed, paused, shared, dedicated, tested_24h, total_errors
- **Workflow list**: All customer workflows with client name, status, webhook, last run, error count
- **Pending deployments**: Queue of workflows needing attention (draft/building/deployed/needs_review)
- **Recent events**: Cross-customer event stream (created, deployed, tested, failed)
- **Architecture mode**: Shows "shared" (Phase 1)

### Files Changed
- `systack-command-center/api.py` — Enhanced `/api/fleet/workflows` with customer data
- Added `get_pool()` helper for connection pool access
- Fixed column references (`company_name` → `customer_name`)

---
*Phase 1 Workflow Delivery: FULLY COMPLETE including Command Center ops view.*
