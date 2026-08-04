# Utopia Deli Meal Prep Pause — 2026-08-04 18:18 CDT

**Session:** SOL (WebChat direct)
**User:** Green
**Status:** ✅ COMPLETE

---

## What Happened

Green needed to temporarily disable the Utopia Deli meal prep/catering page while the deli partners are away at an event. The main pickup-order page should remain live.

## Actions Taken

### 1. n8n Workflow (Initially Misunderstood)
- Unpublished `Utopia-Deli-Simple-Checkout-v4` (id: `9e21e791-58cd-4255-89f1-2cdb472af701`) in n8n
- Green clarified: unpublish the **website page**, not the workflow
- Workflow was NOT re-published — Green will handle that

### 2. Website Page Pause (Correct Action)

**Source repo:** `Phillip-Lowe/Phillip-Lowe_Main.git` (GitHub Pages site)
**Live URL:** https://www.theutopiadeli.com/catering/
**Local path:** `~/.openclaw/workspaces/sol/The Utopia Deli/catering/`

**Steps:**
1. Renamed `catering/index.html` → `catering/index.html.disabled` (preserved original)
2. Created temporary pause page at `catering/index.html`
3. Committed and pushed to `origin main`

**Final pause page message:**
```
🚫 Meal Prep is Temporarily Unavailable

Meal prep is currently unavailable. We apologize for any inconvenience.

[Back to Main Site]
```

**Preserved original file:** `catering/index.html.disabled`

## What Was NOT Modified

- `pickup-order/index.html` — Still live, untouched
- n8n workflow — Unpublished but Green will re-publish
- Any other site pages or files
- Database or order history

## How to Restore

### Option A: Git Revert (Recommended)
```bash
cd ~/.openclaw/workspaces/sol/The\ Utopia\ Deli
mv catering/index.html.disabled catering/index.html
git add catering/
git commit -m "RESUME: Re-enable catering/meal-prep page"
git push origin main
```

### Option B: Manual Rename + Commit
```bash
cd ~/.openclaw/workspaces/sol/The\ Utopia\ Deli
rm catering/index.html
mv catering/index.html.disabled catering/index.html
git add catering/
git commit -m "RESUME: Re-enable catering/meal-prep page from pause"
git push origin main
```

## Repeatable Task Pattern

This is now a documented operational procedure for "temporarily disable a page while preserving original":

```bash
# PAUSE a page
mv page/index.html page/index.html.disabled
cat > page/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head><title>Temporarily Unavailable</title></head>
<body style="text-align:center; padding: 50px; font-family: sans-serif;">
  <h1>🚫 [Feature] is Temporarily Unavailable</h1>
  <p>[Feature] is currently unavailable. We apologize for any inconvenience.</p>
  <a href="/">Back to Main Site</a>
</body>
</html>
EOF

# RESORE a page
mv page/index.html.disabled page/index.html
```

## Key Files

| File | Status |
|------|--------|
| `The Utopia Deli/catering/index.html` | Temporary pause page (live) |
| `The Utopia Deli/catering/index.html.disabled` | Original preserved |
| `The Utopia Deli/pickup-order/index.html` | Untouched, still live |

## Lessons / Repeatable Knowledge

1. **Repo location matters** — The deployed Utopia Deli site is in `Phillip-Lowe_Main.git`, NOT the Systack site repo. Always verify which repo serves which domain.
2. **"Unpublish" is ambiguous** — Clarify whether user means n8n workflow, website page, or both before acting.
3. **Preserve originals** — Always rename-to-disable rather than delete. Enables instant restore.
4. **GitHub Pages 404 behavior** — Renaming `index.html` and replacing with a new one is cleaner than relying on default 404 (which may not exist or may be unbranded).

## Verification Needed Next Time

Before acting on "pause the page", confirm:
- [ ] Which page URL exactly (catering? pickup? both?)
- [ ] Which system (n8n workflow vs GitHub Pages site)
- [ ] Whether to preserve original for easy restore
- [ ] What message to show users during pause
