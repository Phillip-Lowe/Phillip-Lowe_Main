# Deli System Status — Current State

**Last Updated:** 2026-07-12 22:53 CDT
**Repo:** `Phillip-Lowe/utopia-deli`
**Live Site:** https://order.theutopiadeli.com

---

## Menu Status

### Sandwiches (4 items) — ✅ LIVE
| Item | ID | Price | Status |
|------|-----|-------|--------|
| Cowboy Chik'n Sandwich | COWBOY | $13.00 | ✅ Available |
| Chik'n Club Sub | CLUB | $15.00 | ✅ Available |
| Chik'n Fried Chik'n Sub | FRIED | $13.00 | ✅ Available |
| Philly Sub | PHILLY | $13.00 | ✅ Available |

### Specialties (4 items) — ✅ LIVE
| Item | ID | Price | Status |
|------|-----|-------|--------|
| Chik'n Poppers | POPPERS | $10.00 | ✅ Available |
| Korean Pork Dumpling Tacos | DUMPLING_TACOS | $10.00 | ✅ Available |
| Rocktown Bourbon Chik'n Sliders | ROCKTOWN_SLIDERS | $12.00 | ✅ Available |
| Buffalo Chik'n Sliders | BUFFALO_SLIDERS | $12.00 | ✅ Available |

### Sides (5 items) — ✅ LIVE (Juice Hidden)
| Item | ID | Price | Status |
|------|-----|-------|--------|
| Fries | FRIES | $5.00 | ✅ Available |
| **Fresh Cold-Pressed Juice** | **JUICE_CP** | **$5.00** | **⏸️ TEMPORARILY REMOVED** |
| Two Fresh Baked Chocolate Chip Cookies | COOKIES_2 | $4.00 | ✅ Available |
| Side Salad | SIDE_SALAD | $5.00 | ✅ Available |
| 16 oz Bottled Water | WATER_16OZ | $2.00 | ✅ Available |
| Potato Chip Spirals | CHIPS_SPIRALS | $5.00 | ✅ Available |

### Meal Prep (Catering Page) — ✅ LIVE (Juice Hidden)
- **6 rotating weekly meals** — all active
- **Apple Pie dessert** — ✅ Available
- **Fresh Cold-Pressed Juice** — ⏸️ TEMPORARILY REMOVED (was $5.00, 10 oz)

---

## Recent Changes

### 2026-07-12 — Fresh Pressed Juice Temporarily Removed
**Reason:** Out of stock
**Files Modified:**
- `pickup-order/menu-data.js` — `JUICE_CP` item commented out
- `catering/catering-form.js` — `cold-pressed-juice` drink commented out
**Commit:** `8fd5926`
**Note:** Both items preserved with `TEMPORARILY REMOVED` comments. Easy restoration when stock returns.

---

## System Health

| Component | Status |
|-----------|--------|
| GitHub Pages Deployment | ✅ Active |
| n8n Webhook (order-v4) | ✅ Active |
| Square Integration | ✅ Active |
| Image Assets | ✅ All present |
| Modifier System | ✅ Functional |

---

## To Restore Juices
1. Uncomment `JUICE_CP` block in `pickup-order/menu-data.js`
2. Uncomment `cold-pressed-juice` in `catering/catering-form.js` DRINKS array
3. Commit and push

---

**Everything else in the deli system is working correctly.**
