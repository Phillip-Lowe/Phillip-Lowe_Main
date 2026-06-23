# SAOS Customer Dashboard — Persistent Service Fix
**Date:** 2026-06-23 10:35 CDT

---

## Problem
Customer dashboard API was running (port 8768) but HTML frontend was not being served. Dashboard was unreachable via browser — only API endpoints worked.

## Root Cause
Flask app only had API routes (`/api/portal/*`). No static file serving for `index.html` or PDFs.

## Fix Applied

### 1. Updated `api.py` — Added Static File Serving
**File:** `Systack/content/saos/saos-data/customer-dashboard/api.py`

Changes:
- Added `send_from_directory` import
- Added `BASE_DIR = os.path.dirname(os.path.abspath(__file__))`
- Added Flask `static_folder=BASE_DIR`
- Added catch-all route `/<path:path>` that serves:
  - `index.html` for root path
  - Any file in the directory (PDFs, etc.)
  - Falls back to `index.html` for SPA routing

### 2. Hardened LaunchAgent
**File:** `~/Library/LaunchAgents/net.systack.customer-dashboard.plist`

Added persistence features:
- `KeepAlive` with `SuccessfulExit: false` — restarts on crash
- `ThrottleInterval: 10` — prevents rapid restart loops
- `LimitLoadToSessionType: Aqua` — runs in user login session
- `Nice: 5` — lower priority than foreground apps
- `PYTHONDONTWRITEBYTECODE: 1` — cleaner runtime

### 3. Verified Endpoints

| Endpoint | Status | Details |
|----------|--------|---------|
| `GET /` | ✅ 200 | Dashboard HTML (38.8 KB) |
| `GET /api/portal/health` | ✅ 200 | `{"status":"ok"}` |
| `GET /api/portal/status` | ✅ 200 | Full agent fleet data |
| `GET /SAOS-Service-Manual-v2.0.pdf` | ✅ 200 | 211 KB PDF |
| `GET /SAOS-Quick-Start-Guide.pdf` | ✅ 200 | 196 KB PDF |

### 4. Service Status
- **PID:** 15623
- **Port:** 8768
- **LaunchAgent:** `net.systack.customer-dashboard`
- **Working Directory:** `Systack/content/saos/saos-data/customer-dashboard/`
- **Logs:** `Systack/content/saos/saos-data/logs/customer-dashboard.log`
- **Error Logs:** `Systack/content/saos/saos-data/logs/customer-dashboard.error.log`

## Access URLs
- **Dashboard:** http://localhost:8768/
- **Demo client:** http://localhost:8768/?client_id=1
- **Health Check:** http://localhost:8768/api/portal/health

## Dashboard Features (5 Tabs)
1. **Overview** — Fleet status, metrics, health banner
2. **Agents** — All 10 fleet agents with status + task counts
3. **Tasks** — Task history with filtering
4. **Documents** — PDF downloads (tier-based access)
5. **Account** — Subscription + deployment info

## Persistence Guarantee
- Survives reboots (LaunchAgent in `~/Library/LaunchAgents/`)
- Auto-restarts on crash (KeepAlive)
- Throttled restarts prevent runaway loops
- Logs rotate to dedicated files

---
*Session saved: 2026-06-23 10:35 CDT*
