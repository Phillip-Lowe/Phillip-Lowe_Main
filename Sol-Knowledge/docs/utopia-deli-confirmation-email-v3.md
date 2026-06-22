# Utopia Deli — Confirmation Email System v3

**Built:** 2026-06-12  
**Status:** Deployed  
**Version:** 3.0

---

## 🎯 What This Is

Post-payment confirmation system for Utopia Deli. When a customer completes payment on Square, they land on a branded success page that fires a webhook to n8n, which sends an itemized receipt email.

---

## 📐 Architecture

```
Customer Pays on Square
    ↓
Square redirects to success page
    ↓
Success page fires webhook
    ↓
n8n receives webhook → looks up order in DB
    ↓
Builds branded email → sends to customer
```

---

## 📄 Success Pages

### Pickup Orders
**URL:** `https://order.theutopiadeli.com/payment-confirmed/?order_id=UDO-xxx`

**File:** `payment-confirmed/index.html`

**Copy:**
- ✅ Payment Confirmed
- ✅ Order Status: Paid & Received
- ✅ Pickup time: 25–30 minutes
- ✅ Order Policy (no modifications)
- ✅ Contact info
- ✅ Homepage button → `https://www.theutopiadeli.com/home`
- ✅ Order Again button → `https://order.theutopiadeli.com/pickup-order/`

### Meal Prep
**URL:** `https://order.theutopiadeli.com/payment-confirmed-meal-prep/?order_id=UMP-xxx`

**File:** `payment-confirmed-meal-prep/index.html`

**Copy:**
- ✅ Payment Confirmed
- ✅ Order Status: Paid & Received
- ✅ Pickup: Thursday 12:30 PM – 7:30 PM
- ✅ Order Policy (no modifications)
- ✅ Contact info
- ✅ Homepage button → `https://www.theutopiadeli.com/home`
- ✅ Order Again button → `https://order.theutopiadeli.com/catering/`

---

## 🔗 Webhook Endpoints

### Frontend Trigger
```
POST https://utopia-api.systack.net/webhook/utopia-confirmation-email
Content-Type: application/json

{
  "order_id": "UDO-20260612-001",
  "source": "online-order",
  "page_url": "https://order.theutopiadeli.com/payment-confirmed/?order_id=...",
  "triggered_at": "2026-06-12T14:30:00Z"
}
```

### Square Webhook
```
POST https://utopia-api.systack.net/webhook/utopia-square-webhook
Event: payment.updated
```

---

## 🗄️ DB Schema Required

```sql
CREATE TABLE IF NOT EXISTS orders (
  order_id TEXT PRIMARY KEY,
  customer_name TEXT,
  customer_email TEXT,
  customer_phone TEXT,
  cart_json TEXT,
  subtotal_cents INTEGER,
  tax_cents INTEGER,
  total_cents INTEGER,
  source TEXT,  -- 'online-order' or 'meal-prep'
  email_sent INTEGER DEFAULT 0,
  email_sent_at DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📧 Email Template

**Subject:** Your Utopia Deli Order Receipt (or Meal Prep Receipt)

**Contents:**
- Utopia Deli logo
- "Payment received ✅"
- Order ID
- Itemized cart table
- Subtotal, Tax, Total
- Footer with address + phone

---

## 🔧 n8n Workflow

**File:** `utopia-deli-revamp/utopia-confirmation-email-v3.json`

**Flow:**
```
Frontend Webhook ───┐
                    ├─→ Route Trigger → Prep DB Lookup
Square Webhook ─────┘
                    ↓
Lookup Order in DB → Extract DB Row
                    ↓
IF Order Exists? (error === "NOT_FOUND")
  YES → Not Found Response → Respond
  NO  → IF Email Not Sent? (Number(email_sent) !== 1)
          YES → Build Order Data → Build Cart HTML → Build Branded Email
                → IF Email Exists? (email !== "")
                  YES → Send Email → Mark Sent (email_sent = 1) → Respond
                  NO  → No Email Response → Respond
          NO  → Already Sent Response → Respond
```

---

## 🚀 Deployment

### Files to Deploy

| File | Destination |
|------|-------------|
| `payment-confirmed/index.html` | `order.theutopiadeli.com/payment-confirmed/` |
| `payment-confirmed-meal-prep/index.html` | `order.theutopiadeli.com/payment-confirmed-meal-prep/` |
| `utopia-deli-revamp/utopia-confirmation-email-v3.json` | Import to n8n |

### n8n Setup

1. Import workflow JSON
2. Configure SQLite credential: `utopia-orders`
3. Configure SMTP credential
4. Activate workflow

### Square Setup

1. Developer Dashboard → Webhooks
2. Add subscription:
   - Event: `payment.updated`
   - URL: `https://utopia-api.systack.net/webhook/utopia-square-webhook`

### Checkout Workflows

Update redirect URLs in:
- `utopia-simple-checkout-v4.json`
  - Pickup: `https://order.theutopiadeli.com/payment-confirmed/?order_id={{order_id}}`
  - Meal Prep: `https://order.theutopiadeli.com/payment-confirmed-meal-prep/?order_id={{order_id}}`

---

## ✅ Testing

### Test Frontend Trigger
```bash
curl -X POST https://utopia-api.systack.net/webhook/utopia-confirmation-email \
  -H "Content-Type: application/json" \
  -d '{"order_id": "UDO-TEST-001", "source": "online-order"}'
```

### Test Square Webhook
```bash
curl -X POST https://utopia-api.systack.net/webhook/utopia-square-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "type": "payment.updated",
    "data": {
      "object": {
        "payment": {
          "status": "COMPLETED",
          "reference_id": "UDO-TEST-001"
        }
      }
    }
  }'
```

---

## 📚 Files

| File | Description |
|------|-------------|
| `payment-confirmed/index.html` | Pickup order success page |
| `payment-confirmed-meal-prep/index.html` | Meal prep success page |
| `utopia-deli-revamp/utopia-confirmation-email-v3.json` | n8n workflow |
| `utopia-deli-revamp/utopia-simple-checkout-v4.json` | Updated checkout workflow |
| `docs/utopia-deli-confirmation-email-v3.md` | This documentation |

---

**Built by:** SOL (OpenClaw Agent)  
**Last Updated:** 2026-06-12  
**Status:** Deployed and ready for testing
