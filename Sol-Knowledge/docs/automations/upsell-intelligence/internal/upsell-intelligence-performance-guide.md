# Upsell Intelligence Engine — Performance Guide

**Automation ID:** `upsell-intelligence`  
**Version:** 1.0  
**Status:** Draft — Planning  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## 1. Key Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| Conversion Rate | conversions / impressions | > 5% |
| Revenue per Impression | total_revenue / impressions | > $0.50 |
| Click-through Rate | clicks / impressions | > 10% |
| Add-to-Cart Rate | conversions / clicks | > 30% |

---

## 2. Score Interpretation

| Score Range | Performance | Action |
|-------------|-------------|--------|
| > 5.0 | Star performer | Feature #1 position |
| 2.0–5.0 | Solid performer | Keep in top 3 |
| 0.5–2.0 | Average | Middle of list |
| < 0.5 | Underperformer | Move to bottom or hide |

---

## 3. Optimization Cycle

```
Week 1: Collect data (let current ordering run)
Week 2: Analyze scores, reorder
Week 3: A/B test new ordering vs old
Week 4: Promote winner, start next cycle
```

---

## 4. Common Patterns

### What Top Performers Look Like

- Low price relative to main item ($5–15 add-on to $50 service)
- Quick to consume (no time added to service)
- High perceived value (upgrade, not just extra)
- Visually appealing (image matters)

### What Low Performers Look Like

- Expensive relative to main item
- Adds significant time
- Unclear benefit
- Poor image or description

---

## 5. Personalization Rules

| Customer Segment | Recommended Upsell |
|------------------|-------------------|
| First-time visitor | Popular add-ons (social proof) |
| Regular (3+ visits) | Items they haven't tried |
| High spender | Premium upgrades |
| Budget-conscious | Value bundles |

---

## 6. A/B Testing Protocol

1. **Hypothesis:** "Showing [upsell X] before [upsell Y] will increase conversion"
2. **Split:** 50/50 random assignment
3. **Duration:** Minimum 200 impressions per variant
4. **Significance:** p < 0.05
5. **Winner:** Deploy winning variant to 100%

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
