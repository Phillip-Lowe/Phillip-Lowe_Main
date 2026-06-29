# Utopia Deli — Meal Prep Ordering System
## Internal Implementation Guide

**Document ID:** `UD-MP-IMPL-001`  
**Version:** 1.1  
**Status:** Internal — Systack Only  
**Source System:** Utopia Deli (Live since 2026-06-15)  
**Date:** 2026-06-29  
**Builder:** SOL / Assembly

---

## Brand Reference

| Role | Color | Hex |
|------|-------|-----|
| Primary | Deep Burgundy | `#590B3F` |
| Primary Light | Burgundy Light | `#7a1a55` |
| Accent | Rust Red | `#AF3D4B` |
| Secondary | Purple | `#754681` |
| Gold | Warm Gold | `#D59F5C` |

---

## 1. System Architecture

```
Customer visits meal-prep page
  → Views 7 meal cards (display only)
    → Selects package quantities (+/- buttons)
      → Pricing: $84/meal set + $42/dessert set + $50 labor/set
        → Checkout via Square
          → Confirmation page (meal-prep variant)
            → Pickup: Thursday 12:30–7:30 PM
```

---

## 2. Core Components

### Frontend

- **File:** `catering/catering-form.js` (shared with catering lead system)
- **Key constants:**
  - `MEALS_PER_PACKAGE = 7`
  - `MEAL_SET_PRICE = 84` (dollars)
  - `DESSERT_SET_PRICE = 42` (dollars)
  - `LABOR_PER_SET = 50` (dollars)

### Package Functions

```javascript
function addWeeklyPackage() {
  weeklySets++;
  updateMPTotals();
}

function removeWeeklyPackage() {
  if (weeklySets > 0) weeklySets--;
  updateMPTotals();
}

function addDessertPackage() {
  dessertSets++;
  updateMPTotals();
}

function removeDessertPackage() {
  if (dessertSets > 0) dessertSets--;
  updateMPTotals();
}
```

### Pricing Calculation

```javascript
function updateMPTotals() {
  const mealSubtotal = weeklySets * MEAL_SET_PRICE;
  const dessertSubtotal = dessertSets * DESSERT_SET_PRICE;
  const laborTotal = weeklySets * LABOR_PER_SET;
  const subtotal = mealSubtotal + dessertSubtotal + laborTotal;
  const tax = subtotal * 0.0952;
  const total = subtotal + tax;
}
```

---

## 3. Setup Process (Replication)

### Step 1 — Deploy Meal Prep Page

- Copy meal prep HTML/JS to client domain
- Configure package pricing constants
- Set pickup day and deadline

### Step 2 — Configure n8n

- Meal prep uses same Square checkout workflow as regular orders
- Different redirect URL: `payment-confirmed-meal-prep/`
- Order source tag: `meal-prep`

### Step 3 — Set Business Rules

- Minimum: 1 meal set
- Pickup: Thursday only
- Deadline: Wednesday
- Labor: per-set (not flat)

---

## 4. Critical Constraints

| Constraint | Detail |
|------------|--------|
| **Package model** | No individual meal selection — sets only |
| **Labor scaling** | $50 per meal set, not flat |
| **Tax rate** | 9.52% (not 6.5% — was mislabeled) |
| **Meals per set** | 7 (was 6 before 2026-06-15 fix) |
| **Pickup day** | Thursday only |

---

## 5. Known Pitfalls (All Fixed)

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Tax label 6.5% but calc 9.52% | Customer confusion | Corrected label to 9.52% |
| Flat $50 labor | Unfair for multi-set orders | Changed to $50/set |
| 6 meals per set | Wrong package size | Changed to 7 |
| Individual meal toggles | Confusing UX | Replaced with package +/- |

---

## 6. Production Fix Log (2026-06-29)

### Bug: Submit Button Shows Error After Order Processes

**Symptom:** Customer clicks "Pay & Place Order" → order processes in n8n → Square link created → email sent → DB saved → but browser shows "Something went wrong"

**Root Causes:**
1. **Frontend:** `mp-pickup` element referenced in JS but never existed in HTML → null reference crash before fetch
2. **n8n Workflow:** `MP Format Response1` node not connected to `Respond to Webhook` node → empty HTTP response

**Fixes Applied:**

| Fix | File | Detail |
|-----|------|--------|
| Hardcode pickup time | `catering/catering-form.js` | `pickup = 'Thursday 12:30 PM - 7:30 PM'` |
| Fix payload format | `catering/catering-form.js` | Match meal-prep branch: `body.pricing.subtotal/labor/tax/total`, `items` with `qty` + `price` |
| Connect response node | n8n workflow | Wire `MP Format Response1` → `Respond to Webhook` |

**Commits:** `98f792d`, `92ec9a0`

**Verification:**
- ✅ Order submits successfully
- ✅ Square payment link returned in response  
- ✅ Browser redirects to payment page
- ✅ Confirmation email sent
- ✅ Order saved to database

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
