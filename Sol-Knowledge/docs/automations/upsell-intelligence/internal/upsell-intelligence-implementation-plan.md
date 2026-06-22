# Upsell Intelligence Engine — Implementation Plan

**Automation ID:** `upsell-intelligence`  
**Version:** 1.0  
**Status:** Draft — Planning  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## 1. Build Phases

### Phase 1: Performance Tracking Database (2 hours)

**Tasks:**

1. Create `upsell_performance` table
2. Seed with existing upsell items
3. Initialize all counters at 0

---

### Phase 2: Impression/Click/Conversion Logging (2 hours)

**Tasks:**

1. **Impression:** Log when upsell is displayed to customer
2. **Click:** Log when customer clicks/taps upsell
3. **Conversion:** Log when upsell is added to cart
4. **Revenue:** Log upsell revenue on completed order
5. All logging via n8n webhooks from frontend

---

### Phase 3: Scoring Algorithm (2 hours)

**Tasks:**

1. Build scoring function in n8n Code node
2. Recalculate scores daily (cron)
3. Apply exploration boost for new items
4. Auto-flag low performers for review

```javascript
// Daily score recalculation
for (const item of items) {
  const impressions = Math.max(item.impressions, 1);
  const conversionRate = item.conversions / impressions;
  const avgRevenue = item.revenue_cents / Math.max(item.conversions, 1);
  let score = conversionRate * (avgRevenue / 100);
  
  // Exploration boost for new items
  if (item.impressions < 100) {
    score *= 1.5;
  }
  
  // Status update
  if (item.impressions > 500 && conversionRate < 0.01) {
    item.status = 'hidden';
  } else if (item.impressions > 200 && conversionRate < 0.02) {
    item.status = 'low_priority';
  } else {
    item.status = 'active';
  }
  
  item.score = score;
}
```

---

### Phase 4: Dynamic Ordering in Frontend (2 hours)

**Tasks:**

1. Frontend fetches upsell scores on page load
2. Sorts upsells by score (descending)
3. Top 3 displayed prominently
4. Hidden items not rendered
5. New items get "New!" badge during exploration period

---

### Phase 5: A/B Testing Framework (2 hours)

**Tasks:**

1. Randomly assign customers to groups (A/B)
2. Group A: current ordering
3. Group B: experimental ordering
4. Track conversion rates per group
5. After statistical significance: promote winner

---

## 2. Timeline

| Phase | Est. Hours |
|-------|------------|
| Phase 1 | 2 |
| Phase 2 | 2 |
| Phase 3 | 2 |
| Phase 4 | 2 |
| Phase 5 | 2 |
| **Total** | **10 hours (~2 weeks)** |

---

## 3. Success Metrics

| Metric | Target |
|--------|--------|
| Overall upsell conversion | > 20% |
| Average order value increase | +15–25% |
| Low-performer auto-detection | < 2% conversion flagged |
| A/B test velocity | 1 test/month |

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
