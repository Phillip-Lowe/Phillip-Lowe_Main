# SAOS Dashboard Mobile Auth Fix — 2026-06-25 04:30 CDT

## What Was Fixed

### 1. Login Auth Broken (Critical Bug)
- **Problem:** Dashboard login failed on mobile with error "The string did not match the expected pattern"
- **Root Cause:** `API_BASE` was hardcoded to `''` (empty string), so browser fetch calls went to `/api/auth/login` which resolved to `https://phillips-macbook-air.tail573d57.ts.net/api/auth/login` — but Tailscale serve only proxies `/dashboard/` to the backend API (port 8768). The root `/` path proxies to a different service (port 18789), so API calls returned 404.
- **Fix:** `API_BASE` now dynamically detects the path: `window.location.pathname.startsWith('/dashboard') ? '/dashboard' : ''`
- **Result:** Mobile login works. PIN auth + session tokens functional.

### 2. Login Form Validation Issues
- **Problem:** iOS Safari was triggering HTML5 form validation despite `novalidate` attribute
- **Fix:** Changed login button from `type="submit"` to `type="button"` with direct `onclick="login()"` to bypass all native form submission behavior
- **Additional:** Added programmatic `novalidate` + `stopPropagation()` to be extra safe

### 3. Mobile Layout Issues
- **Problem:** Sidebar toggle (☰) too small, nav bar cramped, text overflow in textarea placeholder
- **Fixes:**
  - Added explicit `.sidebar-toggle` CSS styling (larger font, padding, hover state)
  - Mobile `@media` styles: smaller nav padding, smaller avatar (28px→26px), hidden client name on mobile, smaller Logout button
  - Shortened textarea placeholder from "Type your message... (Enter to send, Shift+Enter for new line)" to just "Type your message..."
  - Added mobile-specific `.input-area` sizing (reduced padding, font-size: 16px to prevent iOS zoom)
  - Added prominent "+ New Conversation" button in empty chat state for mobile UX

## Files Changed
- `Systack/content/saos/saos-data/customer-dashboard/index.html`

## Testing
- ✅ API login endpoint verified with curl (both `/dashboard/api/auth/login` and root path tested)
- ✅ PIN "1234" authenticates client_id=1 correctly
- ✅ Mobile Safari loads dashboard, login, chat, sidebar toggle, new conversation all working
- ✅ Green confirmed: "thats it it works"

## Lesson
Relative API paths in single-page apps MUST account for reverse proxy path prefixes. When Tailscale serve (or any reverse proxy) maps `/dashboard/` → `localhost:8768`, the frontend's `fetch('/api/...')` calls resolve to the ROOT path, not the proxied path. Either use absolute paths with the prefix, or detect the prefix dynamically at runtime.
