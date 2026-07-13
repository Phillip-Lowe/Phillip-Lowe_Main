# 2026-07-07 05:26 CDT — n8n Full Cleanup & Workflow Import (NEW BASELINE)

## Status: ✅ COMPLETE — New n8n Baseline

## What Was Done

### 1. n8n Workflow List UI Fix (04:39 CDT)
Fixed blank workflow list page (`TypeError: null is not an object (evaluating 'e.updatedAt.toString')` at `WorkflowsView.vue:372`).

**Root causes found and fixed:**
- 6 orphaned `shared_workflow` entries pointing to deleted workflows
- 4 SAOS workflows with NULL `createdAt`/`updatedAt` (inserted via API without timestamps)
- 7 active workflows missing `workflow_published_version` entries
- 93 orphaned `workflow_statistics`, 6 `workflow_history`, 18 `workflow_publish_history` entries

Reference: `memory/2026-07-07-n8n-workflow-list-fix.md`

### 2. SAOS Workflow JSON Build (04:53 CDT)
Assembly (deepseek-v4-pro) built 7 complete SAOS workflow JSON files from Oracle's specs.

**Files:** `Systack/content/saos/saos-data/n8n-workflows-v2/`

| Workflow | Nodes | Trigger |
|----------|-------|---------|
| SAOS Chat Bridge | 7 | Webhook `saos-chat-bridge` |
| SAOS Customer Support Drafting | 7 | Schedule every 5 min |
| SAOS Document Classification Engine | 9 | Webhook `saos-doc-uploaded` |
| SAOS Scheduled Report Generator | 7 | Schedule daily 8 AM CT |
| SAOS Email Notification Dispatcher | 8 | Schedule every 60s |
| SAOS Enterprise Configure Fleet | 9 | Webhook `saos-fleet-config` |
| SAOS VPS Ready Notification | 7 | Webhook `saos-vps-ready` |

**Total:** 54 nodes across 7 workflows. All validated: unique UUIDs, positive positions, valid connections, retry policies on HTTP nodes.

### 3. Import & Database Cleanup (05:26 CDT)

**n8n CLI import failed** with `SQLITE_CONSTRAINT: NOT NULL constraint failed: workflow_entity.id` — n8n 2.20.7-exp import doesn't auto-generate workflow IDs. Workflows were inserted directly via SQL instead.

**Old skeleton workflows deleted:** 7 (Chat Bridge, Customer Support Drafting, Document Classification, Scheduled Report Generator, Email Dispatcher, Configure Fleet, VPS Ready)

**Orphaned webhook_entity entries deleted:** 5 (pointing to deleted workflows, causing "conflicting webhook path" errors)

**Massive FK cleanup (14,200+ records):**

| Table | Orphans Deleted |
|-------|-----------------|
| `execution_entity` | 6,538 |
| `execution_data` | 6,538 |
| `workflow_dependency` | 214 |
| `insights_metadata` | 5 |
| `insights_by_period` | 604 |
| `insights_raw` | 303 |
| `webhook_entity` | 5 |
| `shared_workflow` | 6 |
| `workflow_statistics` | 93 |
| `workflow_history` | 6 |
| `workflow_publish_history` | 18 |
| **Total** | **~14,200** |

**workflow_history entries created:** 7 (for new SAOS workflows — needed for FK from `workflow_published_version`)

**FK violations after cleanup:** 0

### 4. Final State — n8n Baseline (05:26 CDT)

| Metric | Value |
|--------|-------|
| Total workflows | 60 |
| SAOS workflows | 10 |
| Active SAOS workflows | 1 (Lead Capture) |
| Inactive SAOS workflows | 9 (all new + existing skeletons) |
| FK violations | 0 |
| n8n version | 2.20.7-exp.0 |
| Database | SQLite (`~/.n8n/database.sqlite`) |
| n8n PID | 18268 |
| HTTP status | 200 |

### SAOS Workflow Status (All Baseline)

| Workflow | Nodes | Active | Notes |
|----------|-------|--------|-------|
| SAOS Lead Capture + Score + Log | 4 | ✅ | Original, working |
| SAOS Client Provisioning Pipeline | 8 | ❌ | Original skeleton, deferred |
| SAOS Enterprise — Stripe Checkout Webhook | 5 | ❌ | Original skeleton, deferred |
| SAOS Chat Bridge | 7 | ❌ | **NEW v2** — ready to activate |
| SAOS Customer Support Drafting | 7 | ❌ | **NEW v2** — ready to activate |
| SAOS Document Classification Engine | 9 | ❌ | **NEW v2** — ready to activate |
| SAOS Scheduled Report Generator | 7 | ❌ | **NEW v2** — ready to activate |
| SAOS Email Notification Dispatcher | 8 | ❌ | **NEW v2** — ready to activate |
| SAOS Enterprise Configure Fleet | 9 | ❌ | **NEW v2** — ready to activate |
| SAOS VPS Ready Notification | 7 | ❌ | **NEW v2** — ready to activate |

### Key Lessons

1. **n8n CLI import is broken in 2.20.7-exp** — doesn't auto-generate workflow IDs. Use direct SQL insert instead.
2. **Orphaned records accumulate fast** — every deleted workflow leaves orphans in `execution_entity`, `execution_data`, `webhook_entity`, `workflow_statistics`, `workflow_history`, `workflow_publish_history`, `workflow_published_version`, `workflow_dependency`, `insights_metadata`, `insights_by_period`, `insights_raw`. Run the cleanup SQL after ANY workflow deletion.
3. **workflow_history entries are required** — `workflow_published_version.publishedVersionId` has an FK RESTRICT to `workflow_history.versionId`. When inserting workflows via SQL, you must create matching `workflow_history` entries.
4. **webhook_entity entries persist after workflow deletion** — must be manually cleaned or they cause "conflicting webhook path" errors.
5. **FK violations cascade** — `execution_data` references `execution_entity`, `insights_by_period`/`insights_raw` reference `insights_metadata`. Clean top-down.

### Prevention SQL (run after ANY workflow deletion)

```sql
-- Clean all orphaned FK references
DELETE FROM execution_data WHERE executionId NOT IN (SELECT id FROM execution_entity);
DELETE FROM execution_entity WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
DELETE FROM webhook_entity WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
DELETE FROM workflow_dependency WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
DELETE FROM workflow_published_version WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
DELETE FROM workflow_history WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
DELETE FROM workflow_publish_history WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
DELETE FROM workflow_statistics WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
DELETE FROM shared_workflow WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
DELETE FROM insights_by_period WHERE metaId NOT IN (SELECT metaId FROM insights_metadata);
DELETE FROM insights_raw WHERE metaId NOT IN (SELECT metaId FROM insights_metadata);
DELETE FROM insights_metadata WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
```

### Prevention SQL (run after ANY workflow import via SQL)

```sql
-- Ensure timestamps
UPDATE workflow_entity SET "createdAt" = strftime('%Y-%m-%d %H:%M:%f', 'now') WHERE "createdAt" IS NULL OR "createdAt" = '';
UPDATE workflow_entity SET "updatedAt" = strftime('%Y-%m-%d %H:%M:%f', 'now') WHERE "updatedAt" IS NULL OR "updatedAt" = '';

-- Ensure activeVersionId
UPDATE workflow_entity SET activeVersionId = versionId WHERE activeVersionId IS NULL OR activeVersionId = '';

-- Ensure shared_workflow entries
INSERT OR IGNORE INTO shared_workflow (workflowId, projectId, role, "createdAt", "updatedAt")
SELECT we.id, 'yXbqdfXQYS5El7Nb', 'workflow:owner',
  COALESCE(we."createdAt", strftime('%Y-%m-%d %H:%M:%f', 'now')),
  COALESCE(we."updatedAt", strftime('%Y-%m-%d %H:%M:%f', 'now'))
FROM workflow_entity we
WHERE we.id NOT IN (SELECT workflowId FROM shared_workflow);

-- Ensure published_version entries
INSERT OR IGNORE INTO workflow_published_version (workflowId, publishedVersionId, createdAt, updatedAt)
SELECT we.id, we.versionId,
  COALESCE(we."createdAt", strftime('%Y-%m-%d %H:%M:%f', 'now')),
  COALESCE(we."updatedAt", strftime('%Y-%m-%d %H:%M:%f', 'now'))
FROM workflow_entity we
WHERE we.id NOT IN (SELECT workflowId FROM workflow_published_version);

-- Ensure workflow_history entries (FK from published_version)
INSERT OR IGNORE INTO workflow_history (versionId, workflowId, authors, "createdAt", "updatedAt", nodes, connections, name, autosaved, description)
SELECT we.versionId, we.id, 'system',
  COALESCE(we."createdAt", strftime('%Y-%m-%d %H:%M:%f', 'now')),
  COALESCE(we."updatedAt", strftime('%Y-%m-%d %H:%M:%f', 'now')),
  we.nodes, we.connections, we.name, 0, NULL
FROM workflow_entity we
WHERE we.versionId NOT IN (SELECT versionId FROM workflow_history);

-- Verify FK integrity
SELECT COUNT(*) FROM pragma_foreign_key_check();
-- Should return 0
```

## Files

| File | Location |
|------|----------|
| 7 workflow JSON files | `Systack/content/saos/saos-data/n8n-workflows-v2/` |
| Workflow list fix log | `memory/2026-07-07-n8n-workflow-list-fix.md` |
| This baseline | `memory/2026-07-07-n8n-new-baseline.md` |

## Related

- `memory/2026-07-07-n8n-workflow-list-fix.md` — UI blank fix
- `memory/2026-07-07-pre-deploy-audit.md` — full systems audit
- `memory/2026-06-30-n8n-workflow-visibility-fix.md` — previous activeVersionId fix
- `memory/2026-07-01-0526-n8n-nuclear-recovery.md` — full n8n recovery