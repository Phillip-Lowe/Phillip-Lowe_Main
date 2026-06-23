# Utopia Deli Weekly Email Campaign — Production Notes

**Date:** 2026-06-23 (Updated)  
**Status:** ✅ PRODUCTION LIVE — Successfully sent to ~300 recipients
**Files:**
- Master: `email-campaign/utopia-deli-5day-campaign.js`
- Legacy: `email-campaign/utopia-deli-all-days.js`

---

## 📧 What's Built (5-Day Campaign)

| Day | Subject | Focus |
|-----|---------|-------|
| Monday | 🍽️ We're Open + Meal Prep Closes Wed | Walk-up open + meal prep urgency |
| Tuesday | 🎉 Planning an Event? | Catering push with real images |
| Wednesday | ⏰ Closes Today at Noon | Final hours + we're open |
| Thursday | 📦 Pick Up Your Bowls | Pickup reminder + walk-up + catering |
| Friday | 🍱 New Week Fresh Bowls | New meal prep week + weekend hours |

**Schedule:**
- Meal prep orders: Close Wed 12:00 PM → Reopen Thu 8:00 PM → Pickup Thu 12:30–7:30
- Walk-up: Monday–Saturday 12:30 PM – 7:30 PM

**Production Deployment:**
- **Test send:** 2026-06-23 10:28 CDT — SUCCESS
- **Production send:** 2026-06-23 10:30 CDT — SUCCESS (after fixing SMTP throttle)

---

## ⚠️ SMTP THROTTLE LESSON (CRITICAL)

**Problem:** "Sent too many" error during bulk send
**Cause:** Gmail SMTP rate limits
**Fix:** Changed n8n delay from 10 seconds → 20 seconds between sends
**Result:** Campaign completed successfully

**Rule:** Always use 20s+ delay for lists >200 contacts. Test with small batches first.

---

## 📊 Current Bowl Lineup (7 Bowls)

| Bowl | Description | Calories | Image? |
|------|-------------|----------|--------|
| Mediterranean Harvest Bowl | Lemon herb quinoa, crispy oregano chickpeas, cucumber tomato salad, hummus, tahini drizzle, pickled red onion | 500 | ✅ |
| Thai Peanut Crunch Bowl | Jasmine rice, crispy peanut tofu, sesame cabbage slaw, sweet chili peanut drizzle | 490 | ✅ |
| Eggplant Parmesan | Parmesan crusted eggplant layered with homemade marinara, topped with fresh basil | 530 | ✅ |
| Cajun Red Beans & Dirty Rice Bowl | Dirty rice, Cajun beans, peppers & onions, green onion garnish | 460 | ✅ |
| Street Corn Taco Bowl | Cilantro lime rice, chipotle lentil crumble, roasted corn, black beans, pickled onions, chipotle crema | 470 | ❌ (no image yet) |
| Nashville Hot Lentil Bowl | Garlic rice, Nashville hot lentils, roasted broccoli, ranch drizzle | 480 | ❌ (no image yet) |
| Loaded BBQ Potato Bowl | Roasted potatoes, BBQ lentil crumble, broccoli, smoked cheeze sauce, green onions | 510 | ❌ (no image yet) |

**Missing images:** 3 bowls need photos. Currently showing only bowls with images in emails.

---

## 📝 Weekly Update Checklist

| Day | Issue |
|-----|-------|
| **Monday** | "How Meal Prep Works" section — verify pickup times match current schedule |
| **Tuesday** | Catering descriptions are generic — update based on actual offerings |
| **Wednesday** | "Meal Prep Favorites" — need actual current bowls |
| **Thursday** | "Next Week's Bowls" section — need actual next week lineup |
| **Sunday** | "This Week's Menu" — need all 6 bowls with real descriptions |

---

## 📝 Weekly Update Checklist

Before sending each week, verify:

- [ ] **Images** — All 6 meal prep bowl photos match current menu
- [ ] **Bowl names** — Match what's actually being offered this week
- [ ] **Descriptions** — Accurate ingredients/flavors for each bowl
- [ ] **Add-ons** — Desserts and juices in stock
- [ ] **Schedule** — Pickup times, order deadlines haven't changed
- [ ] **Hero images** — Monday, Thursday, Sunday need fresh/relevant shots
- [ ] **Links** — URLs still work (catering page, pickup-order page)

---

## 📂 File Locations

| File | Purpose |
|------|---------|
| `email-campaign/utopia-deli-all-days.js` | **Master file** — copy into n8n Function node |
| `email-campaign/utopia-deli-weekly-email-campaign.json` | Combined workflow JSON (if using routing) |
| `email-campaign/monday-item-of-week.js` | Standalone Monday (backup) |
| `email-campaign/tuesday-catering.js` | Standalone Tuesday (backup) |
| `email-campaign/wednesday-meal-prep-close.js` | Standalone Wednesday (backup) |
| `email-campaign/thursday-reopen.js` | Standalone Thursday (backup) |
| `email-campaign/friday-weekend.js` | Standalone Friday (backup) |
| `email-campaign/saturday-weekend.js` | Standalone Saturday (backup) |
| `email-campaign/sunday-preview.js` | Standalone Sunday (backup) |

---

## 🔄 How to Use

1. **Open** `utopia-deli-all-days.js`
2. **Edit** the `images` object at the top — swap URLs for current week
3. **Edit** each day's template body — update descriptions, bowl names
4. **Copy entire file** into n8n Function node
5. **Test** with your own email first
6. **Send**

---

## 🗓️ Future Improvements

- Build a proper CMS/sheet-driven system where Phillip updates a Google Sheet and the email auto-pulls from it
- Set up image hosting with consistent naming (e.g., `bowls/week-of-06-22/...`)
- Create a simple "weekly update" form that generates the code automatically

---

**Saved by:** SOL  
**Session:** 2026-06-22 ~10:00 CDT  
**Status:** Ready for testing, needs weekly content updates
