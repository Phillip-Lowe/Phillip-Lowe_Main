# Systack Site — Deploy Notes

## ⚠️ CRITICAL: Where the site actually lives

The live site `systack.net` is deployed from:
**Repo:** `Phillip-Lowe/systack`  
**URL:** https://github.com/Phillip-Lowe/systack

This workspace has the source files at:
`Systack/content/systack-site/`

But GitHub Pages is NOT enabled on `Phillip-Lowe_Main` — it's enabled on `Phillip-Lowe/systack`.

## How to deploy changes

After editing files in `Systack/content/systack-site/`, run:

```bash
./scripts/sync-site.sh
```

Or preview first:
```bash
./scripts/sync-site.sh --dry-run
```

## Why two repos?

- `Phillip-Lowe_Main` = workspace repo (all projects, code, memory)
- `Phillip-Lowe/systack` = deploy repo (only site files, GitHub Pages enabled)

The workspace repo is large and has GitHub Actions disabled for Pages. The deploy repo is lightweight and serves the site.

## CNAME

Both repos have `CNAME` with `systack.net`. The deploy repo's CNAME is what actually matters for GitHub Pages routing. The workspace CNAME is copied over by the sync script to keep them consistent.

Last updated: 2026-07-07
