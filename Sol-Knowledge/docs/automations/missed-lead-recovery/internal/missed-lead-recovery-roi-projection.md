# Missed-Lead Recovery Engine — ROI Projection

**Automation ID:** `missed-lead-recovery`  
**Version:** 1.0  
**Status:** Draft — Planning  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## 1. Baseline Assumptions

| Metric | Conservative | Moderate | Optimistic |
|--------|-------------|----------|------------|
| Monthly booking attempts | 150 | 200 | 300 |
| Abandonment rate | 25% | 30% | 35% |
| Recovery rate | 10% | 15% | 20% |
| Average booking value | $40 | $50 | $65 |

---

## 2. Revenue Projections

### Conservative Scenario

| Calculation | Value |
|-------------|-------|
| Monthly attempts | 150 |
| Abandoned (25%) | 38 |
| Recovered (10%) | 4 |
| Avg booking value | $40 |
| **Monthly recovered revenue** | **$160** |
| **Annual recovered revenue** | **$1,920** |

---

### Moderate Scenario (Target)

| Calculation | Value |
|-------------|-------|
| Monthly attempts | 200 |
| Abandoned (30%) | 60 |
| Recovered (15%) | 9 |
| Avg booking value | $50 |
| **Monthly recovered revenue** | **$450** |
| **Annual recovered revenue** | **$5,400** |

---

### Optimistic Scenario

| Calculation | Value |
|-------------|-------|
| Monthly attempts | 300 |
| Abandoned (35%) | 105 |
| Recovered (20%) | 21 |
| Avg booking value | $65 |
| **Monthly recovered revenue** | **$1,365** |
| **Annual recovered revenue** | **$16,380** |

---

## 3. Cost Analysis

| Cost Item | Amount |
|-----------|--------|
| Build effort | ~12 hours (one-time) |
| Monthly maintenance | $0 (fully automated) |
| Email sending (SMTP) | $0 (existing infrastructure) |
| Database storage | $0 (existing Postgres) |
| **Total fixed cost** | **~12 hours labor** |
| **Monthly operating cost** | **$0** |

---

## 4. Payback Period

| Scenario | Monthly Revenue | Build Cost (hours) | Payback |
|----------|----------------|---------------------|---------|
| Conservative | $160 | 12 hrs | < 1 month |
| Moderate | $450 | 12 hrs | < 1 month |
| Optimistic | $1,365 | 12 hrs | Immediate |

**Conclusion:** Positive ROI in all scenarios within the first month.

---

## 5. Comparison: Recovery vs New Customer Acquisition

| Channel | Cost per Customer | Monthly Volume |
|---------|-------------------|----------------|
| Paid ads (Google/Facebook) | $15–30 | Varies |
| Delivery platform fees | 20–30% per order | Ongoing |
| Missed-lead recovery | **$0** | 4–21 recovered/month |

Recovered leads cost $0 to acquire — they already found you once.

---

## 6. Sensitivity Analysis

### What if recovery rate is only 5%?

| Scenario | Monthly Revenue |
|----------|----------------|
| Conservative (150 attempts) | $80 |
| Moderate (200 attempts) | $150 |
| Optimistic (300 attempts) | $340 |

**Still positive ROI** — system costs $0/month to run.

### What if average booking value is $25?

| Recovery Rate | Monthly Revenue |
|---------------|----------------|
| 10% | $112 |
| 15% | $225 |
| 20% | $375 |

**Still positive ROI** at any recovery rate above ~2%.

---

## 7. Recommendation

**Build immediately.** Zero operating cost, positive ROI at any recovery rate above 2%, and recovered customers have higher lifetime value (they already showed purchase intent).

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
