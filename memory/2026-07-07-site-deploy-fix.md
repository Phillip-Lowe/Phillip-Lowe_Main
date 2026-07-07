# Systack Site Deploy Fix — 2026-07-07 00:12 CDT

## Problem
User updated site files in workspace (`Systack/content/systack-site/`) but live site at `systack.net` still showed old version with "Personal Agent" link and "Stop Handling Bookings..." hero text.

## Root Cause
- Live site `systack.net` is served from **`Phillip-Lowe/systack` repo** (GitHub Pages enabled)
- Workspace edits were in `Phillip-Lowe_Main` repo (`Systack/content/systack-site/`)
- Both repos had CNAME = `systack.net` causing confusion
- Pages is NOT enabled on `Phillip-Lowe_Main` (API returned 404)

## Solution
1. Cloned `Phillip-Lowe/systack` repo to `/tmp/systack-deploy`
2. Copied current site files from workspace to deploy repo root
3. Committed and pushed to `Phillip-Lowe/systack`
4. GitHub Pages rebuilt and deployed

## Files Changed in Deploy Repo
- `index.html` — "Your Business. Systemized." (was "Stop Handling Bookings...")
- Removed "Personal Agent" nav links
- Updated `pricing.html`, `services.html`, `contact.html`
- Updated `services/`, `work/`, `saos/`, `saos-landing/`, `case-studies/` directories

## Prevention Measures
1. **CNAME** — Added back to workspace with comment explaining deploy repo
2. **DEPLOY.md** — Document explaining the two-repo setup
3. **sync-site.sh** — Script at `scripts/sync-site.sh` to sync workspace → deploy repo
   - Usage: `./scripts/sync-site.sh` or `./scripts/sync-site.sh --dry-run`

## Verification
```bash
curl -s https://systack.net | grep "Your Business"
# ✅ Returns: <h1>Your Business.<br>Systemized.</h1>

curl -s https://systack.net | grep "Personal Agent"
# ✅ Returns nothing (link removed)
```

## Deploy Repo
- **URL:** https://github.com/Phillip-Lowe/systack
- **CNAME:** systack.net
- **Pages:** Enabled, builds from `main` branch root

## Workspace Source
- **Path:** `Systack/content/systack-site/`
- **Repo:** Phillip-Lowe_Main
- **Pages:** NOT enabled (source of previous confusion)
