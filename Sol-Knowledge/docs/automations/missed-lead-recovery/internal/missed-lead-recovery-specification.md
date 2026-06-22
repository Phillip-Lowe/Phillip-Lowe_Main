# Missed-Lead Recovery Engine — Specification Document

**Automation ID:** `missed-lead-recovery`  
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

Captures every abandoned booking attempt and follows up automatically at three intervals: 5 minutes ("forgot something?"), 2 hours ("still interested?"), 24 hours ("here's a reason to come back"). Converts lost sessions into revenue.

### Business Value

| Metric | Before | After (Target) |
|--------|--------|----------------|
| Abandoned session recovery | 0% | > 15% |
| Revenue from recovered leads | $0 | $300–1,000/mo |
| Customer acquisition cost | Baseline | −20% (recovered vs new) |

---

## 2. System Architecture

### Flow Diagram

```
Customer Visits Booking Page
  → Partial Data Captured?
    → Email entered → Store in recovery_queue
    → Phone entered → Store in recovery_queue
    → Neither → Cookie-based retargeting only
  → Timer: T+5 minutes
    → Email/SMS: "Did something go wrong? Complete your booking."
  → No booking?
    → Timer: T+2 hours
      → Email: "Your slot is still available" + urgency
  → No booking?
    → Timer: T+24 hours
      → Email: "Come back for X% off" or "Bonus add-on free"
  → Booked? → Remove from queue → End
  → Still no? → Tag: "lost lead" → Monthly report
```

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Abandonment Detector | Frontend JS | Captures partial form data |
| Recovery Queue | Postgres/SQLite | Stores abandoned sessions |
| Follow-Up Engine | n8n Cron + Email | Timed follow-up messages |
| Conversion Tracker | Postgres | Tracks recovered vs lost |

---

## 3. Technical Specifications

### Abandonment Detection

- Trigger: User enters email/phone but doesn't complete booking
- Capture: On field blur or form abandonment (beforeunload event)
- Storage: `recovery_queue` table with timestamp

### Follow-Up Schedule

| Interval | Channel | Message Type |
|----------|---------|-------------|
| T+5 min | Email/SMS | "Did something go wrong?" — helpful, not salesy |
| T+2 hours | Email | "Your slot is still available" — mild urgency |
| T+24 hours | Email | Incentive: discount or free add-on |

### Database Schema

```sql
CREATE TABLE recovery_queue (
  id SERIAL PRIMARY KEY,
  customer_email TEXT,
  customer_phone TEXT,
  service_interest TEXT,
  abandoned_at TIMESTAMP,
  followup_5min_sent BOOLEAN DEFAULT FALSE,
  followup_2hr_sent BOOLEAN DEFAULT FALSE,
  followup_24hr_sent BOOLEAN DEFAULT FALSE,
  recovered BOOLEAN DEFAULT FALSE,
  recovered_at TIMESTAMP,
  status TEXT DEFAULT 'active'
);
```

---

## 4. Implementation Plan

| Phase | Task | Est. Effort |
|-------|------|-------------|
| 1 | Frontend abandonment detection (JS) | 3 hours |
| 2 | Recovery queue database + webhook | 2 hours |
| 3 | T+5min follow-up workflow | 2 hours |
| 4 | T+2hr follow-up workflow | 1 hour |
| 5 | T+24hr incentive workflow | 2 hours |
| 6 | Conversion tracking + reporting | 2 hours |
| **Total** | | **~12 hours** |

---

## 5. ROI Projection

| Assumption | Value |
|------------|-------|
| Monthly booking attempts | 200 |
| Abandonment rate | ~30% (60 sessions) |
| Recovery rate (target) | 15% (9 recovered) |
| Average booking value | $50 |
| Monthly recovered revenue | **$450** |
| Annual recovered revenue | **$5,400** |

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
