# Smart Rebooking Engine — ROI Projection

**Automation ID:** `smart-rebooking`  
**Version:** 1.0  
**Status:** Draft — Planning  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## 1. Baseline Assumptions

| Metric | Conservative | Moderate | Optimistic |
|--------|-------------|----------|------------|
| Monthly active customers | 80 | 100 | 150 |
| Current rebooking rate (no reminders) | 40% | 50% | 60% |
| Target rebooking rate (with reminders) | 50% | 65% | 75% |
| Average booking value | $40 | $50 | $65 |

---

## 2. Revenue Impact

### Conservative

| Calculation | Value |
|-------------|-------|
| Customers | 80 |
| Current monthly rebooks (40%) | 32 |
| Target monthly rebooks (50%) | 40 |
| Additional bookings | 8 |
| Avg value | $40 |
| **Monthly additional revenue** | **$320** |
| **Annual** | **$3,840** |

### Moderate (Target)

| Calculation | Value |
|-------------|-------|
| Customers | 100 |
| Current rebooks (50%) | 50 |
| Target rebooks (65%) | 65 |
| Additional bookings | 15 |
| Avg value | $50 |
| **Monthly additional revenue** | **$750** |
| **Annual** | **$9,000** |

### Optimistic

| Calculation | Value |
|-------------|-------|
| Customers | 150 |
| Current rebooks (60%) | 90 |
| Target rebooks (75%) | 113 |
| Additional bookings | 23 |
| Avg value | $65 |
| **Monthly additional revenue** | **$1,495** |
| **Annual** | **$17,940** |

---

## 3. Cost Analysis

| Cost Item | Amount |
|-----------|--------|
| Build effort | ~10 hours (one-time) |
| Monthly maintenance | $0 (automated) |
| Email sending | $0 (existing SMTP) |
| **Total fixed cost** | **~10 hours** |
| **Monthly operating cost** | **$0** |

---

## 4. Retention Impact

| Metric | Before | After |
|--------|--------|-------|
| 3-month retention | ~60% | ~75% |
| 6-month retention | ~40% | ~55% |
| Customer lifetime (months) | ~8 | ~12 |
| Lifetime value | $400 | $600 |

**Lifetime value increase: +50%**

---

## 5. Recommendation

**Build after CRM Lite.** Requires customer history to calculate cycles. High retention impact with zero operating cost.

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
