# Utopia Deli — Online Ordering System
## Internal Implementation Guide

**Document ID:** `UD-IMPL-001`  
**Version:** 1.0  
**Status:** Internal — Systack Only  
**Source System:** Utopia Deli (Live since 2026-06-03)  
**Date:** 2026-06-29  
**Builder:** SOL / Assembly

---

## Brand Reference

| Role | Color | Hex |
|------|-------|-----|
| Headers, CTAs | Navy | `#001a2d` |
| Navy Light | Navy Light | `#002845` |
| Secondary accents | Teal | `#007da9` |
| Primary buttons, links | Cyan | `#00a1db` |
| Gradients | Cyan Bright | `#00c5e0` |
| Backgrounds | Gray 50 | `#f8fafc` |
| Cards | Gray 100 | `#f1f5f9` |
| Borders | Gray 200 | `#e2e8f0` |
| Muted text | Gray 400 | `#94a3b8` |
| Body text | Gray 600 | `#475569` |
| Headings | Gray 800 | `#1e293b` |
| Success | Green | `#22c55e` |
| Error | Red | `#ef4444` |
| Accent highlights | Purple | `#8b5cf6` |

---

## 1. System Architecture

```
Frontend (HTML/JS)
  → n8n Webhook
    → Validation + Normalization
      → Business Logic (hours, totals)
        → Order ID generation
          → Square Checkout Link
            → Payment (Square)
              → Square Webhook
                → n8n Confirmation Workflow
                  → Kitchen Notification + Customer Email
```

---

## 2. Core Components

### Frontend

- Static HTML ordering page
- Sends POST request to webhook
- Handles redirect to Square

---

### n8n Workflow (Order Intake)

**Workflow ID:** `Utopia-Deli-Simple-Checkout-v4`

Key nodes:

| # | Node | Purpose |
|---|------|---------|
| 1 | Webhook (POST) | Receives order data from frontend |
| 2 | Validate + Normalize (Code Node) | Normalizes items, converts prices, handles dual schema |
| 3 | Hours Gate (Code Node) | Enforces business hours, handles ASAP |
| 4 | Generate Order ID | Creates unique order identifier |
| 5 | Build Payment Link | Constructs Square Checkout API request |
| 6 | Response Node | Returns payment URL to frontend |

---

### Square Integration

- Square Checkout API v2
- Payment link generated dynamically
- Webhook triggers confirmation workflow

---

### Confirmation Workflow

**Workflow ID:** `Utopia-Deli-Confirmation`

Handles:

- Payment verification
- Kitchen notification
- Customer email

---

## 3. Setup Process (Replication)

### Step 1 — Create Webhook

- **Method:** POST
- **Path:** `utopia-deli-order-v4`
- **Mode:** `responseNode`

---

### Step 2 — Add Validation Node

- Normalize items
- Convert prices to cents
- Handle dual schema (cents vs dollars)

---

### Step 3 — Implement Hours Gate

- **Timezone:** America/Chicago
- Enforce Mon–Sat, 12:30–19:30
- Add ASAP handling (+30 minutes)

---

### Step 4 — Generate Order ID

**Format:**
```
UD-YYYYMMDD-HHMMSS-RANDOM
```

---

### Step 5 — Square Payment Link

- Use Square API
- Return URL to frontend

---

### Step 6 — Response Node

**Return:**
```json
{
  "success": true,
  "order_id": "UD-20260616-143022-4782",
  "payment_url": "https://square.link/u/xxxxx"
}
```

---

### Step 7 — Confirmation Workflow

- Create second webhook for Square
- Validate signature
- Send notifications

---

## 4. Configuration Requirements

### Credentials

| Credential | Type | Purpose |
|------------|------|---------|
| Square API | n8n credential | Payment link generation |
| SMTP (Gmail) | n8n credential | Email delivery |
| Twilio (SMS) | Optional | Kitchen SMS notifications |

---

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `SQUARE_WEBHOOK_SECRET` | Validates Square webhook signatures |
| `SQUARE_ACCESS_TOKEN` | Square API authentication |
| `SQUARE_LOCATION_ID` | Square location identifier |

---

## 5. Testing Procedure

| Step | Action | Verify |
|------|--------|--------|
| 1 | Submit test order | Webhook receives data |
| 2 | Confirm payment redirect works | Square link generated |
| 3 | Complete payment (sandbox) | Payment processes |
| 4 | Verify kitchen notification | Notification received |
| 5 | Verify confirmation email | Email delivered |
| 6 | Simulate failure (cancel payment) | No order created |

---

## 6. Maintenance

- Monitor webhook activity
- Check email delivery
- Review Square logs
- Update menu manually in frontend

---

## 7. Critical Constraints

| Constraint | Detail |
|------------|--------|
| **Response order** | Do not send webhook response before processing |
| **Webhook mode** | Use `responseNode` mode |
| **Currency** | Use cents, not floating dollars |
| **JavaScript** | Avoid ES6 spread in code nodes |

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
