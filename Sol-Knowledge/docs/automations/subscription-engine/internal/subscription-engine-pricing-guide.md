# Subscription/Membership Engine — Pricing Strategy Guide

**Automation ID:** `subscription-engine`  
**Version:** 1.0  
**Status:** Draft — Planning  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## 1. Pricing Models

### Model A: Fixed Bundle (Most Common)

| Plan | Visits/Month | Price | Per-Visit | Savings |
|------|-------------|-------|-----------|---------|
| Basic | 2 | $X | $X/2 | 10% vs walk-in |
| Standard | 4 | $Y | $Y/4 | 15% vs walk-in |
| Premium | 8 | $Z | $Z/8 | 20% vs walk-in |

**Best for:** Services with predictable frequency (haircuts, massages, cleaning).

---

### Model B: Tiered Access

| Plan | Access Level | Price |
|------|-------------|-------|
| Silver | Off-peak only | $X |
| Gold | Any time | $Y |
| Platinum | Priority booking + perks | $Z |

**Best for:** Businesses with peak/off-peak demand variation.

---

### Model C: Unlimited (Gym-Style)

| Plan | Limit | Price |
|------|-------|-------|
| Unlimited | No cap | $Z |

**Best for:** Low marginal cost services (fitness, coworking, digital).

---

## 2. Pricing Formula

```
Subscription Price = (Walk-In Price × Visits) × (1 − Discount %)
```

### Example: Barber Shop

| Walk-in cut | $35 |
|-------------|-----|
| Visits/month | 4 |
| Discount | 15% |
| **Subscription price** | **$119 → round to $120** |

Customer saves $20/month vs walk-in. Business gets guaranteed $120/month.

---

## 3. Discount Guidelines

| Visit Frequency | Recommended Discount |
|-----------------|---------------------|
| 2 visits/month | 10% |
| 4 visits/month | 15% |
| 8 visits/month | 20% |
| Unlimited | 25–30% |

**Rule:** Higher commitment = higher discount. But never discount below marginal cost.

---

## 4. Retention Tactics

| Tactic | When | Impact |
|--------|------|--------|
| Annual plan discount | At signup | +20% retention |
| Freeze option | Customer traveling/ill | Prevents cancellation |
| Loyalty bonus | Every 6 months | +15% retention |
| Win-back offer | After cancellation | 10–15% recovery |

---

## 5. Common Mistakes

| Mistake | Why It Fails | Fix |
|---------|-------------|-----|
| Discount too deep | Loses money on heavy users | Cap visits or raise price |
| No usage tracking | Customers feel cheated if they miss visits | Roll over unused visits |
| Complex plans | Customers can't decide | Max 3 plans |
| Hidden terms | Chargebacks, complaints | Clear upfront |

---

## 6. Launch Checklist

- [ ] Plans defined with clear pricing
- [ ] Stripe products + prices created
- [ ] Checkout flow tested end-to-end
- [ ] Usage tracking working
- [ ] Renewal emails configured
- [ ] Failed payment dunning active
- [ ] Cancel flow with retention offer
- [ ] Member portal live

---

*Specification document — not yet built.*  
*© 2026 Systack. All rights reserved.*
