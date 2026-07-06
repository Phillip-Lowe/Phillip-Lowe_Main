# n8n Nuclear Recovery — Complete Session Log

**Date:** 2026-07-01 05:26 CDT
**Status:** ✅ RECOVERED — All 60 workflows visible in UI
**Solution:** Fresh DB + CLI re-import

---

## Problem Statement

User reported n8n workflows not showing in UI. The workflows existed in database but appeared as empty canvas or were completely invisible in the list.

**What user saw:**
- Executions tab showed workflows still running
- Main workflows list was empty
- Could not select, edit, or view any workflows

---

## Diagnosis Timeline

### Attempt 1: activeVersionId Fix (FAILED)
- Checked `workflow_entity.activeVersionId` vs `versionId`
- Found 3 mismatches on July 1
- Fixed mismatches: `UPDATE workflow_entity SET activeVersionId = versionId WHERE activeVersionId != versionId`
- Result: Workflows still not visible

### Attempt 2: shared_workflow Fix (FAILED)
- Found 5 workflows missing from `shared_workflow` (no project assignment)
- Added entries linking to personal project
- Result: Workflows still not visible

### Attempt 3: FK Cleanup + Full Restart (FAILED)
- Cleaned 200+ orphaned foreign key references across:
  - `workflow_publish_history`
  - `workflow_history`
  - `shared_workflow`
  - `workflow_dependency`
  - `insights_metadata`
  - `insights_by_period`
- Restarted n8n with clean DB
- Result: Workflows still not visible

### Attempt 4: June 30 Backup Restore (FAILED)
- Restored June 30 06:55 clean backup
- Applied only original `activeVersionId` fix
- Result: Workflows still not visible

---

## Root Cause

**NOT a database corruption issue.**

The June 30 backup itself also had the 5 missing `shared_workflow` entries — meaning those workflows were NEVER visible through the n8n UI, only accessible via CLI or executions.

The real issue was likely a combination of:
1. n8n version-specific project/permission model (2.20.7-exp.0)
2. Workflows imported via CLI/API without proper project assignment
3. Browser cache/auth issues compounded the problem

---

## ✅ Working Solution: Nuclear Recovery

### Step 1: Export workflows via CLI
```bash
cd ~/.n8n
n8n export:workflow --all --output=/tmp/n8n-workflows-backup.json
# Result: Successfully exported 60 workflows
```

### Step 2: Fix export JSON (updatedAt bug)
n8n export JSON missing `updatedAt` field caused import failures. Fixed with Python:
```python
import json
from datetime import datetime

with open('/tmp/n8n-workflows-backup.json') as f:
    data = json.load(f)

now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
for w in data:
    if 'updatedAt' not in w or w['updatedAt'] is None:
        w['updatedAt'] = now
    if 'createdAt' not in w or w['createdAt'] is None:
        w['createdAt'] = now

with open('/tmp/n8n-workflows-import-fixed.json', 'w') as f:
    json.dump(data, f)
```

### Step 3: Create fresh database
```bash
# Stop n8n
pkill -9 -f "n8n start"
pkill -9 -f "task-runner"

# Move old DB aside
mv ~/.n8n/database.sqlite ~/.n8n/database.sqlite.before-nuclear
rm -f ~/.n8n/database.sqlite-wal ~/.n8n/database.sqlite-shm

# Start n8n (creates fresh DB)
nohup ~/.n8n/start-n8n.sh > /dev/null 2>&1 &
```

### Step 4: Import into fresh DB
```bash
# Get fresh project ID
PROJECT_ID=$(sqlite3 ~/.n8n/database.sqlite "SELECT id FROM project LIMIT 1;")

# Import with project assignment
n8n import:workflow \
  --input=/tmp/n8n-workflows-import-fixed.json \
  --projectId="$PROJECT_ID"

# Result: Successfully imported 60 workflows
```

### Step 5: Restart n8n
```bash
pkill -9 -f "n8n start"
sleep 3
nohup ~/.n8n/start-n8n.sh > /dev/null 2>&1 &
```

---

## Result

| Metric | Value |
|--------|-------|
| Workflows in DB | 60 ✅ |
| shared_workflow entries | 60 ✅ |
| FK violations | 0 ✅ |
| SAOS workflows visible | 10 ✅ |
| UI loads | ✅ |

**All workflows deactivated on import** — user must re-activate desired workflows.

---

## Files

| File | Description |
|------|-------------|
| `~/.n8n/database.sqlite.before-nuclear` | Original corrupted/pre-recovery DB |
| `~/.n8n/database.sqlite.bak.20260630_065518` | June 30 clean backup |
| `/tmp/n8n-workflows-backup.json` | Export of all 60 workflows |
| `/tmp/n8n-workflows-import-fixed.json` | Fixed export with updatedAt |

---

## Lessons

1. **Don't over-fix DB** — Multiple attempts to fix FKs/activeVersionId/shared_workflow made no difference. The issue was DB state model incompatibility with n8n's project system.
2. **CLI re-import is safest** — n8n's import handles project assignment, history, published version correctly.
3. **Export has updatedAt bug** — Must add timestamps before import.
4. **Browser cache was NOT the issue** — Multiple incognito/private attempts failed.
5. **Preserve backups** — Always keep `.before-nuclear` and `.pre-recovery` files.

---

## Prevention

After recovery:
- [ ] Re-activate critical workflows
- [ ] Export workflows weekly via cron: `n8n export:workflow --all --output=/backup/workflows-$(date +%Y%m%d).json`
- [ ] Monitor for missing shared_workflow entries
- [ ] Upgrade n8n when possible (current: 2.20.7-exp.0, outdated)

---

## User Directive

> "save everywhere and end session"

Saved to:
- `memory/2026-07-01-0526-n8n-nuclear-recovery.md`
- Referenced in MEMORY.md (to be added)
