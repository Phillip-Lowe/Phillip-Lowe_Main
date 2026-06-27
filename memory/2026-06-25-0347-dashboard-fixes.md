# Dashboard Fixes — 2026-06-25 03:47 CDT

## Issues Fixed

### 1. Missing Activity Tab Button
- **Problem:** Activity tab div existed (`#activityTab`) with `loadActivity()` referenced, but no nav button to trigger it
- **Fix:** Added `<button class="nav-link" onclick="showTab('activity', this)">📋 Activity</button>` to nav

### 2. Missing `loadActivity()` Function
- **Problem:** `showTab()` called `loadActivity()` but function didn't exist
- **Fix:** Added `loadActivity()` function that fetches tasks and renders an activity feed with status icons

### 3. Weak Authentication (No PIN)
- **Problem:** Anyone could login with just a client_id, no password/PIN
- **Fix:** 
  - Added `auth_pin` column to `saos_clients` table
  - Set PIN `1234` for test client (id=1)
  - Updated `/api/auth/login` to require PIN
  - Updated frontend login form with PIN input field
  - Existing token field preserved as bypass option

### 4. Mobile Responsive Issues
- **Problem:** nav-right elements (user name, logout button) could overflow on small screens
- **Fix:** Added mobile responsive styles:
  - `.nav-right .nav-client-name { display: none }` on mobile
  - Smaller logout button on mobile
  - `.agents-grid { grid-template-columns: 1fr }` on mobile
  - `.task-table { font-size: 12px }` on mobile
  - `.activity-item` smaller padding on mobile
  - Login card padding reduced on mobile
  - Added `@media (max-width: 480px)` breakpoint for extra-small screens

## Testing Results

- ✅ API health check passes
- ✅ PIN-based auth works (returns token on valid PIN)
- ✅ Invalid PIN rejected (401)
- ✅ Tailscale URL loads dashboard HTML
- ✅ Activity tab button renders in nav
- ✅ All 6 tabs have corresponding nav buttons

## Files Modified

1. `Systack/content/saos/saos-data/customer-dashboard/index.html`
   - Added Activity nav button
   - Added Activity tab content div
   - Added `loadActivity()` function
   - Added `getStatusIcon()` helper
   - Added activity feed CSS styles
   - Updated login form with PIN field
   - Updated `login()` JavaScript to send PIN
   - Added mobile responsive improvements

2. `Systack/content/saos/saos-data/customer-dashboard/api.py`
   - Updated `/api/auth/login` to require PIN
   - Returns 401 for invalid PIN, 403 for unset PIN

## Database Changes

```sql
ALTER TABLE saos_clients ADD COLUMN auth_pin VARCHAR(10);
UPDATE saos_clients SET auth_pin = '1234' WHERE id = 1;
```

## URLs

- Local: http://localhost:8768/
- Tailnet: https://phillips-macbook-air.tail573d57.ts.net/dashboard/
- Test PIN: `1234` (for client id 1)

## Mobile Fix — 2026-06-25 03:54 CDT

### Problem
"The string did not match the expected pattern" error on mobile login.

### Cause
HTML5 `pattern="[0-9]*"` + `inputmode="numeric"` attributes triggered browser validation errors on mobile Safari/Chrome.

### Fix Applied
- Removed `pattern` and `inputmode` attributes from login inputs
- Added `novalidate` to form to disable HTML5 validation entirely
- Removed inline `onclick="login()"` from button (double-fired with form submit)
- Added proper `submit` event listener in DOMContentLoaded
- Added `.trim()` to all input values
- Added `-webkit-appearance: none` to login inputs
- Set `font-size: 16px` on password fields to prevent iOS zoom

## Next Steps

- Test on actual mobile device
- Verify all tabs load correctly through Tailscale
- Consider adding "forgot PIN" flow
- Consider PIN hashing (currently plaintext for simplicity)
