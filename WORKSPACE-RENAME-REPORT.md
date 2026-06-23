# WORKSPACE RENAME REPORT — 2026-06-23

## What Was Changed

### GitHub Repos Renamed

| Old Name | New Name | Serves | CNAME |
|----------|----------|--------|-------|
| `systack` | `utopia-deli-order` | `order.theutopiadeli.com` | `order.theutopiadeli.com` |
| `systack-site` | `systack` | `systack.net` | `systack.net` |

### Why
The repo names were backwards:
- `systack` was serving the deli ordering site
- `systack-site` was serving the business site

This caused confusion — we kept pushing changes to the wrong repo.

## Local Workspace Structure

**IMPORTANT:** Your local workspace is ONE git repo:
- **Root:** `/Users/philliplowe/.openclaw/workspaces/sol`
- **Origin:** `https://github.com/Phillip-Lowe/utopia-deli-order.git` (was `systack`)

**Directories:**
- `Systack/content/systack-site/` — Website files (HTML/CSS) for systack.net
- `Systack/content/saos/` — SAOS backend code
- `The Utopia Deli/` — Deli content
- `Systack/content/systack-stack/` — Infrastructure

**Note:** The local `systack-site` directory is NOT the same as the GitHub `systack-site` repo (now renamed to `systack`). It's just a directory inside your monorepo.

## What Was Committed

All 25 uncommitted changes were saved in commit `7bbfbd2`:
- Email campaign files
- Utopia Deli updates
- SAOS provisioning scripts

## Next Steps

1. ✅ GitHub repos renamed
2. ✅ Local remote updated to `utopia-deli-order`
3. ✅ Uncommitted changes saved
4. ⏳ Verify systack.net shows updated content (GitHub Pages rebuild triggered)
5. ⏳ Test Stripe → onboard flow when you're back

## Naming Convention Going Forward

| Repo | Purpose | Local Path |
|------|---------|------------|
| `utopia-deli-order` | Main workspace monorepo | `/Users/philliplowe/.openclaw/workspaces/sol` |
| `systack` | Business website (systack.net) | No local clone yet |
| `systack-saas` | Backend scripts | Remote only |

**Rule:** If you're editing website files for systack.net, make sure you're pushing to `Phillip-Lowe/systack` repo, NOT the local workspace.
