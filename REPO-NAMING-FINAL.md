# REPO NAMING — FINAL STATE (2026-06-23)

## GitHub Repos (User Renamed)

| Repo Name | What It Is | URL |
|-----------|-----------|-----|
| **Phillip-Lowe_Main** | Main workspace (was `systack`, then `utopia-deli-order`) | https://github.com/Phillip-Lowe/Phillip-Lowe_Main |
| **Systack-SAOS** | Backend scripts/provisioning (was `systack-saas`) | https://github.com/Phillip-Lowe/Systack-SAOS |
| **systack** | Business website (systack.net) (was `systack-site`) | https://github.com/Phillip-Lowe/systack |
| **utopia-deli** | Deli-only content | https://github.com/Phillip-Lowe/utopia-deli |

## Local Workspace Remotes

| Remote | Points To |
|--------|-----------|
| `origin` | https://github.com/Phillip-Lowe/Phillip-Lowe_Main.git |
| `systack-saas` | https://github.com/Phillip-Lowe/Systack-SAOS.git |

## What Goes Where

### Phillip-Lowe_Main (origin)
- Everything: SAOS, business, deli content, workspace files
- This is your main monorepo

### Systack-SAOS (systack-saas remote)
- Backend scripts: provisioning, deployment, automation
- Kept separate for clean architecture

### systack (separate repo, no local clone yet)
- Website files: HTML, CSS, assets for systack.net
- Clone locally if you need to edit the business site

### utopia-deli (separate repo, no local clone yet)
- Deli-specific content only
- Already exists, can clone if needed

## Local Directory Structure

```
/Users/philliplowe/.openclaw/workspaces/sol/
├── .git/                           # Git root for Phillip-Lowe_Main
├── AGENTS.md, MEMORY.md, etc.     # Workspace config
├── Systack/                        # SAOS + business systems
│   ├── content/
│   │   ├── saos/                   # SAOS backend code
│   │   ├── systack-site/           # Website files (systack.net)
│   │   └── ...
│   └── ...
├── The Utopia Deli/                # Deli content
├── scripts/                        # Automation scripts
├── memory/                         # Session logs
└── ...
```

## Next Steps

1. ✅ Remotes updated
2. ⏳ Verify `git push origin main` works when ready
3. ⏳ Clone `systack` repo locally if editing website
4. ⏳ Clone `utopia-deli` repo if separating deli content

## Important

- GitHub redirects old repo names automatically
- Old URLs still work (e.g., `github.com/Phillip-Lowe/systack` redirects to `Phillip-Lowe_Main`)
- No data was lost in any rename
- Your commits are safe in `Phillip-Lowe_Main`
