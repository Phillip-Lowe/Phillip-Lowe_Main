# 2026-07-07 04:39 CDT — n8n Workflow List UI Blank (FIXED — Root Cause Found)

## Problem

n8n workflow list page (`/workflows`) was blank — no workflows rendered. Browser console showed:

```javascript
TypeError: null is not an object (evaluating 'e.updatedAt.toString')
```

Location: `WorkflowsView.vue:372`

## Root Cause (DEFINITIVE)

**Three separate issues, all causing the same Vue render crash:**

### Issue 1: Orphaned `shared_workflow` entries (6 records)
6 `shared_workflow` records pointed to deleted workflows. The API joined these to `workflow_entity`, got NULL `updatedAt` back, and the Vue list renderer crashed.

### Issue 2: NULL `createdAt`/`updatedAt` on 4 SAOS workflows
The 4 SAOS workflows built on June 30 (Chat Bridge, Customer Support Drafting, Document Classification Engine, Scheduled Report Generator) were inserted via API/DB without proper timestamps. The DB stored them as NULL, and the n8n CLI export confirmed `updatedAt=None`.

**Affected workflows:**
- `0c6f9147-ae52-45a2-87f1-79b339a5e5bd` — SAOS Chat Bridge
- `61be935f-fdbd-4d26-b7ff-27491e47aab5` — SAOS Customer Support Drafting
- `7814e383-1d1a-4111-9c2c-2350cb4b7730` — SAOS Document Classification Engine
- `f3b106b0-fb3d-48b1-9994-208bb53a2fef` — SAOS Scheduled Report Generator

### Issue 3: Missing `workflow_published_version` entries (7 active workflows)
7 active workflows had no entry in `workflow_published_version` table. The API uses this table to resolve version metadata. Without an entry, the API returned null for version-related fields.

### Issue 4: Orphaned records across 3 tables
- 93 orphaned `workflow_statistics` entries (pointing to deleted workflows)
- 6 orphaned `workflow_history` entries
- 18 orphaned `workflow_publish_history` entries

## Fix Applied

```sql
-- 1. Delete orphaned shared_workflow entries
DELETE FROM shared_workflow 
WHERE workflowId NOT IN (SELECT id FROM workflow_entity);

-- 2. Fix NULL timestamps on 4 SAOS workflows
UPDATE workflow_entity 
SET "updatedAt" = strftime('%Y-%m-%d %H:%M:%f', 'now'),
    "createdAt" = strftime('%Y-%m-%d %H:%M:%f', 'now')
WHERE id IN (
  '0c6f9147-ae52-45a2-87f1-79b339a5e5bd',
  '61be935f-fdbd-4d26-b7ff-27491e47aab5',
  '7814e383-1d1a-4111-9c2c-2350cb4b7730',
  'f3b106b0-fb3d-48b1-9994-208bb53a2fef'
);

-- 3. Create missing workflow_published_version entries for active workflows
INSERT INTO workflow_published_version (workflowId, publishedVersionId, createdAt, updatedAt)
SELECT we.id, we.versionId,
  COALESCE(we."createdAt", strftime('%Y-%m-%d %H:%M:%f', 'now')),
  COALESCE(we."updatedAt", strftime('%Y-%m-%d %H:%M:%f', 'now'))
FROM workflow_entity we
LEFT JOIN workflow_published_version wpv ON we.id = wpv.workflowId
WHERE wpv.workflowId IS NULL AND we.active = 1;

-- 4. Clean orphaned statistics/history
DELETE FROM workflow_statistics WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
DELETE FROM workflow_history WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
DELETE FROM workflow_publish_history WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
```

Then restart n8n:
```bash
pkill -f "n8n start"
nohup ~/.n8n/start-n8n.sh > /dev/null 2>&1 &
```

## Verification

- CLI export: 60/60 workflows with valid timestamps ✅
- Browser: Workflow list renders correctly ✅ (confirmed by user 04:39 CDT)

## Key Lesson

**The `e.updatedAt.toString()` crash has multiple possible causes, not just NULL `updatedAt` in `workflow_entity`:**

1. **NULL timestamps in `workflow_entity`** — workflows inserted via API/DB without timestamps
2. **Orphaned `shared_workflow` entries** — deleted workflows leave orphaned records that return NULLs on join
3. **Missing `workflow_published_version` entries** — active workflows without published version records
4. **Orphaned records in related tables** — `workflow_statistics`, `workflow_history`, `workflow_publish_history`

### Diagnosis Checklist (in order)

1. Check `workflow_entity` for NULL `updatedAt`/`createdAt`:
   ```sql
   SELECT id, name FROM workflow_entity WHERE "updatedAt" IS NULL OR "createdAt" IS NULL;
   ```

2. Check for orphaned `shared_workflow` entries:
   ```sql
   SELECT sw.workflowId FROM shared_workflow sw 
   LEFT JOIN workflow_entity we ON sw.workflowId = we.id 
   WHERE we.id IS NULL;
   ```

3. Check for active workflows missing `workflow_published_version`:
   ```sql
   SELECT we.id, we.name FROM workflow_entity we
   LEFT JOIN workflow_published_version wpv ON we.id = wpv.workflowId
   WHERE we.active = 1 AND wpv.workflowId IS NULL;
   ```

4. Check for orphaned records in related tables:
   ```sql
   SELECT COUNT(*) FROM workflow_statistics WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
   SELECT COUNT(*) FROM workflow_history WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
   SELECT COUNT(*) FROM workflow_publish_history WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
   ```

5. Use n8n CLI export to verify what the API would return:
   ```bash
   n8n export:workflow --all --output=/tmp/check.json
   python3 -c "import json; ws=json.load(open('/tmp/check.json')); [print(f'❌ {w[\"name\"]}: updatedAt={w.get(\"updatedAt\")}') for w in ws if not w.get('updatedAt')]"
   ```

### Prevention

After ANY workflow import via API or DB (not through UI Save), run:

```sql
-- Ensure timestamps
UPDATE workflow_entity SET "createdAt" = strftime('%Y-%m-%d %H:%M:%f', 'now') WHERE "createdAt" IS NULL OR "createdAt" = '';
UPDATE workflow_entity SET "updatedAt" = strftime('%Y-%m-%d %H:%M:%f', 'now') WHERE "updatedAt" IS NULL OR "updatedAt" = '';

-- Ensure activeVersionId
UPDATE workflow_entity SET activeVersionId = versionId WHERE activeVersionId IS NULL OR activeVersionId = '';

-- Ensure shared_workflow entries exist
INSERT OR IGNORE INTO shared_workflow (workflowId, projectId, role, createdAt, updatedAt)
SELECT we.id, 'yXbqdfXQYS5El7Nb', 'workflow:owner', 
  COALESCE(we."createdAt", strftime('%Y-%m-%d %H:%M:%f', 'now')),
  COALESCE(we."updatedAt", strftime('%Y-%m-%d %H:%M:%f', 'now'))
FROM workflow_entity we
WHERE we.id NOT IN (SELECT workflowId FROM shared_workflow);

-- Ensure published_version entries for active workflows
INSERT OR IGNORE INTO workflow_published_version (workflowId, publishedVersionId, createdAt, updatedAt)
SELECT we.id, we.versionId,
  COALESCE(we."createdAt", strftime('%Y-%m-%d %H:%M:%f', 'now')),
  COALESCE(we."updatedAt", strftime('%Y-%m-%d %H:%M:%f', 'now'))
FROM workflow_entity we
WHERE we.active = 1 AND we.id NOT IN (SELECT workflowId FROM workflow_published_version);

-- Clean orphans
DELETE FROM shared_workflow WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
DELETE FROM workflow_statistics WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
DELETE FROM workflow_history WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
DELETE FROM workflow_publish_history WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
```

## Related

- `memory/2026-06-30-n8n-workflow-visibility-fix.md` — previous fix (activeVersionId NULL)
- `memory/2026-06-05-v2-empty-fix.md` — earlier instance (activeVersionId NULL)
- `memory/2026-06-05-v2-add-first-step-fix.md` — node ID issue
- `memory/2026-06-05-v2-empty-attempt2.md` — negative coordinates issue
- `memory/2026-07-01-0526-n8n-nuclear-recovery.md` — full n8n recovery