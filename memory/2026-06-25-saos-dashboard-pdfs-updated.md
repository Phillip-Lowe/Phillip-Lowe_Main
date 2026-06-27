# 2026-06-25 — SAOS Dashboard v2.1: Complete PDF Documentation Update + Doc Link Fix

## What Was Done

### PDF Documentation — All Updated

| PDF | Version | Pages | Status |
|-----|---------|-------|--------|
| Quick Start Guide | v5.0 | 4 pages | ✅ NEW — PIN auth, onboarding, 7 tabs |
| Dashboard User Guide | v3.0 | 7 pages | ✅ NEW — Complete feature reference |
| Service Manual | v5.0 | 7 pages | ✅ NEW — DB schema, auth flow, troubleshooting |
| Architecture Overview | v4.0 | 7 pages | ✅ NEW — API endpoints, system architecture |
| Mobile Access Guide | v2.0 | 4 pages | ✅ NEW — iPhone/Android Tailscale + home screen shortcuts |

All PDFs have source markdowns for future updates.

### PDF Doc Link Fix

**Problem:** Clicking doc cards opened `target="_blank"` which:
- Lost Tailscale session context
- New tab hit login screen (catch-all route served index.html)
- Login in new tab failed with "string int connected" error

**Solution:** Changed doc cards from `<a href target="_blank">` to `<div onclick="downloadDoc()">`:
```javascript
async function downloadDoc(url, filename) {
    const res = await fetch(url);
    const blob = await res.blob();
    const blobUrl = URL.createObjectURL(blob);
    window.open(blobUrl, '_blank');  // Opens in new tab, blob URL works without Tailscale
    setTimeout(() => URL.revokeObjectURL(blobUrl), 30000);
}
```

**Why it works:**
- `fetch()` runs in authenticated dashboard tab
- `URL.createObjectURL(blob)` creates local blob URL
- Blob URL opens in new tab without needing Tailscale auth
- PDF displays inline for viewing, auto-cleans up after 30s

### Commits
- `9b9fac6` — SAOS Dashboard v2.1: Complete UX overhaul + updated PDFs
- `fb39694` — SAOS Dashboard v2.1: Complete PDF documentation update
- `b1c1a8c` — SAOS Dashboard: Fix PDF doc links — fetch blob + window.open

## Files Created/Modified
- `SAOS-Quick-Start-Guide-v5.0.md` + `.pdf`
- `SAOS-Dashboard-User-Guide-v3.0.md` + `.pdf`
- `SAOS-Service-Manual-v5.0.md` + `.pdf`
- `SAOS-Architecture-Overview-v4.0.md` + `.pdf`
- `SAOS-Dashboard-Mobile-Access-Guide-v2.0.md` + `.pdf`
- `index.html` — Updated docs tab + downloadDoc function
- `api.py` — Updated /download/ routes for v5.0/v3.0/v4.0/v2.0