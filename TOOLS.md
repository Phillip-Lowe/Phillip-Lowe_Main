# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## Related

- [Agent workspace](/concepts/agent-workspace)

---

## Skills Database (Updated 2026-06-30)

**Location:** `~/.openclaw/skills/`
**Total:** 32 skills (all with SKILL.md)

### Recently Added (24)
From `Sol-Knowledge/tools/skills/` — discovered gap where documented skills were never installed:
- ai-consultation-orchestrator
- auto-research
- automator-runbook-generator
- booking-frontend
- catering-lead-system
- client-onboarding
- cold-email-engine
- dashboard-api
- fleet-orchestrator
- green-content-calendar
- green-email-outreach
- green-lead-scraper
- green-n8n-monitor
- invoice-pipeline
- linkedin-lead-gen-outreach
- mcporter-skill
- n8n-error-catcher
- n8n-workflow-automation
- pdf-generation
- productivity-automation-kit
- sage-lite-memory
- site-deployer
- stripe-payment-integration
- vps-provisioning

### Existing (8)
- branded-pdf-generator
- kling-ai
- local-image-gen
- local-video-gen
- local-voice-streaming
- n8n
- n8n-workflow-builder
- sol-voice-agent

### Discovery Source
Also check `Sol-Knowledge/tools/skills/` for additional skill documentation not yet installed.

---

## Credential Security (Added 2026-06-22)

### Exposed Credential Response
**Tool:** BFG Repo-Cleaner (`brew install bfg`)
**Process:**
```bash
# 1. Clone mirror
git clone --mirror https://github.com/Phillip-Lowe/systack-saas.git
cd systack-saas.git

# 2. Delete file from all history
bfg --delete-files "filename.json"

# 3. Clean reflog and garbage collect
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. Force push
git push --force
```

### .gitignore Rules (Always Active)
- `*secret*`, `*credential*`, `*token*`, `*password*`, `*api_key*`
- `*oauth*.json`, `*google*.json`, `*maps*.json`
- `credentials/`, `secrets/`, `tokens/`, `auth/` directories

### Never Commit
- Any file with "secret", "credential", "token", "password" in name
- JSON files containing OAuth configs
- API keys in any format
- Private keys (.pem, .key, .p12)

### Pre-Commit Protection
**Recommended:** `git-secrets` or `truffleHog` pre-commit hooks
**Install:** `brew install git-secrets`
**Setup per repo:**
```bash
git secrets --install
git secrets --register-aws  # or custom patterns
```

---

## BlueBubbles (iMessage Bridge)

**Status:** ✅ Working as of 2026-06-25
**Server:** http://phillips-macbook-air.tail573d57.ts.net:1234
**Phone:** +15012746231

### Delivery Config for Cron Jobs
All cron jobs that notify Green must include:
```json
"delivery": {
  "mode": "announce",
  "channel": "bluebubbles",
  "to": "+15012746231"
}
```

### Common Error (Fixed)
`"Delivering to BlueBubbles requires --to <handle|chat_guid:GUID>"`
→ Fix: Add explicit `channel` and `to` fields to delivery object.

### n8n Workflow List UI Crash — Prevention

After ANY workflow import via API or DB (not through UI Save), run:

```sql
-- Ensure timestamps
UPDATE workflow_entity SET "createdAt" = strftime('%Y-%m-%d %H:%M:%f', 'now') WHERE "createdAt" IS NULL OR "createdAt" = '';
UPDATE workflow_entity SET "updatedAt" = strftime('%Y-%m-%d %H:%M:%f', 'now') WHERE "updatedAt" IS NULL OR "updatedAt" = '';

-- Ensure activeVersionId
UPDATE workflow_entity SET activeVersionId = versionId WHERE activeVersionId IS NULL OR activeVersionId = '';

-- Clean orphans (causes NULL updatedAt on join → crashes WorkflowsView.vue)
DELETE FROM shared_workflow WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
DELETE FROM workflow_statistics WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
DELETE FROM workflow_history WHERE workflowId NOT IN (SELECT id FROM workflow_entity);
DELETE FROM workflow_publish_history WHERE workflowId NOT IN (SELECT id FROM workflow_entity);

-- Ensure published_version entries for active workflows
INSERT OR IGNORE INTO workflow_published_version (workflowId, publishedVersionId, createdAt, updatedAt)
SELECT we.id, we.versionId, COALESCE(we."createdAt", strftime('%Y-%m-%d %H:%M:%f', 'now')), COALESCE(we."updatedAt", strftime('%Y-%m-%d %H:%M:%f', 'now'))
FROM workflow_entity we WHERE we.active = 1 AND we.id NOT IN (SELECT workflowId FROM workflow_published_version);
```

**Root cause reference:** `memory/2026-07-07-n8n-workflow-list-fix.md` and `memory/2026-07-07-n8n-new-baseline.md`

---

### Media File Access Fix (2026-07-11)

**Problem:** TTS-generated audio files in `~/.openclaw/media/outbound/` show "Outside allowed folders" error when served.

**Root Cause:** OpenClaw's media serving restricts access to workspace paths only (`tools.fs.workspaceOnly`). Files in the global `media/outbound/` directory are outside this boundary.

**Fix Applied:**
```bash
# Create symlink from workspace media to outbound directory
rm -rf ~/.openclaw/workspaces/sol/media
ln -s ~/.openclaw/media/outbound ~/.openclaw/workspaces/sol/media
```

**Result:** `~/.openclaw/workspaces/sol/media` → `~/.openclaw/media/outbound`

**For Future TTS Files:** After generating TTS audio, reference files via workspace path:
- `MEDIA:~/.openclaw/workspaces/sol/media/voice-<timestamp>---<uuid>.mp3`

Or ensure files are copied/symlinked to workspace media before sending.

---

## n8n Database Cleanup After Workflow Deletion

After deleting ANY workflow from `workflow_entity`, clean ALL related tables:

```sql
-- Clean top-down to avoid FK RESTRICT errors
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
-- Verify
SELECT COUNT(*) FROM pragma_foreign_key_check(); -- Should be 0
```

**Failure to clean orphans causes:**
- Blank workflow list UI (`e.updatedAt.toString` crash)
- "Conflicting webhook path" errors on new workflows
- FK constraint failures when publishing/activating workflows
- Bloated database (14,200+ orphans accumulated in this session)

**Reference:** `memory/2026-07-07-n8n-new-baseline.md`

---

### When BlueBubbles Breaks
- Check server is running: `brew services list | grep bluebubbles`
- Server URL must be reachable (Tailscale or localhost)
- If disabled in config: update `openclaw.json` → `channels.bluebubbles.enabled = true`

### Admin PIN (Rotated 2026-07-07)
- **Value:** `46097565`
- **Saved to:** `~/.openclaw/workspaces/sol/.admin-pin`
- **Used for:** Command Center (8770) + Customer Portal (8768) admin access
- **Old PIN `1234`:** REJECTED — no longer valid

### SAOS_INTERNAL_API_KEY (Rotated 2026-07-06)
- **Value:** 64-char hex, stored in `.env` + `.zshrc`
- **Old dev key:** Removed from all code (no fallback)

---

## Git Repos

| Repo | URL | Purpose |
|------|-----|---------|
| systack (workspace) | `origin` | Main workspace, agent configs |
| systack-saas | `systack-saas` | SAOS product codebase |

**⚠️ systack-saas contains PUBLIC history** — never commit credentials there.

---

## Incident Response Contacts

| Service | Where to Rotate | What to Check |
|---------|----------------|---------------|
| Google OAuth | cloud.google.com → APIs & Services → Credentials | Client ID: `964526683104-eij4huqs16t72irn6eg129h1gsgbbsl4` |
| Google Maps API | Same console, API Keys section | Check billing for unauthorized usage |
| n8n | n8n.systack.net → Settings → API | Update webhook/credential configs |

---

## SAOS Documentation Pipeline

**Location:** `~/.openclaw/skills/branded-pdf-generator/`
**Script:** `scripts/generate_pdf.py`
**Stack:** pandoc (MD→HTML) + pyppeteer/Chromium (HTML→PDF)

### Usage
```bash
# Single file
python3 ~/.openclaw/skills/branded-pdf-generator/scripts/generate_pdf.py input.md output.pdf --title "Title"

# All SAOS docs
cd ~/.openclaw/workspaces/sol/Systack/content/saos/saos-data/customer-dashboard
for md in SAOS-*.md; do
  pdf="${md%.md}.pdf"
  python3 ~/.openclaw/skills/branded-pdf-generator/scripts/generate_pdf.py "$md" "$pdf"
done
```

### Document Version Matrix
| Document | Current MD | Current PDF | Pages | Audience |
|----------|-----------|-------------|-------|----------|
| Quick Start Guide | **v7.0** | **v7.0** | 5 | Client |
| Dashboard User Guide | **v6.0** | **v6.0** | 10 | Client |
| Service Manual | **v7.0** | **v7.0** | 10 | Client |
| Architecture Overview | **v5.0** | **v5.0** | 10 | Internal |
| Mobile Access Guide | **v4.0** | **v4.0** | 7 | Client |
| Enterprise Deployment | — | v1.0 | 4 | Enterprise/Private |
| Dashboard Technical Spec | — | v1.0 | 8 | Internal |
| iOS Cert Trust Plan | — | v1.0 | 6 | Internal |
| Changelog (Jun 29) | — | v1.0 | 4 | Internal |
| Customer Portal README | — | v2.0 | 4 | Internal |
| Security Architecture | **v2.0** | **v2.0** | 14 | Enterprise/Private |
| Compliance Trust Center | **v1.0** | **v1.0** | 4 | Public |
| Backup & Recovery Guide | **v1.0** | **v1.0** | 5 | Internal |

### Dashboard Doc Routes (api.py)
- `/download/quickstart-v7` → Quick Start v7.0
- `/download/user-guide-v6` → User Guide v6.0
- `/download/manual-v7` → Service Manual v7.0
- `/download/architecture-v5` → Architecture v5.0 (internal)
- `/download/mobile-guide-v4` → Mobile Guide v4.0
- `/download/enterprise-guide` → Enterprise Deployment v1.0
- `/download/technical-spec` → Dashboard Technical Spec
- `/download/ios-cert-plan` → iOS Cert Trust Plan
- `/download/changelog` → Changelog (Jun 29)
- `/download/readme` → Customer Portal README v2
- `/download/security-arch` → Security Architecture v2.0
- `/download/trust-center` → Compliance Trust Center v1.0
- `/download/backup-recovery` → Backup & Recovery Guide v1.0
- *(Backward compat: `/download/user-guide-v5` → User Guide v6.0, `/download/mobile-guide-v3` → Mobile Guide v4.0, `/download/security-arch-v1` → Security Architecture v1.0)*

### Known Issues
- pyppeteer Chromium often fails on macOS — script falls back to Brave Browser
- If Brave also fails: `brew install --cask google-chrome`
