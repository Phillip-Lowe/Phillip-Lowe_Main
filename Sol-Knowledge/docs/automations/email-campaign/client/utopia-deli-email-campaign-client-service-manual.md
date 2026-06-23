# Utopia Deli — Weekly Email Campaign
## Client Service Manual

**Document ID:** `UD-EMAIL-CLIENT-001`  
**Version:** 1.0  
**Status:** Client-Facing — Utopia Deli Partners  
**Source System:** Utopia Deli (Live since 2026-06-23)  
**Date:** 2026-06-23  
**Builder:** SOL

---

## What This Document Covers

This manual explains the automated Weekly Email Campaign built for The Utopia Deli. It covers what emails are sent, when they go out, and how to update content.

---

## 1. Campaign Overview

Your customers receive **5 branded emails per week** keeping them informed about meal prep deadlines, walk-up hours, catering, and special offerings.

### Why This Matters

Before this system: inconsistent communication, no reminders, customers forgot deadlines.

After this system: regular touchpoints, higher meal prep orders, better customer retention.

---

## 2. Weekly Email Schedule

| Day | Send Time | What It Says |
|-----|-----------|-------------|
| **Monday** | 9:00 AM | "We're open today + meal prep closes Wednesday" |
| **Tuesday** | 9:00 AM | "Planning an event? We cater." |
| **Wednesday** | 9:00 AM | "Last chance — meal prep closes at noon" |
| **Thursday** | 9:00 AM | "Pick up your bowls today + we're open" |
| **Friday** | 9:00 AM | "New week meal prep is live" |

### What Each Email Includes

- **Branded header** with Utopia Deli logo
- **Hero image** of food
- **Clear call-to-action** button (Order Now, Get Quote, etc.)
- **Photos of actual dishes** with descriptions
- **Your address and hours**
- **Unsubscribe link** (required by law)

---

## 3. How It Works

### Automatic Process (No Manual Work)

1. **n8n** (automation platform) sends emails automatically
2. **Customer database** pulls from Square + website orders
3. **Templates** generate branded HTML emails
4. **Gmail SMTP** delivers emails to ~300 customers
5. **Logs** track what was sent and when

### What You Don't Have to Do

- ❌ Manually send emails
- ❌ Build email templates
- ❌ Manage unsubscribes
- ❌ Format images or content

### What You Still Control

- ✅ Weekly bowl names and descriptions
- ✅ Special announcements (holidays, events)
- ✅ Catering availability
- ✅ Menu updates

---

## 4. Weekly Update Process

### Every Week (Takes 5 Minutes)

**Step 1:** Tell us this week's 7 bowl names
- Example: "Mediterranean Harvest, Thai Peanut Crunch, Eggplant Parm..."

**Step 2:** Send any new food photos (or we'll reuse existing)

**Step 3:** We update the code and activate the campaign

**Done.** Emails send automatically all week.

### What Happens Automatically

- Monday email: Uses current week bowls
- Tuesday email: Catering focus (same each week)
- Wednesday email: Urgency reminder (same each week)
- Thursday email: Pickup reminder (same each week)
- Friday email: New week preview (uses next week's bowls)

---

## 5. Current Menu Items (as of June 2026)

### Meal Prep Bowls ($12 each)

| Bowl | Description | Calories |
|------|-------------|----------|
| Mediterranean Harvest Bowl | Lemon herb quinoa, crispy oregano chickpeas, cucumber tomato salad, hummus, tahini drizzle, pickled red onion | 500 |
| Thai Peanut Crunch Bowl | Jasmine rice, crispy peanut tofu, sesame cabbage slaw, sweet chili peanut drizzle | 490 |
| Eggplant Parmesan | Parmesan crusted eggplant layered with homemade marinara, topped with fresh basil | 530 |
| Cajun Red Beans & Dirty Rice Bowl | Dirty rice, Cajun beans, peppers & onions, green onion garnish | 460 |
| Street Corn Taco Bowl | Cilantro lime rice, chipotle lentil crumble, roasted corn, black beans, pickled onions, chipotle crema | 470 |
| Nashville Hot Lentil Bowl | Garlic rice, Nashville hot lentils, roasted broccoli, ranch drizzle | 480 |
| Loaded BBQ Potato Bowl | Roasted potatoes, BBQ lentil crumble, broccoli, smoked cheeze sauce, green onions | 510 |

### Add-Ons

| Item | Description | Price |
|------|-------------|-------|
| Raspberry Dark Chocolate Mousse | Rich dark chocolate mousse topped with fresh raspberries — sugar free | $5 |
| Cold-Pressed Juice | Fresh 10oz juice | $5 |

### Walk-Up Menu

| Item | Description |
|------|-------------|
| Stek Philly | Thin-cut steak, peppers, onions, hoagie roll |
| Chick'n Poppers | Crispy dippers — BBQ, Garlic Parm, Jerk, Buffalo, Lemon Pepper |
| Loaded Bac'n Fry | Crinkle-cut fries loaded with bac'n, cheeze sauce |
| Chocolate Chip Cookies | Two fresh-baked cookies |

---

## 6. Important Details

### Meal Prep Schedule

- **Opens:** Thursday 8:00 PM
- **Closes:** Wednesday 12:00 PM (noon)
- **Pickup:** Thursday 12:30 PM – 7:30 PM
- **Location:** 801 S Chester St, Little Rock, AR 72202

### Walk-Up Hours

- **When:** Monday – Saturday
- **Hours:** 12:30 PM – 7:30 PM
- **How:** Order online for pickup (recommended) or walk up

### Catering

- **Minimum:** 10 guests
- **Notice:** 3 days advance
- **Deposit:** 50% to book
- **Options:** Drop-off, staffed buffet, or full-service

---

## 7. Customer List

**Current Size:** ~300 email subscribers

**Where They Come From:**
- Square POS transactions (customers who provided email)
- Website orders (pickup-order, catering)
- Manual additions

**Growth:** List grows automatically with each order.

---

## 8. Compliance (TCPA/CAN-SPAM)

### What We've Done

- ✅ Consent text on order forms
- ✅ Privacy page explaining email usage
- ✅ Unsubscribe link in every email
- ✅ Unsubscribe requests processed automatically
- ✅ Customer data stored securely

### Customer Rights

Customers can:
- Unsubscribe from emails anytime
- Request data deletion
- Opt-out of SMS (when SMS is added)

---

## 9. What to Expect

### Week 1-2: Baseline
- Monitor delivery rates
- Check for customer feedback
- Watch unsubscribe rate (should be <1%)

### Month 1: Patterns
- Identify best-performing emails
- Adjust send times if needed
- Add/remove content based on engagement

### Ongoing: Optimization
- Rotate bowl descriptions seasonally
- Update hero images with fresh photos
- Add community spotlight content

---

## 10. Support & Updates

### If You Need Changes

**Text/call:** Phillip Lowe (SOL/Systack)
**Email:** theutopiadelilittlerock@gmail.com
**Turnaround:** Updates typically same day

### What We Can Change Quickly

- Bowl names/descriptions
- Hero images
- Special announcements (events, closures)
- Send times

### What Takes Longer

- New email template designs
- Additional email days
- Advanced segmentation
- SMS integration

---

## Summary

You now have an automated system that:
- Sends 5 branded emails per week
- Reminds customers about meal prep deadlines
- Promotes catering services
- Keeps your business top-of-mind
- Requires minimal weekly maintenance

**Your only job:** Tell us the bowl lineup each week.

**Everything else:** Automated.

---

**End of Document**

*Questions? Contact Phillip Lowe or the Systack team.*
