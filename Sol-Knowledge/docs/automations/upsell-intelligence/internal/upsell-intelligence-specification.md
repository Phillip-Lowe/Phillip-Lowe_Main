# Upsell Intelligence Engine — Specification Document

**Automation ID:** `upsell-intelligence`  
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

Tracks which upsells perform best and automatically reorders them. Top performers shown first, poor performers hidden. Adapts to customer profiles ("people like you also bought...").

### Business Value

| Metric | Before | After (Target) |
|--------|--------|----------------|
| Upsell acceptance | Static ~10% | Dynamic > 20% |
| Average order value | Baseline | +15–25% |
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

score = (conversions / impressions) × revenue_per_conversion
```

### Dynamic Ordering

```
Customer views menu
  → Query upsell scores
    → Sort by score (descending)
      → Top 3 shown prominently
      → Low performers (< 2% conversion) hidden
      → New items given "exploration boost" (first 100 impressions)
```

### Personalization

```
For returning customer:
  → Look up profile (CRM Lite)
    → "Customers who get [their service] also add:"
      → Show top 3 correlated upsells
```

---

## 3. Database Schema

```sql
CREATE TABLE upsell_performance (
  upsell_id TEXT PRIMARY KEY,
  name TEXT,
  impressions INTEGER DEFAULT 0,
  clicks INTEGER DEFAULT 0,
  conversions INTEGER DEFAULT 0,
  revenue_cents INTEGER DEFAULT 0,
  score REAL DEFAULT 0,
  status TEXT DEFAULT 'active',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Implementation Plan

| Phase | Task | Est. Effort |
|-------|------|-------------|
| 1 | Performance tracking database | 2 hours |
| 2 | Impression/click/conversion logging | 2 hours |
| 3 | Scoring algorithm | 2 hours |
| 4 | Dynamic ordering in frontend | 2 hours |
| 5 | A/B testing framework | 2 hours |
| **Total** | | **~10 hours** |

---

## 5. Performance Guide

### Score Calculation

```javascript
const impressions = item.impressions || 1; // avoid division by zero
const conversionRate = item.conversions / impressions;
const avgRevenue = item.revenue_cents / (item.conversions || 1);
const score = conversionRate * (avgRevenue / 100); // normalize to dollars
```

### When to Retire an Upsell

| Condition | Action |
|-----------|--------|
| < 1% conversion after 500 impressions | Hide from menu |
| < 2% conversion after 200 impressions | Move to bottom |
| > 5% conversion | Feature prominently |
| New item (< 100 impressions) | Boost score by 50% |

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
