# n8n Workflow Audit Report — 2026-05-20

**Auditor:** SOL (System Operations Liaison)  
**Date:** 2026-05-20 05:28 CDT  
**Status:** ✅ Complete

---

## Executive Summary

| Metric | Count |
|---|---|
| **Total Active Workflows** | 21 |
| **Utopia Deli Related** | 8 |
| **Lead Generation** | 3 |
| **Content/Publishing** | 1 |
| **System/Testing** | 4 |
| **Constraint Evaluator** | 3 |
| **Other** | 2 |

**Health Status:**
| Service | Status | Details |
|---|---|---|
| n8n (localhost:5678) | ✅ Healthy | API responding |
| Utopia Deli Server (localhost:8000) | ✅ Healthy | Checkout + admin dashboard |
| SOL Webhook (localhost:9000) | ✅ Healthy | Invoice extraction ready |
| Invoice Dashboard (localhost:9001) | ✅ Healthy | Showing 1 invoice ($14,864.50) |
| invoices.systack.net | ✅ Live | Public tunnel working |
| order-utopia-deli.systack.net | ✅ Live | Deli order page + admin |
| n8n.theutopiadeli.com | ❌ FAIL | Tunnel issue — needs check |

---

## Category 1: Utopia Deli (8 workflows)

### 🔴 CRITICAL ISSUES

**1. Multiple Checkout Workflows — REDUNDANT**
- `Utopia Deli — Full Checkout (Modifiers + Validation)` — ACTIVE
- `Utopia Deli — HTML Webhook Checkout v2` — ACTIVE
- `Utopia Deli — HTML Checkout v3 (Local API)` — ACTIVE
- `Utopia Deli — Minimal Checkout` — ACTIVE
- `Utopia-Deli-Simple-Checkout` — ACTIVE

**Problem:** 5 different checkout workflows all active = customer confusion, data inconsistency, maintenance nightmare.

**Fix:** Pick ONE canonical checkout, disable others, update order page to use single endpoint.

**2. Google Sheets Dependencies — EXTERNAL RISK**
- All deli workflows read/write Google Sheets for:
  - Menu catalog
  - Open hours
  - City/tax rates
  - Order log
  - Cart state

**Problem:** If Google auth expires or Sheets API limits hit, orders fail.

**Fix:** Migrate critical data to local SQLite (menu, hours, orders already in `orders.db`).

**3. Square Payment Link Creation — EXTERNAL API**
- All checkout workflows call Square API for payment links
- Requires valid Square OAuth token

**Problem:** Token expiration breaks checkout entirely.

**Fix:** Add token refresh automation + fallback (cash on pickup).

### 🟡 WARNINGS

**4. AbstractAPI for Email/Phone Validation**
- Free tier limits: 100 requests/day
- Used in full checkout workflow

**Fix:** Consider removing or caching validation results.

**5. Twilio SMS Fallback**
- Configured but may not be funded
- Fallback SMS if email fails

**6. Payment Link Cleanup — SCHEDULED**
- `Utopia Deli Online Order Unused Payment Link deletion` — ACTIVE
- Runs on schedule to delete unpaid Square links
- Prevents link clutter

**Status:** ✅ Working as intended

---

## Category 2: Lead Generation (3 workflows)

### ✅ WORKING

**1. Green Systems — Service Business Lead Scraper**
- Trigger: Schedule (daily)
- Action: Scrapes Google Maps for service businesses
- Status: ACTIVE

**2. Systack Lead Scraper — SQLite CRM**
- Trigger: Schedule
- Action: Saves leads to SQLite instead of Sheets
- Uses Google Maps API
- Status: ACTIVE

**3. Green Systems — Outreach Sequencer**
- Trigger: Schedule
- Action: Sends follow-up emails to leads
- Status: ACTIVE

### 🔴 ISSUES

**4. Google Maps API Key**
- Stored in `~/.n8n/env.sh`
- Hardcoded: `GOOGLE_MAPS_API_KEY="AIzaSy…_T4Y"`

**Problem:** Key is exposed in env file. If leaked, quotas could be drained.

**Fix:** Move to keychain or n8n credentials vault.

---

## Category 3: Content/Publishing (1 workflow)

**1. Sol Blog Post Webhook**
- Trigger: Webhook POST
- Action: Receives blog content, publishes (where?)
- Status: ACTIVE

**⚠️ Unknown:** Where does this publish? WordPress? Ghost? GitHub Pages?

---

## Category 4: System/Testing (4 workflows)

**1. SOL Morning Briefing** — ✅ WORKING
- Trigger: Schedule (daily 9 AM)
- Action: Sends weather + status to Green via iMessage
- Uses wttr.in for weather
- Status: ACTIVE

**2. Error Catcher — Master** — ✅ WORKING
- Trigger: Error events from other workflows
- Action: Logs errors, notifies
- Status: ACTIVE

**3. SOL-Test-sqlite3-Fixed / SOL-Test-Webhook-sqlite3**
- Status: ACTIVE but likely development/testing
- Should be disabled in production

---

## Category 5: Constraint Evaluator (4 workflows)

### 🔴 BROKEN

**All 4 constraint evaluator workflows are NON-FUNCTIONAL:**

1. `Constraint Evaluator Master`
2. `Invoice Validation with Constraint Evaluator`
3. `Custom Constraint Validation`
4. `Schedule Conflict Detection`

**Problem:** All call `http://127.0.0.1:8000/evaluate` — but there is NO server running on port 8000 for constraint evaluation.

The Utopia Deli checkout server IS on port 8000, but it doesn't have a `/evaluate` endpoint.

**Fix Options:**
- Option A: Deploy constraint evaluation server on different port
- Option B: Disable these workflows until server exists
- Option C: Integrate constraint checking into SOL webhook or n8n code nodes

---

## Category 6: Other (1 workflow)

**1. SOL-Checkout-Proxy**
- Trigger: Webhook
- Purpose: Unknown proxy/routing layer
- Status: ACTIVE

---

## Recommendations

### Immediate (Do Now)

1. **Disable redundant checkout workflows** — Pick ONE, disable 4 others
2. **Fix n8n.theutopiadeli.com tunnel** — Check cloudflared config
3. **Disable constraint evaluator workflows** — No backend server
4. **Hide Google Maps API key** — Move to secure storage

### Short-term (This Week)

5. **Migrate deli data from Sheets to SQLite** — Menu, hours, orders
6. **Add Square token refresh automation**
7. **Document which checkout is canonical**
8. **Test lead scraper output** — Verify leads are being collected

### Long-term (This Month)

9. **Build constraint evaluator backend** — Or remove workflows
10. **Add monitoring dashboard** — All workflow health in one view
11. **Create invoice ingestion n8n workflow** — Connect to SOL webhook
12. **Build review monitoring automation** — Google Reviews API

---

## Action Items

| Priority | Action | Owner |
|---|---|---|
| 🔴 P0 | Fix n8n.theutopiadeli.com tunnel | SOL |
| 🔴 P0 | Disable 4 redundant checkout workflows | Green + SOL |
| 🔴 P0 | Disable broken constraint evaluator workflows | SOL |
| 🟡 P1 | Migrate deli data to SQLite | SOL |
| 🟡 P1 | Secure Google Maps API key | SOL |
| 🟢 P2 | Build invoice ingestion n8n workflow | SOL |
| 🟢 P2 | Add review monitoring workflow | SOL |

---

## File Locations

| Component | Path |
|---|---|
| n8n Database | `~/.n8n/database.sqlite` |
| Utopia Deli Server | `~/.openclaw/workspaces/sol/utopia-deli-revamp/checkout-server-v3.py` |
| SOL Webhook | `~/.openclaw/workspaces/sol/scripts/sol-webhook-server.py` |
| Invoice Dashboard | `~/.openclaw/workspaces/sol/scripts/invoice-dashboard-server.py` |
| Cloudflare Configs | `~/.cloudflared/config-*.yml` |
| n8n Env | `~/.n8n/env.sh` |
| Audit Script | `~/.openclaw/workspaces/sol/scripts/n8n-audit.py` |

---

**Report generated by SOL — System Operations Liaison**
