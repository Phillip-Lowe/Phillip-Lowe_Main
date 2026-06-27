# Path Prefix Cascade Lesson — 2026-06-25 06:12 CDT

## What Happened

When fixing the SAOS dashboard mobile access issue, we moved OpenClaw's Control UI from the root path (`/`) to `/openclaw/` by setting `gateway.controlUi.basePath: "/openclaw"`.

This fixed the original problem (Control UI scripts intercepting PDF link clicks), but it created a new problem: **relative URLs in the dashboard broke.**

## The Breakage

PDF links in the dashboard were coded as:
```javascript
{ url: '/download/mobile-guide' }
```

When the browser was at `https://host/dashboard/`, it resolved to:
```
https://host/download/mobile-guide  ← WRONG (Not Found)
```

Instead of:
```
https://host/dashboard/download/mobile-guide  ← CORRECT
```

## Why It Happened

The `basePath` change altered how OpenClaw served its static files, which in turn affected how the browser resolved relative URLs on the same origin. Even though `/dashboard/` is proxied separately by Tailscale serve, the browser's URL resolution uses the current page's origin + the relative path.

## The Fix

Changed all relative URLs to include the `/dashboard/` prefix:
```javascript
{ url: '/dashboard/download/mobile-guide' }
```

Also applied the same lesson to `API_BASE` earlier in the session:
```javascript
const API_BASE = window.location.pathname.startsWith('/dashboard') ? '/dashboard' : '';
```

## The Rule

**When you change `basePath`, add a reverse proxy prefix, or serve an app behind a path prefix, ALL relative URLs in that app must be updated.**

This includes:
- `fetch('/api/...')` → `fetch('/dashboard/api/...')` or dynamic detection
- `<a href="/download/...">` → `<a href="/dashboard/download/...">`
- WebSocket connections
- Static asset references
- Client-side routing

**Prevention:** Use runtime path detection or absolute URLs with full prefixes. Never assume relative paths will resolve correctly.
