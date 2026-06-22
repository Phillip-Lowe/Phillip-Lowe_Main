# Revenue Dashboard — Specification Document

**Automation ID:** `revenue-dashboard`  
**Version:** 1.0  
**Status:** Draft — Specification  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## Brand Reference

| Role | Color | Hex |
|------|-------|-----|
| Headers, CTAs | Navy | `#001a2d` |
| Secondary accents | Teal | `#007da9` |
| Primary buttons, links | Cyan | `#00a1db` |
| Body text | Gray 600 | `#475569` |
| Headings | Gray 800 | `#1e293b` |
| Success | Green | `#22c55e` |
| Error | Red | `#ef4444` |

---

## 1. Executive Summary

### What It Does

Real-time dashboard pulling data from all automations: bookings, upsells, time slots, customer visits. Shows top services, peak hours, average booking value, conversion rate. Operator view for business decisions.

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
Bookings  → SQLite/Postgres
Upsells   → SQLite/Postgres
Payments  → Square API
Slots     → Calendar DB
Customers → CRM Lite
    ↓
[Aggregator — n8n Cron + Code]
    ↓
[Dashboard API]
    ↓
[Web UI — HTML/CSS/JS]
```

### Key Metrics

| Category | Metrics |
|----------|---------|
| **Revenue** | Daily/weekly/monthly revenue, avg booking value, revenue by service |
| **Customers** | New vs returning, visits/month, churn rate |
| **Operations** | Peak hours, slot utilization, no-show rate |
| **Growth** | Conversion rate, upsell rate, referral rate |

---

## 3. Dashboard Views

### View 1: Today at a Glance

- Today's bookings (count + revenue)
- Slots filled vs available
- Peak hour indicator
- No-shows today

### View 2: Weekly Trends

- Revenue chart (7-day)
- Booking count chart
- Top 5 services
- New vs returning customers

### View 3: Monthly Deep Dive

- Revenue by week
- Customer retention curve
- Upsell performance
- Referral attribution

---

## 4. Implementation Plan

| Phase | Task | Est. Effort |
|-------|------|-------------|
| 1 | Data aggregation pipeline | 3 hours |
| 2 | Dashboard API | 2 hours |
| 3 | Web UI (3 views) | 4 hours |
| 4 | Access control | 1 hour |
| **Total** | | **~10 hours** |

---

## 5. Metrics Dictionary

| Metric | Definition | Source |
|--------|-----------|--------|
| **Daily Revenue** | Sum of all completed booking totals | Bookings DB |
| **Avg Booking Value** | Total revenue / number of bookings | Bookings DB |
| **Slot Utilization** | Filled slots / total available slots | Calendar |
| **No-Show Rate** | Unconfirmed bookings / total bookings | No-Show System |
| **Upsell Rate** | Bookings with add-ons / total bookings | Upsell Engine |
| **Customer Retention** | Customers with 2+ visits / total customers | CRM Lite |
| **Referral Rate** | Bookings via referral / total bookings | Referral Engine |

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
