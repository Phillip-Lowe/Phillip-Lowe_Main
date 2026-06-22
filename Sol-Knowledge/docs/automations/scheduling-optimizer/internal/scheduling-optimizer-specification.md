# Auto-Scheduling Optimizer — Specification Document

**Automation ID:** `scheduling-optimizer`  
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

Detects gaps in the schedule (30-min holes, dead zones) and automatically creates discount slots. Pushes availability to past customers via SMS/email to fill empty time.

### Business Value

| Metric | Before | After (Target) |
|--------|--------|----------------|
| Schedule utilization | ~70% | > 90% |
| Revenue from discount slots | $0 | $200–500/week |
| Dead time | 2–3 hrs/day | < 30 min/day |

---

## 2. System Architecture

### Gap Detection

```
Calendar Analysis (daily at 6 PM for tomorrow)
  → Scan all slots for next 48h
    → Identify gaps:
      - 30+ min hole between bookings
      - Full hour+ with no bookings
      - Day-before empty slots
    → Create discount slot:
      - 20% off for 30-min gaps
      - 30% off for 60-min gaps
      - 40% off for empty day-before slots
    → Push to past customers:
      - Email: "Last-minute availability — 20% off!"
      - SMS: "Flash slot open today at 2 PM — 30% off"
```

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Calendar Scanner | n8n Cron + Code | Detects gaps |
| Discount Engine | n8n Code Node | Creates discount slots |
| Notification | n8n Email/SMS | Pushes to customers |
| Booking Handler | n8n Webhook | Fills discount slots |

---

## 3. Implementation Plan

| Phase | Task | Est. Effort |
|-------|------|-------------|
| 1 | Calendar integration | 3 hours |
| 2 | Gap detection algorithm | 2 hours |
| 3 | Discount slot creation | 2 hours |
| 4 | Customer notification | 2 hours |
| 5 | Fill-rate tracking | 1 hour |
| **Total** | | **~10 hours** |

---

## 4. Revenue Impact Model

| Assumption | Value |
|------------|-------|
| Daily dead hours | 2 |
| Slots created/week | 10 |
| Fill rate | 40% (4 filled) |
| Avg discounted booking | $40 |
| **Weekly additional revenue** | **$160** |
| **Monthly** | **$640** |
| **Annual** | **$7,680** |

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
