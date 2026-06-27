# Full Session Lessons — 2026-06-25 06:14 CDT

## Session Context
Green accessed SAOS dashboard on mobile, found login was broken ("The string did not match the expected pattern" error). Session spiraled through multiple attempts before finding root causes.

---

## Lesson 1: Don't Assume Simple Errors Are Simple

**What happened:** "The string did not match the expected pattern" looked like a form validation error. Spent time on `novalidate`, button types, input patterns.

**Reality:** It was a completely different error — the API call was hitting the wrong backend service entirely because `API_BASE` was empty string, causing `fetch('/api/auth/login')` to resolve to the root Tailscale proxy (port 18789, OpenClaw) instead of the dashboard proxy (port 8768).

**Lesson:** When you see a generic error message, verify WHICH component is throwing it before fixing the obvious thing. The error was from the browser (fetch TypeError), not HTML5 validation.

---

## Lesson 2: Relative Paths + Reverse Proxies = Silent Failures

**What happened:** `const API_BASE = '';` meant all API calls used relative paths like `/api/auth/login`. With Tailscale serve proxying `/dashboard/` to port 8768, the browser resolved `/api/auth/login` relative to the origin root, not the proxy path.

**Result:** API calls went to OpenClaw (port 18789) instead of dashboard API (port 8768). 404 responses. But because OpenClaw might return HTML instead of JSON, the error manifested weirdly.

**Fix:** `const API_BASE = window.location.pathname.startsWith('/dashboard') ? '/dashboard' : '';`

**Lesson:** Any SPA served behind a path prefix MUST detect and prepend that prefix, or use absolute URLs. This is a guaranteed failure mode.

---

## Lesson 3: Don't Change Multiple Things at Once

**What happened:** While debugging the PDF issue, I simultaneously:
- Changed the `basePath` in OpenClaw config
- Modified the PDF download routes in api.py
- Updated the HTML links
- Changed from `target="_blank"` to blob downloads to iframe to direct navigation

**Result:** Broke the API entirely (duplicate route in Flask), caused "Not Found" errors, and made it impossible to tell which change caused which problem.

**Lesson:** Change ONE thing at a time. Verify it works. Then change the next thing. When you change multiple things simultaneously, you can't isolate failures.

---

## Lesson 4: Know When to Stop

**What happened:** The PDF issue was actually an architectural conflict — OpenClaw Control UI and dashboard share the same Tailscale origin. No amount of JavaScript tricks can fix that cleanly. I tried 6+ approaches (blob URLs, iframes, Web Share API, window.open, direct navigation, basePath changes) before accepting the real fix.

**Reality:** Some problems can't be worked around in code. They require config changes or architectural decisions.

**Lesson:** If you've tried 3+ approaches and none work, step back and ask: "Is this a code problem or a system architecture problem?" The answer was: move Control UI to a different path (`basePath`).

---

## Lesson 5: Path Prefixes Cascade (The Final Fix)

**What happened:** Setting `gateway.controlUi.basePath: "/openclaw"` fixed the Control UI injection on `/dashboard/`, but broke PDF links because they were relative (`/download/...` → resolved to root, not `/dashboard/`).

**Fix:** Updated all PDF links to include `/dashboard/` prefix: `/dashboard/download/mobile-guide`

**Lesson:** Path prefix changes are infectious. When you change `basePath` or add a reverse proxy prefix, you MUST audit and update ALL relative URLs in the application. No exceptions.

---

## Lesson 6: Don't Post Sensitive Data in Chat

**What happened:** Green pasted the full `openclaw.json` config including `token: "916733...b892"` in chat.

**Lesson:** Gateway tokens are sensitive. Don't paste configs in chat without redacting secrets. If exposed, rotate the token immediately.

---

## What Actually Got Fixed

1. ✅ Mobile login now works (API_BASE dynamic detection)
2. ✅ iOS form validation bypassed (button type="button")
3. ✅ Control UI no longer intercepts dashboard (basePath: "/openclaw")
4. ✅ PDF links work on mobile (absolute paths with /dashboard/ prefix)
5. ✅ Nav bar compact on mobile
6. ✅ Sidebar toggle bigger
7. ✅ Textarea placeholder shortened
8. ✅ "+ New Conversation" button in empty chat state

## What Got Broken (And Fixed)

1. ❌ Flask API crashed (duplicate static route) — fixed by removing duplicate
2. ❌ PDF links returned "Not Found" (missing /dashboard/ prefix) — fixed by adding prefix
3. ❌ Control UI temporarily inaccessible (wrong basePath format) — fixed to proper "/openclaw"

## Root Cause Summary

The entire session was a cascading failure from one architectural decision: **serving dashboard and Control UI on the same Tailscale origin without considering path prefix interactions.**

The fix required three coordinated changes:
1. Config: `gateway.controlUi.basePath: "/openclaw"`
2. Frontend: Dynamic `API_BASE` detection + absolute PDF URLs
3. Backend: Explicit PDF download routes

None of these alone would have worked.
