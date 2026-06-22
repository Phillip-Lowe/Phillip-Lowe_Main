# Auto-Scheduling Optimizer — Revenue Impact Model

**Automation ID:** `scheduling-optimizer`  
**Version:** 1.0  
**Status:** Draft — Planning  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## 1. Baseline Assumptions

| Metric | Conservative | Moderate | Optimistic |
|--------|-------------|----------|------------|
| Daily operating hours | 8 | 8 | 10 |
| Current utilization | 70% | 65% | 60% |
| Daily dead hours | 2.4 | 2.8 | 4.0 |
| Avg slots per dead hour | 2 | 2 | 3 |
| Discount slots created/day | 5 | 6 | 12 |
| Fill rate | 30% | 40% | 50% |
| Avg discounted booking | $35 | $40 | $45 |

---

## 2. Revenue Projections

### Conservative

| Calculation | Value |
|-------------|-------|
| Slots created/day | 5 |
| Filled/day (30%) | 1.5 |
| Avg booking | $35 |
| Daily revenue | $52.50 |
| **Weekly** | **$262.50** |
| **Monthly** | **$1,050** |
| **Annual** | **$12,600** |

### Moderate (Target)

| Calculation | Value |
|-------------|-------|
| Slots created/day | 6 |
| Filled/day (40%) | 2.4 |
| Avg booking | $40 |
| Daily revenue | $96 |
| **Weekly** | **$480** |
| **Monthly** | **$1,920** |
| **Annual** | **$23,040** |

### Optimistic

| Calculation | Value |
|-------------|-------|
| Slots created/day | 12 |
| Filled/day (50%) | 6 |
| Avg booking | $45 |
| Daily revenue | $270 |
| **Weekly** | **$1,350** |
| **Monthly** | **$5,400** |
| **Annual** | **$64,800** |

---

## 3. Utilization Improvement

| Scenario | Before | After | Improvement |
|----------|--------|-------|-------------|
| Conservative | 70% | 79% | +9% |
| Moderate | 65% | 80% | +15% |
| Optimistic | 60% | 85% | +25% |

---

## 4. Cost Analysis

| Cost Item | Amount |
|-----------|--------|
| Build effort | ~10 hours (one-time) |
| Monthly maintenance | $0 (automated) |
| Discount cost | Already priced into discount slots |
| Notification cost | $0 (existing email/SMS) |
| **Total fixed cost** | **~10 hours** |
| **Monthly operating cost** | **$0** |

---

## 5. Recommendation

**Build after booking system is live.** Converts dead time into revenue with zero operating cost. Even conservative scenario recovers $1,050/month from currently wasted capacity.

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
