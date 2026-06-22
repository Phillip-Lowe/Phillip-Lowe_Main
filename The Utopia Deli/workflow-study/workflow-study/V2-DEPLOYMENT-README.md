# V2 Workflow — Credentials & Deployment Notes

**Date:** 2026-06-05
**Status:** Ready for deployment

---

## What Changed

### Database (Local SQLite)
- **V2 now writes to the SAME local n8n SQLite database** as all other deli workflows
- CART_STATE appended on order receipt (status = OPEN)
- CART_STATE updated on payment link creation (status = LOCKED)
- All other lifecycle workflows (Disable Link, Cleanup, Refund) read from this same database

### Email (SMTP — deli gmail)
- **V2 now uses the SAME SMTP credential** as the existing workflows: **`deli gmail` (ZOvYr6kSP7zE8tBv)**
- From: `theutopiadelilittlerock@gmail.com`
- This is the SAME sender used by the Disable Payment Link workflow's confirmation email
- Email body is HTML (branded, same template as WKFL 4)

### Square API
- **Uses `httpHeaderAuth`** (same as WKFL 4 Order Received)
- Credential ID: `9FQ7SQhaUqssIJJb` (shared in project `LPFVmXe92Be2P99s`)
- Same endpoint: `POST /v2/online-checkout/payment-links`
- Same location ID: `J4B6A3X6RYA63`

---

## Credential Mapping

| Service | Credential Name | ID | Type | Used By |
|---------|----------------|-----|------|---------|
| **SMTP / Email** | deli gmail | `ZOvYr6kSP7zE8tBv` | smtp | V2 Send Payment Email |
| **Square API** | Square API | `9FQ7SQhaUqssIJJb` | httpHeaderAuth | V2 Create Payment Link |
| Google Sheets | *(OAuth, auto-resolved)* | — | — | V2 Write/Update CART_STATE |

---

## Node Structure (14 nodes)

```
1.  Webhook Trigger          — POST /webhook/utopia-deli-html-order-v2
2.  Validate JSON            — Required fields check
3.  Valid?                   — If/else branch
4.  Normalize HTML→CART_STATE — Transforms payload + builds Square items
5.  Write CART_STATE→Sheets   — Append to CART_STATE (status=OPEN)
6.  Build cart_html           — Render branded cart HTML table
7.  Email Template            — Load branded payment-request template
8.  Create Payment Link (Square) — Square API call
9.  Normalize Payment Response — Extract payment_link URL/ID
10. Update CART_STATE→LOCKED — Update status + payment_link_id
11. Compose Final Email       — Inject cart_html + payment_link into template
12. Send Payment Email        — SMTP via deli gmail credential
13. Success Response         — Return {success, order_id, payment_url}
14. Error Response            — Return {success: false, error}
```

---

## Deployment Checklist

### 1. Import Workflow
```bash
# Via n8n UI: Workflows → Import → paste JSON
# Or via API if you have the n8n API key
```

### 2. Verify Credentials
- [ ] `deli gmail` (SMTP) is available in the workspace
- [ ] `Square API` (httpHeaderAuth) is available in the workspace
- [ ] Google Sheets OAuth is connected and has access to `Utopia_Deli_Menu_System`

### 3. Activate Workflow
```bash
# Toggle Active in n8n UI
# Webhook path: /webhook/utopia-deli-html-order-v2
```

### 4. Test End-to-End
```bash
curl -X POST https://n8n.systack.net/webhook/utopia-deli-html-order-v2 \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Test Customer",
    "email": "test@example.com",
    "phone": "(501) 555-9999",
    "order_items": [
      {"name": "The Cowboy", "qty": 1, "price": 10.99, "modifiers": ["+ Avocado ($0.50)", "no onions"]}
    ],
    "subtotal": 10.99,
    "tax": 1.05,
    "total": 12.04,
    "pickup_time": "14:30",
    "special_instructions": "Extra napkins"
  }'
```

### 5. Verify CART_STATE
- [ ] Check Google Sheets CART_STATE tab for new row (status = OPEN then LOCKED)
- [ ] Verify cart_items_json contains structured modifier objects
- [ ] Confirm email received with branded HTML + payment button

### 6. Verify Lifecycle Integration
- [ ] Pay via Square link
- [ ] Confirm Disable Payment Link workflow triggers
- [ ] Verify CART_STATE status → PAID
- [ ] Verify ONLINE_ORDERS sheet appended
- [ ] Verify confirmation email received

---

## Differences from V1

| Aspect | V1 (Current) | V2 (New) |
|--------|-------------|----------|
| Database | None (ephemeral) | **Local SQLite → Google Sheets CART_STATE** |
| Email type | Plain text | **Branded HTML via SMTP (deli gmail)** |
| Email sender | Same | Same (`theutopiadelilittlerock@gmail.com`) |
| Square auth | httpBearerAuth | **httpHeaderAuth** (matches WKFL 4) |
| Modifier handling | String list | **Structured objects** (mod_name + price_delta) |
| cart_html | Basic | **Branded table** (identifiers / take-offs / add-ons) |
| Status tracking | None | **OPEN → LOCKED → PAID** |
| Lifecycle participation | ❌ No | ✅ **Full participation** |

---

## Files

- `UTXOPIA-DELI-HTML-ORDER-V2.json` — Import-ready workflow
- `HTML-TO-CART-STATE-NORMALIZER.js` — Code node reference
- `CART_HTML-BUILDER.js` — cart_html builder reference
- `DELI-SYSTEM-ARCHITECTURE.md` — Full system documentation
