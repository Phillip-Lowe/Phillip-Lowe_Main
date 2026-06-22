# Smart Rebooking Engine — Implementation Plan

**Automation ID:** `smart-rebooking`  
**Version:** 1.0  
**Status:** Draft — Planning  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## 1. Build Phases

### Phase 1: Customer History Tracking (2 hours)

**Tasks:**

1. Add `customer_cycles` table to Postgres
2. On service completion, INSERT/UPDATE cycle record
3. Calculate `typical_cycle_days` from customer's own history (or use defaults)
4. Set `predicted_return_date = last_booking_date + typical_cycle_days`

---

### Phase 2: Cycle Calculation Algorithm (2 hours)

**Algorithm:**

```javascript
// For each customer + service type:
// 1. Get last 3 booking dates
// 2. Calculate average interval
// 3. If < 3 bookings, use service default cycle
// 4. Set predicted_return_date

const bookings = getLastBookings(customerId, serviceType, 3);
if (bookings.length >= 2) {
  // Calculate average interval from actual history
  let totalDays = 0;
  for (let i = 1; i < bookings.length; i++) {
    totalDays += daysBetween(bookings[i-1].date, bookings[i].date);
  }
  typicalCycleDays = Math.round(totalDays / (bookings.length - 1));
} else {
  // Use service default
  typicalCycleDays = SERVICE_DEFAULTS[serviceType] || 28;
}

predictedReturnDate = addDays(lastBookingDate, typicalCycleDays);
```

**Service defaults:**

| Service | Default Cycle (Days) |
|---------|---------------------|
| Haircut | 28 |
| Color | 42 |
| Beard Trim | 14 |
| Massage | 14 |
| Cleaning | 7 |

---

### Phase 3: Pre-Filled Booking Links (3 hours)

**Tasks:**

1. Generate unique rebooking URL with parameters:
   - `?service=deluxe-cut&customer=cust_001&prefill=true`
2. Booking form detects `prefill=true` and auto-selects:
   - Same service
   - Preferred time slot (based on history)
   - Customer info pre-populated
3. One-click confirmation reduces friction

---

### Phase 4: Reminder Workflow (2 hours)

**Tasks:**

1. Cron workflow runs daily
2. Query: `predicted_return_date - 3 days <= NOW() AND rebook_reminder_sent = FALSE`
3. Send email: "Ready for your next [service]?" + pre-filled link
4. Mark `rebook_reminder_sent = TRUE`

---

### Phase 5: Follow-Up for Non-Rebooked (1 hour)

**Tasks:**

1. Cron workflow checks 7 days after predicted date
2. Query: `predicted_return_date + 7 days <= NOW() AND rebooked = FALSE`
3. Send gentle follow-up: "Still interested? Book when you're ready."
4. Reset cycle for next prediction

---

## 2. Timeline

| Phase | Est. Hours | Dependencies |
|-------|------------|--------------|
| Phase 1 | 2 | CRM Lite (customer history) |
| Phase 2 | 2 | Phase 1 |
| Phase 3 | 3 | Booking form exists |
| Phase 4 | 2 | Phase 2 + 3 |
| Phase 5 | 1 | Phase 4 |
| **Total** | **10** | **~2 weeks** |

---

## 3. Success Metrics

| Metric | Target |
|--------|--------|
| Rebooking link click rate | > 30% |
| Conversion from rebook link | > 50% |
| Overall retention increase | +25% |
| Customer lifetime value increase | +30% |

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
