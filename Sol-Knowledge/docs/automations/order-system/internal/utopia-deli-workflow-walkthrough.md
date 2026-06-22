# Utopia Deli — Online Ordering System
## Workflow Walkthrough

**Document ID:** `UD-WF-001`  
**Version:** 1.0  
**Status:** Internal — Systack Only  
**Source System:** Utopia Deli (Live since 2026-06-03)  
**Date:** 2026-06-16  
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

## Workflow: Order Intake

**Workflow ID:** `1WEM4rZxjhhy7ooM`

---

### Node 1 — Webhook

**Type:** Webhook (POST)  
**Path:** `utopia-deli-html-order-v1`  
**Mode:** `responseNode`

Receives:

- Customer info (name, email, phone)
- Order items (id, name, qty, price)
- Totals (subtotal, tax, total)
- Pickup time
- Special instructions

---

### Node 2 — Normalize Schema

**Type:** Code Node

Handles:

- `item_id` fallback logic (maps legacy field names)
- Quantity normalization (defaults to 1 if missing)
- Cents conversion (multiplies dollar amounts by 100)
- Dual schema support (accepts both cents and dollars input)

---

### Node 3 — Hours Gate

**Type:** Code Node

Validates:

- Business hours (Mon–Sat, 12:30–19:30 CT)
- Sunday closure enforcement
- ASAP conversion (current time + 30 minutes)
- Blocks orders outside operating window

---

### Node 4 — Order ID

**Type:** Code Node

Generates unique identifier:

**Format:** `UD-YYYYMMDD-HHMMSS-RANDOM`

Example: `UD-20260616-143022-4782`

---

### Node 5 — Payment Link Builder

**Type:** HTTP Request (Square API)

Prepares Square Checkout:

- Constructs line items from order
- Adds tax as separate line item
- Sets currency (USD)
- Returns Square payment link URL

---

### Node 6 — Response Node

**Type:** Respond to Webhook

Returns:

```json
{
  "success": true,
  "order_id": "UD-20260616-143022-4782",
  "payment_url": "https://square.link/u/xxxxx"
}
```

---

## Workflow: Confirmation (Square)

**Workflow ID:** `IW27pwPj5DBYQdcq`

---

### Node 1 — Webhook

**Type:** Webhook (POST)

Receives Square payment event:

- Payment ID
- Order ID (from metadata)
- Payment status
- Amount

---

### Node 2 — Signature Validation

**Type:** Code Node

Uses:

- HMAC SHA256
- Secret key (`SQUARE_WEBHOOK_SECRET`)
- Validates request authenticity before processing

---

### Node 3 — Email Builder

**Type:** Code Node

Constructs HTML template:

- Navy header bar (`#001a2d`)
- Gray body (`#f8fafc`)
- Cyan CTA button (`#00a1db`)
- Navy footer (`#001a2d`)
- Variables: `{{ $json.field_name }}`

---

### Node 4 — Send Email

**Type:** Email Send (SMTP)

Uses:

- SMTP credentials (Gmail)
- Sends confirmation to customer
- Includes order details and pickup time

---

### Node 5 — Kitchen Notification

**Type:** Email Send or SMS (Twilio)

Sends:

- Order ID
- Customer name and phone
- Pickup time
- Itemized list with quantities
- Total amount
- Special instructions

---

## Node Chain Summary

### Order Intake Flow

```
Webhook (POST)
  → Normalize Schema
    → Hours Gate
      → Generate Order ID
        → Build Payment Link
          → Response Node
```

### Confirmation Flow

```
Square Webhook
  → Signature Validation
    → Email Builder
      → Send Email (Customer)
        → Kitchen Notification
```

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
