# Utopia Deli — Confirmation Email System
## Internal Implementation Guide

**Document ID:** `UD-CONF-IMPL-001`  
**Version:** 1.0  
**Status:** Internal — Systack Only  
**Source System:** Utopia Deli (Live since 2026-06-12)  
**Date:** 2026-06-29  
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

## 1. System Architecture

```
Customer Pays on Square
  → Square redirects to success page
    → Success page fires webhook
      → n8n receives webhook
        → Lookup order in DB
          → Build branded email
            → Send to customer
```

**Dual Trigger Design:**

```
Frontend Webhook ───┐
                    ├─→ Route Trigger → DB Lookup → Continue
Square Webhook ─────┘
```

Both triggers flow independently into the same processing pipeline. No merge node — avoids deadlock.

---

## 2. Core Components

### Success Pages

| Page | URL | File |
|------|-----|------|
| Pickup Orders | `order.theutopiadeli.com/payment-confirmed/` | `payment-confirmed/index.html` |
| Meal Prep | `order.theutopiadeli.com/payment-confirmed-meal-prep/` | `payment-confirmed-meal-prep/index.html` |

---

### Webhook Endpoints

| Endpoint | Source | Purpose |
|----------|--------|---------|
| `POST /webhook/utopia-confirmation-email` | Frontend success page | Triggers receipt email |
| `POST /webhook/utopia-square-webhook` | Square | Payment confirmation trigger |

---

### n8n Workflow

**File:** `utopia-confirmation-email-v3.json`

**Node Chain:**

```
Webhook (Square or Frontend)
  → Normalize (parses payment.updated + COMPLETED)
    → Should Process? (IF $json.process === true)
      → Prep DB Lookup
        → Lookup Order in DB (SQLite)
          → Extract DB Row (array → object)
            → Order Exists? (IF error !== "NOT_FOUND")
              → Email Not Sent? (IF Number(email_sent) !== 1)
                → Build Order Data (parse cart_json)
                  → Build Cart HTML (table)
                    → Build Branded Email
                      → Email Exists? (IF email !== "")
                        → Send Email (Gmail SMTP)
                          → Mark Email Sent (UPDATE email_sent = 1)
                            → Respond ✅
```

---

### Database Schema

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

## 3. Setup Process (Replication)

### Step 1 — Deploy Success Pages

- Copy `payment-confirmed/index.html` to client domain
- Copy `payment-confirmed-meal-prep/index.html` (if applicable)
- Update webhook endpoint URL in page JavaScript

---

### Step 2 — Import n8n Workflow

- Import `utopia-confirmation-email-v3.json`
- Configure SQLite credential
- Configure SMTP credential
- Activate workflow

---

### Step 3 — Configure Square Webhook

- Square Developer Dashboard → Webhooks
- Add subscription: Event `payment.updated`
- URL: `https://utopia-api.systack.net/webhook/CLIENT-square-webhook`

---

### Step 4 — Update Checkout Redirect URLs

In the order intake workflow, update redirect URLs:

- Pickup: `https://order.client.com/payment-confirmed/?order_id={{order_id}}`
- Meal Prep: `https://order.client.com/payment-confirmed-meal-prep/?order_id={{order_id}}`

---

## 4. Critical Pitfalls (All Fixed in v3)

### Pitfall 1: Merge Node Deadlock

**Problem:** Using `mergeByIndex` waits for both inputs simultaneously. Only one trigger fires → workflow stalls.

**Fix:** Remove merge node. Use direct parallel routing — both triggers flow independently into same downstream node.

---

### Pitfall 2: SQLite Returns Array

**Problem:** SQLite node returns `[{row}]` but downstream expects `{row}`.

**Fix:** Add "Extract DB Row" Code node:
```javascript
const rows = $json;
if (!rows || rows.length === 0) {
  return [{ json: { error: "NOT_FOUND" } }];
}
return [{ json: rows[0] }];
```

---

### Pitfall 3: email_sent Check Type Mismatch

**Problem:** `$json.email_sent !== "true"` compares integer to string.

**Fix:** Use `Number($json.email_sent || 0) !== 1`

---

### Pitfall 4: Missing Order Handling

**Problem:** DB returns no rows → cascading errors.

**Fix:** Add "Order Exists?" IF node checking `$json.error === "NOT_FOUND"`.

---

### Pitfall 5: Missing Email Guard

**Problem:** Empty email → SMTP error.

**Fix:** Add "Email Exists?" IF node checking `$json.email !== "" && $json.email !== null`.

---

## 5. Testing Procedure

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

## 6. Configuration Requirements

### Credentials

| Credential | Type | Purpose |
|------------|------|---------|
| SQLite | n8n credential | Order lookup |
| SMTP (Gmail) | n8n credential | Email delivery |

---

### Database

- **File:** `orders.db`
- **Table:** `orders`
- **Key column:** `email_sent` (INTEGER DEFAULT 0)

---

## 7. Maintenance

- Monitor n8n execution log for failed email sends
- Check `email_sent` column for deduplication accuracy
- Verify Square webhook subscription is active
- Update success page copy as needed

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
