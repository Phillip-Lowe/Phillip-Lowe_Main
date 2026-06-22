# Smart Rebooking Engine — Specification Document

**Automation ID:** `smart-rebooking`  
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

Tracks each customer's service cycle, predicts when they're due for their next visit, and automatically sends a pre-filled booking link at the right time. Example: "Your last Deluxe Cut was 4 weeks ago — ready for your next one? Book with one click."

### Business Value

| Metric | Before | After (Target) |
|--------|--------|----------------|
| Repeat booking rate | Variable | +25% |
| Customer retention | Passive | Proactive |
| Booking friction | Full form every time | One-click rebook |

---

## 2. System Architecture

### Flow Diagram

```
Service Completed
  → Log to customer_history
    → Calculate predicted return date
      → Timer: predicted_date - 3 days
        → Send: "Ready for your next visit?" + pre-filled booking link
          → Customer clicks → Booking form pre-filled with:
            - Same service
            - Same provider (if available)
            - Preferred time slot
          → Booked? → Update cycle → Restart timer
          → Not booked? → Follow-up at predicted_date + 7 days
```

### Service Cycles (Examples)

| Service | Typical Cycle | Reminder Window |
|---------|--------------|-----------------|
| Haircut | 4 weeks | 3 days before |
| Color/Treatment | 6 weeks | 5 days before |
| Massage | 2 weeks | 2 days before |
| Cleaning | 1 week | 1 day before |

---

## 3. Database Schema

```sql
CREATE TABLE customer_cycles (
  customer_id TEXT,
  service_type TEXT,
  last_booking_date DATE,
  typical_cycle_days INTEGER,
  predicted_return_date DATE,
  rebook_reminder_sent BOOLEAN DEFAULT FALSE,
  rebooked BOOLEAN DEFAULT FALSE,
  PRIMARY KEY (customer_id, service_type)
);
```

---

## 4. Implementation Plan

| Phase | Task | Est. Effort |
|-------|------|-------------|
| 1 | Customer history tracking | 2 hours |
| 2 | Cycle calculation algorithm | 2 hours |
| 3 | Pre-filled booking link generation | 3 hours |
| 4 | Reminder workflow (Cron + Email) | 2 hours |
| 5 | Follow-up for non-rebooked | 1 hour |
| **Total** | | **~10 hours** |

---

## 5. ROI Projection

| Assumption | Value |
|------------|-------|
| Monthly customers | 100 |
| Rebooking rate increase | +25% |
| Average booking value | $50 |
| Additional monthly bookings | 25 |
| **Monthly additional revenue** | **$1,250** |
| **Annual additional revenue** | **$15,000** |

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
