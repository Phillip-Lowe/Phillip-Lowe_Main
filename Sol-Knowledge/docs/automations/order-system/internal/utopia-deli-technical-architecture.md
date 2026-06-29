# Utopia Deli — Online Ordering System
## Technical Architecture

**Document ID:** `UD-ARCH-001`  
**Version:** 1.1  
**Status:** Internal — Systack Only  
**Source System:** Utopia Deli (Live since 2026-06-03)  
**Date:** 2026-06-29  
**Builder:** SOL / Assembly

---

## Update Log

| Date | Change | Commit |
|------|--------|--------|
| 2026-06-16 | v1.0 — Initial architecture | — |
| 2026-06-29 | v1.1 — Updated payload format for Deli Simple Checkout v4 | c7c6a24 |

---

## Payload Format (Deli Simple Checkout v4)

The frontend sends the following JSON to `POST /webhook/utopia-deli-order-v4`:

```json
{
  "body": {
    "source": "pickup-order",
    "customer": {
      "name": "Customer Name",
      "email": "customer@example.com",
      "phone": "5015551234"
    },
    "items": [{
      "name": "cowboy chikn sandwich",
      "base_price_cents": 1300,
      "qty": 1,
      "modifiers": [{
        "label": "plain fries",
        "price_cents": 500
      }]
    }],
    "subtotal_cents": 1800,
    "tax_cents": 171,
    "frontend_total_cents": 1971,
    "notes": "",
    "pickup_time": "ASAP"
  }
}
```

**Key Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Display name of menu item |
| `base_price_cents` | integer | Item price without modifiers |
| `qty` | integer | Quantity ordered |
| `modifiers[].label` | string | Display name of modifier |
| `modifiers[].price_cents` | integer | Modifier upcharge in cents |
| `subtotal_cents` | integer | Pre-tax total |
| `tax_cents` | integer | Calculated tax (9.52%) |
| `frontend_total_cents` | integer | Final total including tax |

**Note:** Backend recalculates totals from `base_price_cents + sum(modifiers.price_cents)`. Frontend totals are for comparison only.

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

## Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                    CUSTOMER BROWSER                       │
│  order.theutopiadeli.com/pickup-order/                   │
│                                                          │
│  [Menu] → [Cart] → [Checkout Form] → [POST to Webhook]  │
└──────────────────────────┬──────────────────────────────┘
                           │ POST /webhook/utopia-deli-html-order-v1
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    n8n PROCESSING                         │
│                                                          │
│  [Validate] → [Hours Gate] → [Order ID] → [Square Link]  │
└──────────────────────────┬──────────────────────────────┘
                           │ Returns payment URL
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    SQUARE CHECKOUT                        │
│                                                          │
│  Customer completes payment → Square fires webhook       │
└──────────────────────────┬──────────────────────────────┘
                           │ Square webhook
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    n8n CONFIRMATION                       │
│                                                          │
│  [Verify Signature] → [Build Email] → [Send] → [Kitchen]│
└─────────────┬───────────────────────────┬───────────────┘
              │                           │
              ▼                           ▼
     ┌──────────────┐            ┌──────────────┐
     │ Customer     │            │ Kitchen       │
     │ Confirmation │            │ Notification  │
     │ Email        │            │ (Email/SMS)   │
     └──────────────┘            └──────────────┘
```

---

## Key Principles

| Principle | Description |
|-----------|-------------|
| **Payment-first system** | No order exists until payment is confirmed |
| **Stateless frontend** | All state lives in the browser session; no server-side cart |
| **Webhook-driven backend** | All processing triggered by HTTP POST, not polling |
| **Event-based confirmation** | Square webhook triggers fulfillment, not frontend callback |

---

## Storage Options

| Option | Use Case | Status |
|--------|----------|--------|
| **SQLite** (local) | Development, single-instance | Supported |
| **PostgreSQL** | Production, multi-tenant | Supported |
| **Google Sheets** | Client-visible order log | Active (Utopia Deli) |

---

## Component Map

| Component | Technology | Location |
|-----------|------------|----------|
| Order Page | Static HTML/CSS/JS | `order.theutopiadeli.com/pickup-order/` |
| Menu Config | JavaScript (`menu-data.js`) | GitHub Pages repo |
| Order Intake | n8n Workflow `Utopia-Deli-Simple-Checkout-v4` | `n8n.systack.net` |
| Payment Processing | Square Checkout API v2 | Square |
| Confirmation | n8n Workflow | `n8n.systack.net` |
| Order Log | PostgreSQL DB `utopia_deli` | localhost:5432 |
| Email Delivery | SMTP (Gmail) | n8n Email Node |

---

## External Dependencies

| Service | Purpose | Failure Impact |
|---------|---------|----------------|
| Square API | Payment link generation | Orders cannot be placed |
| Square Webhooks | Payment confirmation | Orders not fulfilled |
| Gmail SMTP | Email delivery | Confirmations not sent |
| Google Sheets API | Order logging | Orders not recorded |
| Cloudflare DNS | Domain routing | Order page unreachable |
| GitHub Pages | Frontend hosting | Order page unavailable |

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
