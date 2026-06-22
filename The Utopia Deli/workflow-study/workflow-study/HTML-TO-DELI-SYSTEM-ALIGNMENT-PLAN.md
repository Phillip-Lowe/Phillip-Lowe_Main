# HTML → Deli System Alignment Plan

**Date:** 2026-06-05
**Agent:** SOL
**Status:** ANALYSIS COMPLETE — Implementation artifacts ready

---

## Executive Summary

The HTML frontend is NOT a separate system. It is a **compressed version of Phases 1–3** of the deli workflow pipeline, delivering a fully-built cart in a single POST request.

**Current Problem:** HTML Order V1 (11 nodes) bypasses the entire CART_STATE pipeline — no Sheets registry, no lifecycle participation, no post-payment flows.

**Solution:** Build HTML Order V2 that:
1. Normalizes HTML payload → canonical CART_STATE
2. Writes to same Google Sheets registry
3. Reuses identical finalization logic (Square, email, locking)
4. Participates in ALL downstream lifecycle workflows

---

## Artifacts Produced

| File | Purpose |
|------|---------|
| `DELI-SYSTEM-ARCHITECTURE.md` | Full system study — all 7 workflows analyzed |
| `HTML-TO-CART-STATE-NORMALIZER.js` | Code node: transforms HTML payload → CART_STATE |
| `CART_HTML-BUILDER.js` | Code node: renders cart_items → branded HTML table (WKFL 4 parity) |
| `FINAL-EMAIL-COMPOSER.js` | Code node: injects cart_html + payment_link into template |
| `EMAIL-TEMPLATE.js` | Code node: branded payment-request template (WKFL 4 parity) |
| `CONFIRMATION-EMAIL-TEMPLATE.js` | Code node: post-payment confirmation template |
| `UTXOPIA-DELI-HTML-ORDER-V2.json` | **Complete n8n workflow JSON** (14 nodes, import-ready) |

---

## What Was Discovered

### The REAL System Architecture

```
PHASE 1: Progressive Cart Building (70 + 52 + 13 = 135 nodes)
  → Contact + Item + Cart (70 nodes)
  → Add Another Item (52 nodes)
  → Cart Renderer + Router (13 nodes)
  → Output: CART_STATE with status = OPEN

PHASE 2: Finalization (20 nodes)
  → Order Received (WKFL 4)
  → Validates totals, builds Square payload, creates payment link
  → Sends email, updates status → LOCKED

PHASE 3: Lifecycle (21 + 16 + 10 = 47 nodes)
  → Disable Payment Link on Completed (21 nodes)
  → Delete Unused Payment Links (16 nodes)
  → Square Refund/Void Confirmation (10 nodes)
```

### Key Finding: Shared Registry

All workflows read/write the **same Google Sheet**:
- **Document:** `1jF85_1dx9WBETfhQyda2nnnKzzvTgzSbQ_uqcgArpm0`
- **CART_STATE** (gid: 2016519037): Tracks order lifecycle
- **ONLINE_ORDERS** (gid: 1868689747): Tracks payment resolution

### Critical Schema (CART_STATE)
| Field | Used By |
|-------|---------|
| `cart_id` | Primary key, referenced everywhere |
| `status` | OPEN → LOCKED → PAID / REFUNDED / VOIDED |
| `cart_items_json` | Parsed by cart_html BUILDER |
| `payment_link_id` | Used by Disable Link workflow |
| `square_order_id` | Used by Disable Link + Refund workflows |
| `customer_email` | Email destination |

### Square API Configuration
- **Endpoint:** `POST /v2/online-checkout/payment-links`
- **Location ID:** `J4B6A3X6RYA63`
- **Tax:** 9.52%, handled as manual line item
- **Redirect:** `https://www.theutopiadeli.com/payment-confirmed`

---

## The V2 Workflow (14 Nodes)

### Node Flow

```
[Webhook Trigger]
    ↓
[Validate JSON] ──Invalid──→ [Error Response]
    ↓ Valid
[Normalize HTML → CART_STATE] ──Parallel──→ [Write CART_STATE → Sheets]
    │                                               ↓
    │                                         [Build cart_html]
    │                                               ↓
    │                                         [Email Template]
    │                                               ↓
    └──→ [Create Payment Link (Square)] ──→ [Normalize Payment Response]
                                                  ↓
                                         [Update CART_STATE → LOCKED]
                                                  ↓
                                         [Compose Final Email]
                                                  ↓
                                         [Send Payment Email]
                                                  ↓
                                         [Success Response]
```

### What V2 Does That V1 Doesn't

| Capability | V1 | V2 |
|-----------|-----|-----|
| Writes to CART_STATE | ❌ | ✅ (status = OPEN) |
| Updates status → LOCKED | ❌ | ✅ |
| Uses canonical cart_items structure | ❌ | ✅ |
| Handles modifiers as structured objects | ❌ | ✅ |
| Uses branded cart_html builder | ❌ | ✅ |
| Uses branded email template | ❌ | ✅ |
| Participates in Disable Link workflow | ❌ | ✅ (via payment_link_id) |
| Eligible for unused link cleanup | ❌ | ✅ |
| Eligible for refund workflow | ❌ | ✅ (via square_order_id) |
| Source tracking | ❌ | ✅ (source = "html") |

---

## Implementation Steps

### Step 1: Deploy V2 Workflow
```bash
# Import into n8n via UI or API
# Workflow file: UTXOPIA-DELI-HTML-ORDER-V2.json
# Webhook path: /webhook/utopia-deli-html-order-v2
```

### Step 2: Configure Google Sheets Credentials
- Ensure n8n has access to `Utopia_Deli_Menu_System`
- Verify CART_STATE sheet exists with correct columns
- Test append + update operations

### Step 3: Configure Square Credentials
- Ensure HTTP Header Auth is configured for Square API
- Verify `J4B6A3X6RYA63` location ID is valid
- Test payment link creation

### Step 4: Update Frontend
Change frontend POST from:
```
POST /webhook/utopia-deli-html-order-v1
```
To:
```
POST /webhook/utopia-deli-html-order-v2
```

### Step 5: Test End-to-End
1. Submit order via HTML frontend
2. Verify CART_STATE row created (status = OPEN)
3. Verify email received with payment link
4. Complete payment
5. Verify Disable Link workflow triggers
6. Verify CART_STATE updated (status = PAID)
7. Verify ONLINE_ORDERS appended
8. Verify confirmation email received

### Step 6: Migrate / Deprecate V1
- Run both in parallel for 1 week
- Monitor V1 vs V2 order volumes
- Deactivate V1 once V2 is stable

---

## Critical Differences from V1

### Payload Structure
**V1 Input:**
```json
{
  "order_items": [
    { "name": "The Cowboy", "qty": 1, "price": 10.99, "modifiers": ["+ Avocado"] }
  ]
}
```

**V2 Output (CART_STATE):**
```json
{
  "cart_items": [
    {
      "type": "primary",
      "display_name": "The Cowboy",
      "quantity": 1,
      "base_price_cents": 1099,
      "variant_price_cents": 0,
      "modifiers": [
        { "mod_name": "+ Avocado", "price_delta": 0.50 }
      ],
      "line_total_cents": 1149
    }
  ]
}
```

### Modifier Handling
- **V1:** Modifiers are strings in the email (no price tracking)
- **V2:** Modifiers are structured objects (mod_name + price_delta), rendered with category headers (IDENTIFIERS / TAKE OFF / ADD-ONS)

### Tax Handling
- **V1:** Tax shown in email but NOT in Square payload
- **V2:** Tax added as separate Square line item ("Tax", quantity "1")

### Order ID Format
- **V1:** `UDO-YYYYMMDD-NNN` (same in V2)
- **V2:** Also used as `reference_id` in Square order metadata

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Square API failure after Sheets write | Status stays OPEN, manual cleanup possible |
| Sheets write failure | Order still processed, email sent, but not tracked |
| Email failure | Payment link created, customer can still pay if they have URL |
| Duplicate orders | Each POST generates new cart_id with random suffix |
| Invalid modifier format | Parser falls back to $0 identifier |

---

## Lifecycle Participation Checklist

After V2 deployment, verify:

- [ ] Disable Payment Link workflow can find HTML orders by `cart_id`
- [ ] Disable Payment Link workflow can disable links created by V2
- [ ] Unused Link Deletion includes V2-generated links
- [ ] Refund/Void webhook can resolve V2 orders by `square_payment_id`
- [ ] All workflows correctly update CART_STATE status transitions

---

## Files Location
```
~/utopia-deli-revamp/workflow-study/
├── DELI-SYSTEM-ARCHITECTURE.md
├── HTML-TO-CART-STATE-NORMALIZER.js
├── CART_HTML-BUILDER.js
├── FINAL-EMAIL-COMPOSER.js
├── EMAIL-TEMPLATE.js
├── CONFIRMATION-EMAIL-TEMPLATE.js
└── UTXOPIA-DELI-HTML-ORDER-V2.json
```

## Next Steps
1. Review this plan with stakeholder
2. Deploy V2 workflow to n8n
3. Configure credentials
4. Run test orders
5. Monitor lifecycle flows
6. Deactivate V1
