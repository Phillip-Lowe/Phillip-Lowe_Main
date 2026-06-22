# Utopia Deli — Catering Lead System
## Lead Scoring Algorithm Documentation

**Document ID:** `UD-CAT-SCORE-001`  
**Version:** 1.0  
**Status:** Internal — Systack Only  
**Source System:** Utopia Deli (Live since 2026-06-08)  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## Brand Reference

| Role | Color | Hex |
|------|-------|-----|
| Primary | Deep Burgundy | `#590B3F` |
| Primary Light | Burgundy Light | `#7a1a55` |
| Accent | Rust Red | `#AF3D4B` |
| Accent Hover | Rust Light | `#c44d5b` |
| Secondary | Purple | `#754681` |
| Gold | Warm Gold | `#D59F5C` |
| Gold Light | Cream | `#f5e6d0` |
| Background | Off-White | `#FBFCFE` |
| Card | White | `#FFFFFF` |
| Text | Dark Gray | `#1F2937` |
| Text Light | Medium Gray | `#6B7280` |
| Border | Light Gray | `#E5E7EB` |
| Success | Green | `#22c55e` |
| Error | Red | `#dc2626` |

---

## 1. Scoring Formula

```
Total Score = (GuestCountScore × 0.40) + (DateProximityScore × 0.30) + (ServiceTypeScore × 0.20) + (BudgetBonus × 0.10)
```

**Range:** 0–100  
**Rounding:** Nearest integer

---

## 2. Factor Definitions

### Factor 1: Guest Count (Weight: 40%)

| Guest Count | Points | Rationale |
|-------------|--------|-----------|
| > 100 | 100 | Large event — high revenue potential |
| 50–100 | 65 | Medium event — solid opportunity |
| < 50 | 30 | Small event — lower priority |

**Default:** 30 (if guest count not provided)

---

### Factor 2: Date Proximity (Weight: 30%)

| Time Until Event | Points | Rationale |
|------------------|--------|-----------|
| < 2 weeks | 100 | Urgent — needs immediate response |
| 2–4 weeks | 65 | Moderate urgency |
| > 4 weeks | 30 | Planning ahead — lower urgency |

**Default:** 30 (if event date not provided)

---

### Factor 3: Service Type (Weight: 20%)

| Service Type | Points | Rationale |
|--------------|--------|-----------|
| Full Service | 100 | Higher value, more complex |
| Drop-off Only | 30 | Lower value, simpler |

**Default:** 30 (if service type not specified)

---

### Factor 4: Budget Mentioned (Weight: 10%)

| Budget Provided | Points | Rationale |
|-----------------|--------|-----------|
| Yes (budget > $0) | 100 | Customer is serious, has funding |
| No / Not provided | 0 | Less qualified |

**Default:** 0

---

## 3. Score Thresholds

| Score Range | Category | Response Type |
|-------------|----------|---------------|
| 80–100 | **High** | Detailed quote + calendar link + priority follow-up |
| 50–79 | **Medium** | Standard info + follow-up offer |
| 0–49 | **Low** | Basic info + "reach out when plans firm up" |

---

## 4. Example Calculations

### Example 1: Corporate Lunch (High Score)

| Factor | Value | Raw Points | Weighted |
|--------|-------|-----------|----------|
| Guest Count | 120 | 100 | 40.0 |
| Date Proximity | 10 days | 100 | 30.0 |
| Service Type | Full Service | 100 | 20.0 |
| Budget | $3,500 | 100 | 10.0 |
| **Total** | | | **100** |

**Category:** High — Send detailed quote immediately.

---

### Example 2: Birthday Party (Medium Score)

| Factor | Value | Raw Points | Weighted |
|--------|-------|-----------|----------|
| Guest Count | 60 | 65 | 26.0 |
| Date Proximity | 21 days | 65 | 19.5 |
| Service Type | Drop-off | 30 | 6.0 |
| Budget | Not provided | 0 | 0.0 |
| **Total** | | | **52** |

**Category:** Medium — Send standard info with follow-up offer.

---

### Example 3: Small Gathering (Low Score)

| Factor | Value | Raw Points | Weighted |
|--------|-------|-----------|----------|
| Guest Count | 20 | 30 | 12.0 |
| Date Proximity | 45 days | 30 | 9.0 |
| Service Type | Drop-off | 30 | 6.0 |
| Budget | Not provided | 0 | 0.0 |
| **Total** | | | **27** |

**Category:** Low — Send basic info.

---

## 5. Implementation (n8n Code Node)

```javascript
const guestCount = $json.guest_count || 0;
const eventDate = new Date($json.event_date);
const now = new Date();
const daysUntil = Math.ceil((eventDate - now) / (1000 * 60 * 60 * 24));
const serviceType = $json.service_type || 'drop-off';
const hasBudget = $json.budget && $json.budget > 0;

// Guest count score
let guestScore = 30;
if (guestCount > 100) guestScore = 100;
else if (guestCount >= 50) guestScore = 65;

// Date proximity score
let dateScore = 30;
if (daysUntil <= 14) dateScore = 100;
else if (daysUntil <= 28) dateScore = 65;

// Service type score
let serviceScore = serviceType === 'full-service' ? 100 : 30;

// Budget bonus
let budgetScore = hasBudget ? 100 : 0;

// Weighted total
const totalScore = Math.round(
  (guestScore * 0.40) + (dateScore * 0.30) + (serviceScore * 0.20) + (budgetScore * 0.10)
);

return [{
  json: {
    ...$json,
    lead_score: totalScore,
    lead_category: totalScore >= 80 ? 'high' : totalScore >= 50 ? 'medium' : 'low',
    scoring_breakdown: {
      guest_count: { value: guestCount, score: guestScore, weighted: guestScore * 0.40 },
      date_proximity: { days: daysUntil, score: dateScore, weighted: dateScore * 0.30 },
      service_type: { type: serviceType, score: serviceScore, weighted: serviceScore * 0.20 },
      budget: { provided: hasBudget, score: budgetScore, weighted: budgetScore * 0.10 }
    }
  }
}];
```

---

## 6. Tuning Guidelines

### When to Adjust Weights

| Symptom | Possible Fix |
|---------|-------------|
| Too many "High" scores | Raise high threshold to 85 |
| Too few "High" scores | Lower high threshold to 75 |
| Small events scoring too high | Reduce guest count weight |
| Far-out events scoring too high | Reduce date proximity weight |
| Budget not differentiating enough | Increase budget weight |

### Adjustment Process

1. Review 2–4 weeks of scored leads
2. Compare scores against actual conversion outcomes
3. Adjust one weight at a time
4. Monitor for 2 weeks before further changes
5. Document all changes in this file

---

## 7. Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-08 | Initial scoring algorithm deployed |
| 1.0 | 2026-06-16 | Documented (this file) |

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
