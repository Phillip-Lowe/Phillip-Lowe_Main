# Utopia Deli — Meal Prep Ordering System
## Client Service Manual

**Document ID:** `UD-MP-CSM-001`  
**Version:** 1.0  
**Status:** Live  
**Prepared for:** Utopia Deli, Little Rock, AR  
**Prepared by:** Systack (systack.net)  
**Date:** 2026-06-16  
**Support:** support@systack.net | (501) 274-6231

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
| Text | Dark Gray | `#1F2937` |
| Success | Green | `#22c55e` |
| Error | Red | `#dc2626` |

---

## 1. Overview

The Utopia Deli Meal Prep System allows customers to order weekly meal packages online. Unlike the regular pickup ordering system (individual items), meal prep uses a package model: customers purchase "Weekly Meal Sets" and "Dessert Sets" in quantities they choose.

---

## 2. How the System Works

### Step 1 — Customer Views Meals

All 7 weekly meals are displayed as cards so customers can see what's available. Meals are display-only — no individual selection.

---

### Step 2 — Customer Selects Packages

Two package types:

| Package | Contents | Price |
|---------|----------|-------|
| **Weekly Meal Set** | 7 meals (one of each) | $84/set |
| **Dessert Set** | 7 dessert portions | $42/set |

Customers use +/- buttons to choose quantity. Minimum: 1 set.

---

### Step 3 — Pricing Breakdown

| Component | Calculation |
|-----------|-------------|
| Meal subtotal | $84 × number of meal sets |
| Dessert subtotal | $42 × number of dessert sets |
| Labor | $50 per meal set |
| Tax | 9.52% (Arkansas rate) |
| **Total** | Meals + Desserts + Labor + Tax |

---

### Step 4 — Checkout + Payment

Same Square payment flow as regular orders. Customer pays, receives confirmation.

---

### Step 5 — Pickup

- **Day:** Thursday
- **Time:** 12:30 PM – 7:30 PM
- **Deadline:** Orders must be placed by Wednesday

---

## 3. Key Differences from Regular Ordering

| Aspect | Regular Ordering | Meal Prep |
|--------|-----------------|-----------|
| Selection | Individual items | Package quantities |
| Pricing | Per-item | Per-set + per-set labor |
| Pickup | Any business day | Thursday only |
| Modifiers | Yes (sauces, extras) | No (fixed menu) |
| Minimum | None | 1 set |

---

## 4. Common Questions

### Can customers choose individual meals?

No — meal prep is package-based. All 7 meals are included in each Weekly Meal Set. Customers see what's in the set but can't swap items.

### What if a customer wants more of one meal?

They would need to place a regular pickup order for individual items. Meal prep is fixed-menu packages.

### When is the order deadline?

Orders must be placed by Wednesday for Thursday pickup.

---

## 5. Troubleshooting

### Pricing looks wrong

- Verify tax rate is 9.52% (not 6.5%)
- Labor is $50 per meal set (not flat)
- Each set = 7 meals

### Can't place order outside window

- Meal prep pickup is Thursday only
- Orders placed after Wednesday deadline may be blocked

---

## 6. Support

| Channel | Detail |
|---------|--------|
| **Email** | support@systack.net |
| **Phone** | (501) 274-6231 |

---

*Document prepared by Systack for Utopia Deli.*  
*© 2026 Systack. All rights reserved.*
