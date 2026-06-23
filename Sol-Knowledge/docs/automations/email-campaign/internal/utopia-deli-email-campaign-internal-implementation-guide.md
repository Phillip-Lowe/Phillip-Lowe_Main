# Utopia Deli — Weekly Email Campaign
## Internal Implementation Guide

**Document ID:** `UD-EMAIL-001`  
**Version:** 1.0  
**Status:** Internal — Systack Only  
**Source System:** Utopia Deli (Live since 2026-06-23)  
**Date:** 2026-06-23  
**Builder:** SOL

---

## Brand Reference

| Role | Color | Hex |
|------|-------|-----|
| Headers, CTAs | Deep Burgundy | `#590B3F` |
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

## 1. System Overview

The Utopia Deli Weekly Email Campaign is a 5-day automated email system that sends branded marketing emails to the customer database. It replaces ad-hoc messaging with a consistent, scheduled communication rhythm.

### Campaign Schedule

| Day | Send Time | Email Type | Focus |
|-----|-----------|-----------|-------|
| **Monday** | 9:00 AM | "We're Open + Meal Prep Closes Wed" | Walk-up open 12:30-7:30 + meal prep urgency |
| **Tuesday** | 9:00 AM | Catering Push | Events, parties, corporate |
| **Wednesday** | 9:00 AM | "Last Call — Closes at Noon" | Final meal prep hours + we're open |
| **Thursday** | 9:00 AM | "Pick Up Your Bowls" | Meal prep pickup + walk-up open + catering tease |
| **Friday** | 9:00 AM | "New Week Fresh Bowls" | New meal prep week opens + weekend hours |

### Business Logic

- **Meal Prep Cycle:** Opens Thursday 8:00 PM → Closes Wednesday 12:00 PM → Pickup Thursday 12:30-7:30 PM
- **Walk-Up Hours:** Monday-Saturday 12:30 PM - 7:30 PM
- **Email Frequency:** 5 emails/week (reduced from 7 to avoid fatigue)
- **Segmentation:** None currently — blast to full list

---

## 2. Technical Architecture

```
n8n Schedule Trigger (Daily 9AM)
  → Set Day & Week (Code Node)
    → Route by Day (Switch Node)
      → Day-Specific Template (Code Node)
        → Postgres Contact Lookup
          → Filter Unsubscribed
            → SMTP Email Send (Gmail)
              → Log to message_logs
                → Done
```

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Scheduler | n8n Schedule Trigger | Daily 9:00 AM CST |
| Day Router | n8n Code Node | Determine which template to send |
| Templates | JavaScript (Function Node) | HTML email generation |
| Contact DB | PostgreSQL | Customer list with consent flags |
| Email Send | SMTP (Gmail) | Deliver emails with 20s throttle |
| Logging | PostgreSQL | Track sends, opens, bounces |

---

## 3. Email Template Structure

All templates use the same base structure:

### Header
- Deep burgundy background (`#590B3F`)
- Utopia Deli logo left-aligned
- "The Utopia Deli" text in Georgia serif

### Body
- White background
- Hero image (day-specific)
- Headline in Georgia serif, burgundy (`#590B3F`)
- Body text in Georgia serif, dark gray (`#1F2937`)
- CTA button in rust red (`#AF3D4B`)
- Dish cards with images/descriptions
- "How It Works" info box (light gray background)

### Footer
- Light gray background (`#f8f6f4`)
- Address: 801 S Chester St, Little Rock, AR 72202
- Unsubscribe link (tracks via webhook)

---

## 4. Contact Database

**Table:** `public.contacts`

| Column | Type | Notes |
|--------|------|-------|
| id | integer | Primary key |
| square_id | varchar(255) | Square customer ID |
| name | varchar(255) | Customer name |
| email | varchar(255) | Email address |
| phone | varchar(50) | Phone number |
| consent_status | varchar(50) | 'implicit' default |
| unsubscribed_email | boolean | false default |
| unsubscribed_sms | boolean | false default |
| last_order_date | timestamp | From Square sync |
| order_count | integer | From Square sync |

**Current Stats:**
- Total contacts: 356
- With email: 333
- With phone: 256
- With both: 233

---

## 5. SMTP Configuration

**Provider:** Gmail (theutopiadelilittlerock@gmail.com)
**Authentication:** App Password (stored in macOS Keychain)
**Rate Limiting:** 20 seconds between sends (prevents "sent too many" errors)

### Throttle Settings

| Setting | Value | Rationale |
|---------|-------|-----------|
| Delay between sends | 20 seconds | Gmail SMTP rate limit |
| Max emails/hour | ~180 | 3600s / 20s = 180/hour |
| Batch size | Full list | Sent sequentially with delay |

**Note:** Previously used 10-second delay. Triggered "sent too many" error at ~250 sends. Increased to 20s resolved issue.

---

## 6. File Locations

### Source Code

| File | Purpose |
|------|---------|
| `email-campaign/utopia-deli-5day-campaign.js` | **Master template** — paste into n8n Function node |
| `email-campaign/utopia-deli-all-days.js` | Legacy 7-day template (kept for reference) |
| `email-campaign/utopia-deli-weekly-email-campaign.json` | n8n workflow export (incomplete) |

### Images

| File | Description |
|------|-------------|
| `email-campaign/catering-1.jpg` | Baked ziti/lasagna (catering) |
| `email-campaign/catering-2.jpg` | Glazed donuts (catering) |
| `email-campaign/catering-3.jpg` | Full catering spread |
| `email-campaign/catering-4.jpg` | Fresh fruit platter |

### Documentation

| File | Purpose |
|------|---------|
| `email-campaign/PRODUCTION-NOTES.md` | Weekly checklist, known issues |
| `email-campaign/README.md` | Campaign overview |
| `memory/2026-06-23-utopia-deli-email-production-sent.md` | Production deployment log |

---

## 7. Weekly Update Process

### Before Each Week

1. **Update bowl names/descriptions** in `utopia-deli-5day-campaign.js`
2. **Update images** if new photos available
3. **Test send** to internal email first
4. **Paste updated code** into n8n Function node
5. **Activate workflow** for the week

### Monday Morning Checklist

- [ ] Verify meal prep closing time hasn't changed
- [ ] Check walk-up hours (holiday schedule?)
- [ ] Confirm email sent successfully
- [ ] Monitor unsubscribe rate

### Wednesday Morning Checklist

- [ ] Verify meal prep actually closes at noon
- [ ] Check pickup time for Thursday
- [ ] Confirm email sent successfully

---

## 8. Troubleshooting

### "Sent too many" Error

**Symptom:** SMTP node fails with "sent too many" after ~250 emails
**Cause:** Gmail rate limiting
**Fix:** Increase delay node from 10s to 20s between sends
**Prevention:** Always use 20s+ delay for lists >200 contacts

### Images Not Loading

**Symptom:** Email shows broken image icons
**Cause:** GitHub raw URLs may change or images may be moved
**Fix:** Verify image URLs in browser. Use `order.theutopiadeli.com` hosting for production.

### Unsubscribe Not Working

**Symptom:** Unsubscribe link returns 404
**Cause:** Webhook URL may have changed
**Fix:** Verify `https://n8n.systack.net/webhook/unsubscribe` is active

---

## 9. Production Notes

### First Send: 2026-06-23

- **Test email:** Sent 10:28 CDT — SUCCESS
- **Production send:** Sent 10:30 CDT — SUCCESS
- **Recipients:** ~300 contacts
- **Issues:** SMTP throttling (fixed with 20s delay)
- **Result:** All emails delivered successfully

### Known Issues

1. **Missing images for 3 bowls:** Street Corn Taco, Nashville Hot Lentil, Loaded BBQ Potato (using emoji placeholders)
2. **No segmentation:** All contacts get all emails
3. **No open/click tracking:** Basic SMTP only, no analytics
4. **Manual weekly updates:** Bowl names must be edited in code weekly

### Future Improvements

- [ ] Build Google Sheets integration for easier weekly updates
- [ ] Add open/click tracking (SendGrid, Postmark, etc.)
- [ ] Segment by order frequency (regulars vs. lapsed)
- [ ] Add A/B testing for subject lines
- [ ] Automate image rotation based on availability

---

**End of Document**

*For questions or updates, contact SOL or update this document directly.*
