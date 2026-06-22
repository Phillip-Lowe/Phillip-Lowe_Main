# Auto-Scheduling Optimizer — Implementation Plan

**Automation ID:** `scheduling-optimizer`  
**Version:** 1.0  
**Status:** Draft — Planning  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## 1. Build Phases

### Phase 1: Calendar Integration (3 hours)

**Tasks:**

1. Connect to booking calendar (Google Calendar or local DB)
2. Fetch all slots for next 48 hours
3. Normalize to standard slot format (start_time, end_time, status)

---

### Phase 2: Gap Detection Algorithm (2 hours)

**Tasks:**

```javascript
// Gap detection logic
const slots = getSlots(next48Hours);
const gaps = [];

for (let i = 0; i < slots.length - 1; i++) {
  const gapMinutes = minutesBetween(slots[i].end, slots[i+1].start);
  
  if (gapMinutes >= 30) {
    gaps.push({
      start: slots[i].end,
      end: slots[i+1].start,
      duration: gapMinutes,
      discount: gapMinutes >= 60 ? 30 : 20, // % off
      type: 'between_bookings'
    });
  }
}

// Also detect: completely empty hours
const emptyHours = findEmptyBlocks(slots);
for (const block of emptyHours) {
  if (block.duration >= 60) {
    gaps.push({
      start: block.start,
      end: block.end,
      duration: block.duration,
      discount: 40,
      type: 'empty_block'
    });
  }
}
```

---

### Phase 3: Discount Slot Creation (2 hours)

**Tasks:**

1. Create discount booking slots from detected gaps
2. Apply discount percentage to standard pricing
3. Mark slots as "discount" type in booking system
4. Set auto-expiry: slots expire 2 hours before start if unfilled

---

### Phase 4: Customer Notification (2 hours)

**Tasks:**

1. Query past customers (CRM Lite) who book at similar times
2. Send targeted notifications:
   - Email: "Flash availability — [service] at [time] for [discount]% off!"
   - SMS (optional): "Last-minute opening today at 2 PM — 30% off. Book now: [link]"
3. Include one-click booking link
4. Limit: don't notify same customer more than 2x/week

---

### Phase 5: Fill-Rate Tracking (1 hour)

**Tasks:**

1. Track: gaps detected, discount slots created, slots filled
2. Calculate fill rate and revenue recovered
3. Adjust discount percentages based on fill rate:
   - Fill rate < 30% → increase discount
   - Fill rate > 70% → decrease discount (maximize revenue)

---

## 2. Timeline

| Phase | Est. Hours |
|-------|------------|
| Phase 1 | 3 |
| Phase 2 | 2 |
| Phase 3 | 2 |
| Phase 4 | 2 |
| Phase 5 | 1 |
| **Total** | **10 hours (~2 weeks)** |

---

## 3. Success Metrics

| Metric | Target |
|--------|--------|
| Schedule utilization | > 90% |
| Discount slot fill rate | > 40% |
| Revenue from filled gaps | > $500/month |
| Customer notification response | > 5% click rate |

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
