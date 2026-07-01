# Dashboard Build Plans — v1.0

**Created:** 2026-06-30 22:07 CDT
**Updated:** Green decision — two dashboards confirmed, deli deferred
**Status:** Ready for build

---

## Confirmed Build Order

| # | Dashboard | Audience | Status |
|---|-----------|----------|--------|
| 1 | **Deployment Command Center** | Green (master view) | Ready to build |
| 2 | **Booking Dashboard** | Booking service clients | Ready after #1 |
| — | ~~Deli Dashboard~~ | ~~Deli staff~~ | **HOLD OFF** — Square covers it |

---

## 1. DEPLOYMENT COMMAND CENTER (Green's Master View)

### Why First

You currently have no visibility into:
- How many clients are deployed and where
- Which agents are running vs dead
- VPS health and uptime
- n8n workflow failures
- Revenue across the entire fleet
- Any service needing attention

This is the backbone. Without it, you're flying blind.

### What It Monitors

| System | Current Port | What We Track |
|--------|-------------|---------------|
| SAOS Customer Dashboard | 8768 | Client logins, task queue, agent health |
| Invoice Dashboard | 8766 | Pipeline status, failed invoices |
| Fleet Dashboard | 8765 | Agent states, pending tasks |
| n8n Instance | 5678 | Workflow runs, failures, queue depth |
| Booking System | (new 8772) | Appointment volume, no-show rate |
| Deli System | Square | Payment link status, order volume |
| VPS Infrastructure | Vultr | Uptime, disk, memory, Tailscale |

### Dashboard Tabs

#### Tab 1: 🗺️ Fleet Overview
```
┌─────────────────────────────────────────────┐
│  8 Clients Active    47 Agents Running       │
│  $3,847 MRR          2 Alerts              │
├─────────────────────────────────────────────┤
│ Client Cards:                               │
│ ┌──────────────┐ ┌──────────────┐           │
│ │ Acme Co      │ │ Utopia Deli  │           │
│ │ 🟢 Healthy   │ │ 🟢 Healthy   │           │
│ │ 5 agents     │ │ 3 agents     │           │
│ │ $299/mo      │ │ $149/mo      │           │
│ └──────────────┘ └──────────────┘           │
└─────────────────────────────────────────────┘
```

- All clients with health status
- Total agents running
- Total MRR
- Quick action: click client → drill down

#### Tab 2: 🖥️ Infrastructure
- VPS list (IP, hostname, uptime, health)
- Service ports status (up/down indicators)
- Disk/memory usage per machine
- Tailscale network map

#### Tab 3: 🤖 Agents
- All agents across all clients — status, last heartbeat
- Busy vs idle count
- Error count per agent
- Spawn/kill controls (admin only)

#### Tab 4: ⚡ Services
- n8n workflow status (active/failed)
- Error queue
- Workflow runs per client
- Enable/disable workflows

#### Tab 5: 💰 Revenue
- MRR per client
- Stripe sync status
- Failed payments
- Usage-based charges

#### Tab 6: 🔔 Alerts
- Active alerts (failed VPS, dead agents, failed workflows)
- Alert history
- Notification routing

### Tech Stack

```
Frontend:  HTML + vanilla JS (reuse SAOS dashboard CSS)
Backend:   Python Flask API (new: fleet-api.py)
Database:  PostgreSQL (systack_memory — reuse existing tables)
Auth:      Green's admin PIN only
Access:    Tailscale only (not public)
Port:      8770
```

### New API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/fleet/clients` | All clients with health status |
| `GET /api/fleet/agents` | All agents across fleet |
| `GET /api/fleet/infrastructure` | VPS + service health |
| `GET /api/fleet/workflows` | n8n workflow status |
| `GET /api/fleet/revenue` | Revenue summary |
| `GET /api/fleet/alerts` | Active alerts |
| `POST /api/fleet/clients/:id/action` | Pause/resume/provision |

### Data Sources

| Data | Source | How |
|------|--------|-----|
| Client list | PostgreSQL `saos_clients` | Direct query |
| Agent status | PostgreSQL `agent_state` | Direct query |
| VPS health | HTTP health checks + SSH | Poll endpoints |
| n8n status | n8n REST API | `GET /api/v1/workflows` |
| Revenue | Stripe API | API call |
| Alerts | Generated from health checks | Rule engine |

### Build Estimate

| Phase | What | Time |
|-------|------|------|
| 1 | Fleet Overview tab + API | 1 day |
| 2 | Infrastructure + Agents tabs | 1 day |
| 3 | Services + Revenue tabs | 1 day |
| 4 | Alerts tab + polish | 1 day |
| **Total** | | **4 days** |

---

## 2. BOOKING DASHBOARD (Client-Facing)

### Audience

Business owners who use SyStack's booking + no-show prevention service.

### What Already Exists

| Component | Status |
|-----------|--------|
| Booking form (`test-book.html`) | ✅ Working demo |
| n8n webhook (`booking-website-demo`) | ✅ Active |
| PostgreSQL `systack_noshow.bookings` | ✅ Working |
| Email confirmation + reminders | ✅ Working |
| Production booking page | ❌ Need `/book.html` (clone of test, remove TEST banner) |

### Dashboard Tabs

#### Tab 1: 📅 Today
- Today's appointments (cards with time, name, service, status)
- Confirmation rate
- No-show risk (flag unconfirmed)
- Quick actions: call, SMS, cancel, reschedule

#### Tab 2: 📆 Calendar
- Week view (appointments by day/time)
- Month view (volume heatmap)
- Filter by service
- Click → detail modal

#### Tab 3: 📊 Analytics
- Booking volume (daily/weekly/monthly)
- No-show rate over time
- Revenue by service
- Lead time analysis
- Source breakdown (web vs phone vs walk-in)

#### Tab 4: ⚙️ Settings
- Business hours
- Services offered (name, duration, price)
- Reminder timing (24hr/2hr)
- Confirmation method (email/SMS)
- Block-out dates (holidays)

### Tech Stack

```
Frontend:  HTML + vanilla JS (reuse SAOS dashboard CSS)
Backend:   Python Flask API (new: booking-api.py)
Database:  PostgreSQL (systack_noshow — already exists)
Auth:      PIN-based (same pattern as SAOS client dashboard)
Access:    Tailscale or public with auth
Port:      8772
```

### Build Estimate

| Phase | What | Time |
|-------|------|------|
| 1 | Today tab + API | 1 day |
| 2 | Calendar tab | 1 day |
| 3 | Analytics tab | 1 day |
| 4 | Settings tab + production booking page | 1 day |
| **Total** | | **4 days** |

---

## DELI DASHBOARD — DEFERRED

**Status:** HOLD OFF

**Reasoning:**
- Square POS already provides transaction-level dashboard
- Deli staff workflow is simple: take order → prepare → hand over
- Kitchen display would be nice but not revenue-critical right now
- Can revisit if Square proves insufficient or if prep complexity grows

**What Deli DOES need (separate from dashboard):**
- Continue monitoring combo pricing (done — v5 fixed)
- Ensure confirmation emails work (done)
- Monitor Google Sheets order log (already working)
- Keep Square integration healthy (monitor via Deployment Command Center)

---

## SHARED INFRASTRUCTURE

Build once, use everywhere:

| Component | Used By |
|-----------|---------|
| `systack-site/css/dashboard-base.css` | Fleet + Booking |
| PIN auth pattern (from SAOS) | Fleet + Booking |
| Flask API patterns (from SAOS `api.py`) | Fleet + Booking |
| PostgreSQL connection pool | Fleet + Booking |
| PDF generator (reports) | Booking |

---

## REVISED TIMELINE

| Week | What | Deliverable |
|------|------|-------------|
| Week 1 | Deployment Command Center | Fleet Overview live on port 8770 |
| Week 2 | Booking Dashboard MVP | Today + Calendar tabs on port 8772 |
| Week 3 | Booking Dashboard complete | Analytics + Settings + production `/book` page |

**Total:** ~3 weeks for both dashboards at full scope.

---

## WHAT I NEED FROM YOU NOW

1. **Confirm priority:** Fleet Command Center first, then Booking?
2. **Fleet dashboard access:** Tailscale only or public with strong auth?
3. **Green's admin PIN:** What PIN for your access?
4. **VPS check:** Do we need a new VPS (8GB) for this, or run on existing MacBook?

Ready to start building when you say go.
