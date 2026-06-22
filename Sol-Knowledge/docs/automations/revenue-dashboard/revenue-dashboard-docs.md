# Revenue Dashboard (Operator View) — Documentation

**Automation ID:** `revenue-dashboard`  
**Version:** 1.0  
**Status:** `draft` — Oracle proposal  
**Built:** N/A  
**Last Updated:** 2026-06-11  
**Owner:** Internal Systack tool + client dashboard  
**Builder:** SOL (planned)

---

## 1. Executive Summary

### What It Does
Real-time dashboard pulling data from all automations: bookings, upsells, time slots, customer visits. Shows top services, peak hours, average booking value, conversion rate.

### Business Value
| Metric | Before | After (Target) |
|--------|--------|----------------|
| Business visibility | Gut feel | Data-driven |
| Decision speed | Days | Hours |
| Problem detection | Reactive | Proactive |

---

## 2. System Architecture

### Data Sources
```
Bookings ──→ SQLite ──→
Upsells ───→ SQLite ──→
Payments ──→ Square ──→  [Aggregator] ──→ [Dashboard API] ──→ [Web UI]
Slots ─────→ n8n ─────→
Customers ─→ SQLite ──→
```

### Key Metrics
| Category | Metrics |
|----------|---------|
| Revenue | Daily, weekly, monthly, YTD |
| Bookings | Count, value, source, conversion |
| Upsells | Count, acceptance rate, revenue lift |
| Customers | New, returning, lapsed, VIP |
| Time | Utilization, peak hours, gaps |
| Automations | Recovery rate, review rate, referral rate |

---

## 3. Technical Specifications

### Dashboard UI
- **Tech:** HTML/CSS/JS + Chart.js or lightweight alternative
- **Update:** Real-time (SSE/polling) or manual refresh
- **Mobile:** Responsive design

### API Endpoints
| Endpoint | Data |
|----------|------|
| `/dashboard/summary` | Key metrics, period |
| `/dashboard/revenue` | Revenue breakdown |
| `/dashboard/bookings` | Booking trends |
| `/dashboard/customers` | Customer segments |

---

## 4. Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DASHBOARD_REFRESH` | Auto-refresh seconds | `300` (5 min) |
| `DASHBOARD_DEFAULT_PERIOD` | Default view | `7_days` |
| `DASHBOARD_ALERT_THRESHOLD` | Alert if bookings < X% of avg | `20` |

---

## 5. Build Log

### Phase 1: Data Aggregation (Planned)
- **Status:** ⏳ QUEUED (Phase 3 priority)

---

## Appendix: Quick Reference

```
START:     Deploy dashboard + configure data sources
STOP:      Dashboard stays live (read-only)
CHECK:     Daily morning review
FIX:       If data stale → check aggregator cron
ESCALATE:  If metrics don't match reality → verify data sources
```

---

**Last Updated:** 2026-06-11  
**Status:** Draft — Phase 3 priority
