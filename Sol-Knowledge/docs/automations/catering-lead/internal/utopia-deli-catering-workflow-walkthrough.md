# Utopia Deli — Catering Lead System
## Workflow Walkthrough

**Document ID:** `UD-CAT-WF-001`  
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

## Workflow: Catering Lead Intake

**Webhook:** `POST https://utopia-api.systack.net/webhook/utopia-deli-catering-v2`

---

### Node 1 — Webhook

**Type:** Webhook (POST)  
**Mode:** `responseNode`

Receives 5-step form submission:

- Event type and details
- Guest count and event date
- Service style (full-service / drop-off)
- Contact info (name, email, phone)
- Special requests and budget

---

### Node 2 — Validate Fields

**Type:** Code Node

Checks:

- Required fields present (name, email, event date, guest count)
- Email format valid
- Guest count is positive number
- Event date is in the future

Returns error response if validation fails.

---

### Node 3 — Score Lead

**Type:** Code Node

Calculates weighted lead score:

| Factor | Weight | Logic |
|--------|--------|-------|
| Guest count | 40% | >100 = 100pts, 50–100 = 65pts, <50 = 30pts |
| Date proximity | 30% | <2 wks = 100pts, 2–4 wks = 65pts, >4 wks = 30pts |
| Service type | 20% | Full-service = 100pts, Drop-off = 30pts |
| Budget mentioned | 10% | Yes = 100pts, No = 0pts |

Outputs: `lead_score` (0–100), `lead_category` (high/medium/low)

---

### Node 4 — Route by Score

**Type:** Switch Node

Routes to appropriate email template:

- **High (80+):** → Node 5 (Detailed Quote)
- **Medium (50–79):** → Node 6 (Standard Info)
- **Low (<50):** → Node 7 (Basic Info)

---

### Node 5 — High Score Email

**Type:** Email Send (SMTP)

Template: Detailed catering quote

Contents:

- Personalized greeting
- Catering menu overview
- Sample pricing for guest count range
- Calendar link to schedule consultation
- Payment policy (50% deposit)
- Contact information

---

### Node 6 — Medium Score Email

**Type:** Email Send (SMTP)

Template: Standard catering information

Contents:

- Personalized greeting
- Catering services overview
- "Would you like more details?" follow-up offer
- Contact information

---

### Node 7 — Low Score Email

**Type:** Email Send (SMTP)

Template: Basic information

Contents:

- Thank you for inquiring
- Brief catering overview
- "Let us know when your plans are firmer"
- Contact information

---

### Node 8 — Log to SQLite

**Type:** SQLite Node

Inserts row into `catering_leads` table:

- Lead score and category
- Customer contact information
- Event details
- Timestamp

---

### Node 9 — Internal Notification

**Type:** Email Send (SMTP)

Sends alert to deli:

- Lead score and category
- Customer name and contact
- Event details summary
- High-score leads flagged for priority follow-up

---

## Node Chain Summary

```
Webhook (POST)
  → Validate Fields
    → Score Lead
      → Route by Score (Switch)
        ├── High → Detailed Quote Email
        ├── Medium → Standard Info Email
        └── Low → Basic Info Email
      → Log to SQLite
      → Internal Notification
      → Response Node
```

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
