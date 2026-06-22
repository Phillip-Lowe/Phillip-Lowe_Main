# Utopia Deli — Weekly Email Campaign System
## Complete Content Calendar + Templates

---

## NEW MEAL PREP SCHEDULE (Effective Immediately)

| Event | Time |
|-------|------|
| Orders CLOSE | Every Wednesday at 12:00 PM (noon) |
| Orders REOPEN | Every Thursday at 8:00 PM |
| Pickup | Thursday 12:30 PM – 7:30 PM |
| **Week Start** | Thursday (when orders reopen) |

> ⚠️ **Critical:** Update ALL deadline text from "Wednesday noon, pickup Thursday" → "Closes Wednesday noon, reopens Thursday 8 PM"

---

## WEEKLY EMAIL CALENDAR

| Day | Focus | Template File | Purpose |
|-----|-------|---------------|---------|
| **Monday** | Item of the Week | `monday-item-of-week.js` | Spotlight one dish/menu item |
| **Tuesday** | Catering Push | `tuesday-catering.js` | Events, corporate, pickup platters (rotating) |
| **Wednesday** | Meal Prep Deadline | `wednesday-meal-prep-close.js` | "Closes today at noon" urgency |
| **Thursday** | Meal Prep Reopen + Regular Deli | `thursday-reopen.js` | "We're back!" + daily menu highlights |
| **Friday** | Weekend Vibes | `friday-weekend.js` | Walk-ups, specials, atmosphere |
| **Saturday** | Weekend Reminder | `saturday-weekend.js` | "We're open today!" |
| **Sunday** | This Week Preview | `sunday-preview.js` | Next week's meal prep menu + Monday lunch tease |

---

## IMAGE ASSET REFERENCE

### Meal Prep (catering/images/)
```
meal-mediterranean-harvest.jpg    → Mediterranean Harvest Bowl
meal-thai-peanut-crunch.jpg       → Thai Peanut Crunch Bowl
meal-eggplant-parm.jpg            → Eggplant Parmesan
meal-buffalo-chickpea.jpg         → Buffalo Chickpea Ranch Bowl
meal-teriyaki-tofu.jpg            → Teriyaki Tofu Bowl
meal-red-lentil-masala.jpg        → Red Lentil Coconut Masala
meal-peanut-ginger.jpg            → Peanut Ginger Bowl
meal-cajun-northern-beans.jpg      → Cajun Northern Beans & Rice
meal-rainbow-bbq-tofu.jpg         → Rainbow BBQ Tofu Wild Rice
```

### Desserts (catering/images/)
```
dessert-raspberry-mousse.jpg      → Raspberry Dark Chocolate Mousse
dessert-mango-chia.jpg            → Mango Chia Seed Pudding
apple-pie.jpg                     → Apple Pie
```

### Regular Menu (images/menu/)
```
stek Philly.jpg                   → Stek Philly
chicken_fried_chikn_sub.png      → Chik'n Fried Chik'n Sub
buffalo_chikn_slider.jpg          → Buffalo Chik'n Sliders
rocktown_bourbon_slider.jpg       → Rocktown Bourbon Sliders
chicken_poppers_v3.jpg            → Chick'n Poppers
loaded_bacon_fry.jpg              → Loaded Bac'n Fry
garlic_parm_fries_v2.jpg          → Garlic Parm Fries
korean_pork_dumpling_tacos.jpg    → Korean Pork Dumpling Tacos
cowboy_chicken.webp               → Cowboy Chicken
cold_pressed_juice_v2.jpg         → Cold-Pressed Juice
cookies_v2.jpg                    → Chocolate Chip Cookies
```

### Catering (images/)
```
Deli Catering Salad.jpg           → Catering Salad Display
Deli Catering Fruit Salad.jpg     → Fruit Salad
```

### Lifestyle/Hero (images/)
```
Deli Happy customer lady.jpg      → Happy customer (weekend vibes)
Deli Meal Prep Plate 1.jpg        → Meal prep hero shot
```

---

## TUESDAY CATERING ROTATION (3-Week Cycle)

| Week | Focus | Subject Line |
|------|-------|--------------|
| **Week 1** | Events & Parties | "🎉 Planning an Event? Let's Cater It" |
| **Week 2** | Corporate / Office | "🏢 Feed Your Team — Corporate Catering" |
| **Week 3** | Pickup Platters | "🍽️ Pickup Platters — Easy & Delicious" |

---

## SUNDAY PREVIEW STRUCTURE

Every Sunday email includes:
1. **This Week's Meal Prep Menu** (6 bowls + rotating spotlight)
2. **Monday Lunch Tease** — "Get lunch tomorrow" with 2-3 items
3. **What's Happening This Week** — optional, only if there's something special

---

## N8N WORKFLOW SETUP

### Option A: Single Workflow with Day Router
```
Trigger (Schedule: Daily 9:00 AM)
  → Switch on day_of_week
    → monday → monday template
    → tuesday → tuesday template (cycle through 3 variants)
    → wednesday → wednesday template
    → thursday → thursday template
    → friday → friday template
    → saturday → saturday template
    → sunday → sunday template
```

### Option B: Separate Workflows (Recommended)
- Easier to manage
- Can pause individual days
- Independent analytics

---

## SWAP INSTRUCTIONS

Each template has these **SWAP ZONES** marked with comments:

```javascript
// ═══════════════════════════════════════════
// SWAP ZONE: Week of [DATE]
// Update these items weekly
// ═══════════════════════════════════════════
```

Look for that pattern in each file.

---

## FILES IN THIS PACKAGE

| File | Description |
|------|-------------|
| `README.md` | This file — overview & calendar |
| `monday-item-of-week.js` | Monday: Item spotlight template |
| `tuesday-catering.js` | Tuesday: Catering (3 variants) |
| `wednesday-meal-prep-close.js` | Wednesday: Deadline urgency |
| `thursday-reopen.js` | Thursday: Reopen + daily menu |
| `friday-weekend.js` | Friday: Weekend kickoff |
| `saturday-weekend.js` | Saturday: Weekend reminder |
| `sunday-preview.js` | Sunday: Next week preview |

---

## NEXT STEPS

1. ✅ Copy each `.js` file content into n8n Function nodes
2. ✅ Update image URLs to your actual CDN paths
3. ✅ Set up n8n workflow triggers (daily at 9 AM)
4. ✅ Test with your email list (send to yourself first)
5. ✅ Weekly: Update SWAP ZONE content before Monday

---

**Built for:** The Utopia Deli
**Location:** 801 S Chester St, Little Rock, AR 72202
**Contact:** (501) 551-5944
**Order:** https://order.theutopiadeli.com
