# Systack — Generic Booking System
## Internal Implementation Guide

**Automation ID:** `generic-booking`  
**Version:** 1.0  
**Status:** Template — Ready for Deployment  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## Brand Reference

| Role | Color | Hex |
|------|-------|-----|
| Headers, CTAs | Navy | `#001a2d` |
| Secondary accents | Teal | `#007da9` |
| Primary buttons, links | Cyan | `#00a1db` |
| Body text | Gray 600 | `#475569` |
| Headings | Gray 800 | `#1e293b` |
| Success | Green | `#22c55e` |
| Error | Red | `#ef4444` |

---

## 1. Overview

White-label booking system template. Booking form → payment (Stripe) → database logging → confirmation email. The foundation that gets customized per client. Available in Private and Accelerate tiers.

**Templates:**
- `templates/private/n8n-generic-booking.json`
- `templates/accelerate/n8n-generic-booking.json`

---

## 2. System Architecture

```
Customer visits booking page
  → Selects service + time slot
    → Enters contact info
      → Payment via Stripe
        → Booking logged to Postgres
          → Confirmation email sent
            → Internal notification
```

---

## 3. Tier Comparison

| Component | Private | Accelerate |
|-----------|---------|------------|
| Payment | Stripe (client account) | Stripe (client account) |
| Booking log | Postgres local | Postgres cloud VPS |
| Notifications | SMS (Twilio) | Slack + email |
| Customer receipt | Local SMTP | SendGrid/GMail |

---

## 4. Customization Points

| Element | What to Change |
|---------|---------------|
| Services | Service types, durations, pricing |
| Time slots | Business hours, slot intervals |
| Branding | Logo, colors, copy |
| Payment | Stripe credentials |
| Notifications | Email/SMS/Slack channels |

---

## 5. Setup Process

### Step 1 — Choose Tier

- Private: on-premise, zero cloud
- Accelerate: cloud Postgres, Slack, Google

### Step 2 — Import + Configure

- Import workflow JSON into n8n
- Set Stripe credentials
- Configure Postgres connection
- Set notification channels

### Step 3 — Deploy Frontend

- Customize booking form HTML/CSS/JS
- Deploy to client domain
- Point form to n8n webhook

### Step 4 — Test

- Complete test booking
- Verify payment processes
- Check database logging
- Confirm notifications deliver

---

## 6. Integration Points

This template is the foundation for:
- No-Show Prevention (adds deposit + reminders)
- Smart Rebooking (adds cycle tracking)
- CRM Lite (adds customer profiles)
- Upsell Intelligence (adds dynamic upsells)

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
