# Utopia Deli — Dual-Trigger Order Confirmation System

**Built:** 2026-06-12  
**Status:** Ready for deployment  
**Version:** 2.0

---

## 🎯 What This Is

A robust post-payment confirmation system that ensures every customer receives a branded itemized receipt email, regardless of which path triggers first.

**Two triggers, one email, zero duplicates.**

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CUSTOMER PAYS ON SQUARE                    │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│ FRONTEND SUCCESS PAGE      │    │ SQUARE WEBHOOK           │
│ (customer lands here)      │    │ (server-to-server)       │
└──────────────────────────┘    └──────────────────────────┘
              │                               │
              ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│ POST utopia-confirmed    │    │ POST utopia-square-webhook│
│ {order_id, source}       │    │ {payment object}          │
└──────────────────────────┘    └──────────────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              ▼
              ┌───────────────────────────────┐
              │  n8n: Order Confirmation       │
              │  (Dual Trigger Workflow)        │
              │                                 │
              │  1. Merge both triggers         │
              │  2. Check DB: email_sent?        │
              │  3. If no → build + send email  │
              │  4. Mark email_sent = true      │
              └───────────────────────────────┘
```

---

## 🔗 Webhook Endpoints

### Frontend Trigger (Backup)
```
POST https://utopia-api.systack.net/webhook/utopia-confirmed
Content-Type: application/json

{
  "order_id": "UDO-20260612-001",
  "source": "online-order",
  "triggered_at": "2026-06-12T14:30:00Z"
}
```

### Square Webhook (Primary)
```
POST https://utopia-api.systack.net/webhook/utopia-square-webhook
Content-Type: application/json

{
  "type": "payment.updated",
  "data": {
    "object": {
      "id": "pay_xxx",
      "status": "COMPLETED",
      "buyer_email_address": "customer@example.com",
      ...
    }
  }
}
```

---

## 📄 Frontend Integration

### Pickup Order Page (`pickup-order/index.html`)

**Square redirect URL:**
```
https://order.theutopiadeli.com/pickup-order/?success=1&order_id=UDO-xxx
```

**Script added:** `../utopia-deli-revamp/confirmation-trigger.js`

### Meal Prep Page (`catering/index.html`)

**Square redirect URL:**
```
https://order.theutopiadeli.com/catering/?mp_success=1&order_id=UMP-xxx
```

**Script added:** `../utopia-deli-revamp/confirmation-trigger.js`

### Script Behavior
1. Parses URL for `order_id` or `order` param
2. Detects source (`mp_success=1` → meal-prep, else → online-order)
3. Prevents double-fire via `sessionStorage`
4. Retries up to 3 times with exponential backoff

---

## 🗄️ Deduplication Logic

```
Trigger Received
    ↓
Lookup order in SQLite DB
    ↓
IF email_sent == true
    → Return {deduplicated: true}
    → STOP

ELSE
    → Build cart HTML
    → Inject branded email template
    → Send via SMTP
    → UPDATE orders SET email_sent = true
    → Return {success: true}
```

**DB Schema Required:**
```sql
ALTER TABLE orders ADD COLUMN email_sent BOOLEAN DEFAULT false;
ALTER TABLE orders ADD COLUMN email_sent_at DATETIME;
```

---

## 📧 Email Template

**Subject:** `Your Utopia Deli Order Receipt` (or `Meal Prep Receipt`)

**Contents:**
- Utopia Deli logo
- "Payment received ✅"
- Order ID + Payment ID
- Itemized cart table
- Subtotal, Tax, Total
- Footer with address

**Auto-detected order type:**
- `UDO-` prefix → Pickup Order
- `UMP-` prefix → Meal Prep Order
- Other → Generic Order

---

## 🔧 Deployment Checklist

### n8n Workflows to Import

| File | Purpose | Webhook Path |
|------|---------|-------------|
| `utopia-simple-checkout-v4.json` | Main checkout (branched) | `utopia-simple-checkout-v4` |
| `utopia-order-confirmation.json` | Frontend confirmation | `utopia-confirmed` |
| `utopia-order-confirmation-dual.json` | Dual-trigger handler | `utopia-confirmed` + `utopia-square-webhook` |
| `square-payment-webhook-handler.json` | Square webhook only | `square-payment-complete` |

### Square Developer Setup

1. Go to [Square Developer Dashboard](https://developer.squareup.com/)
2. Application → Webhooks → Create Subscription
3. **Event type:** `payment.updated`
4. **URL:** `https://utopia-api.systack.net/webhook/utopia-square-webhook`

### Files to Deploy

| File | Destination |
|------|-------------|
| `pickup-order/index.html` | `order.theutopiadeli.com/pickup-order/` |
| `catering/index.html` | `order.theutopiadeli.com/catering/` |
| `utopia-deli-revamp/confirmation-trigger.js` | `order.theutopiadeli.com/utopia-deli-revamp/` |
| `payment-confirmed.html` | `theutopiadeli.com/payment-confirmed.html` (legacy) |

---

## ✅ Testing

### Test 1: Frontend Trigger
```bash
curl -X POST https://utopia-api.systack.net/webhook/utopia-confirmed \
  -H "Content-Type: application/json" \
  -d '{"order_id": "UDO-TEST-001", "source": "online-order"}'
```

### Test 2: Square Webhook
```bash
curl -X POST https://utopia-api.systack.net/webhook/utopia-square-webhook \
  -H "Content-Type: application/json" \
  -d '{"type": "payment.updated", "data": {"object": {"status": "COMPLETED", "buyer_email_address": "test@example.com", "total_money": {"amount": 2848}}}}'
```

### Test 3: Deduplication
Run Test 1 twice. Second run should return: `{"deduplicated": true}`

---

## 🚨 Failure Scenarios

| Scenario | Behavior |
|----------|----------|
| Frontend fires, Square doesn't | Email sent via frontend trigger ✅ |
| Square fires, frontend doesn't | Email sent via Square webhook ✅ |
| Both fire simultaneously | First wins, second deduplicated ✅ |
| No email in payment data | Logs warning, still processes ✅ |
| DB lookup fails | Continues with webhook data ✅ |
| SMTP fails | Retry 3x, then logs error ❌ |

---

## 📚 Files

| File | Description |
|------|-------------|
| `utopia-deli-revamp/utopia-simple-checkout-v4.json` | Unified checkout workflow |
| `utopia-deli-revamp/utopia-order-confirmation.json` | Basic confirmation (single trigger) |
| `utopia-deli-revamp/utopia-order-confirmation-dual.json` | Dual-trigger with deduplication |
| `utopia-deli-revamp/square-payment-webhook-handler.json` | Square webhook only |
| `utopia-deli-revamp/confirmation-trigger.js` | Frontend webhook trigger |
| `docs/utopia-deli-dual-trigger-system.md` | This documentation |

---

**Built by:** SOL (OpenClaw Agent)  
**Last Updated:** 2026-06-12  
**Status:** Ready for testing
