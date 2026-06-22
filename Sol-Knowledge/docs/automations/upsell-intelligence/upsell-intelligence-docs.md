# Upsell Intelligence Engine — Documentation

**Automation ID:** `upsell-intelligence`  
**Version:** 1.0  
**Status:** `draft` — Oracle proposal  
**Built:** N/A  
**Last Updated:** 2026-06-11  
**Owner:** Template for all clients  
**Builder:** SOL (planned)

---

## 1. Executive Summary

### What It Does
Tracks which upsells perform best and automatically reorders them. Top performers shown first, poor performers hidden. Adapts to customer profiles ("people like you also bought...").

### Business Value
| Metric | Before | After (Target) |
|--------|--------|----------------|
| Upsell acceptance | Static ~10% | Dynamic > 20% |
| Average order value | Baseline | +15-25% |
| Upsell relevance | Generic | Personalized |

---

## 2. System Architecture

### Performance Tracking
```
For each upsell item:
  impressions = times shown
  clicks = times clicked
  conversions = times added to cart
  revenue = total $ from conversions
  
score = (conversions / impressions) * revenue_per_conversion
```

### Dynamic Ordering
```
SORT upsells BY score DESC
IF customer_profile exists:
  BOOST items customer or similar customers bought
  PENALIZE items customer declined before
```

---

## 3. Technical Specifications

### Data Collection
| Event | Logged | Source |
|-------|--------|--------|
| Upsell shown | impression | Frontend JavaScript |
| Upsell clicked | click | Frontend JavaScript |
| Upsell added | conversion | Booking form |
| Upsell removed | decline | Cart update |

### Score Calculation
```javascript
// Daily recalculation
function calculateScore(item) {
  const ctr = item.clicks / item.impressions;
  const convRate = item.conversions / item.clicks;
  const revenue = item.conversions * item.price;
  
  // Weight: conversion rate matters most
  return (ctr * 0.2) + (convRate * 0.5) + (revenue * 0.3);
}
```

---

## 4. Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `UPSELL_MIN_IMPRESSIONS` | Min impressions before hiding | `50` |
| `UPSELL_HIDE_THRESHOLD` | Score below which to hide | `0.05` |
| `UPSELL_MAX_ITEMS` | Max upsells shown | `5` |
| `UPSELL_PERSONALIZATION` | Use customer history | `true` |

---

## 5. Operational Runbook

### Monitoring
| Metric | Expected | Alert If |
|--------|----------|----------|
| Top upsell CTR | > 15% | < 10% |
| Bottom upsell CTR | < 2% | > 5% (hiding not working) |
| AOV lift from upsells | > 15% | < 5% |
| Score recalculation | Daily | > 3 days stale |

---

## 6. Build Log

### Phase 1: Tracking (Planned)
- **Status:** ⏳ QUEUED (Phase 3 priority)

---

## Appendix: Quick Reference

```
START:     Enable impression/click tracking on booking form
STOP:      Disable tracking (revert to static ordering)
CHECK:     Weekly upsell performance report
FIX:       If AOV not lifting → check score calculation
ESCALATE:  If personalization broken → check CRM data quality
```

---

**Last Updated:** 2026-06-11  
**Status:** Draft — Phase 3 priority
