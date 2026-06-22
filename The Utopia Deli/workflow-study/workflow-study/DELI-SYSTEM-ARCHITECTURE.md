# Utopia Deli System Architecture — Full Study

**Date:** 2026-06-05
**Agent:** SOL
**Objective:** Understand the complete deli workflow ecosystem to align HTML frontend

---

## System Overview

The deli system is a **multi-workflow distributed state machine** with 3 phases:

```
PHASE 1: Intake + Build (Multi-pass)
  → Contact + Item + Cart
  → Add Another Item
  → Cart Renderer + Router
  → Output: CART_STATE (frozen, OPEN)

PHASE 2: Finalization (Single-pass)
  → Order Received (WKFL 4)
  → Validates totals
  → Builds Square payload
  → Creates payment link
  → Sends email
  → Locks cart (status → LOCKED)

PHASE 3: Post-Payment Lifecycle (Async)
  → Disable Square Payment Link (on payment.completed)
  → Delete Unused Payment Links (scheduled cleanup)
  → Square Refund / Void Confirmation (webhook)
  → Output: Updates CART_STATE → PAID / REFUNDED
```

## Google Sheets Registry

**Document:** `1jF85_1dx9WBETfhQyda2nnnKzzvTgzSbQ_uqcgArpm0` (Utopia_Deli_Menu_System)

### CART_STATE (gid: 2016519037)
| Column | Type |
|--------|------|
| cart_id | string |
| created_at | string |
| updated_at | string |
| status | string (OPEN → LOCKED → PAID → REFUNDED → VOIDED) |
| G_USER_ID | string |
| customer_name | string |
| customer_email | string |
| customer_phone | string |
| cart_items_json | string (JSON array) |
| subtotal_cents | string |
| tax_cents | string |
| total_cents | string |
| square_order_id | string |
| square_payment_id | string |
| payment_link_id | string |
| payment_link_url | string |
| paid_at | string |
| fulfillment_status | string |

### ONLINE_ORDERS (gid: 1868689747)
| Column | Type |
|--------|------|
| order_id | string |
| cart_id | string |
| square_order_id | string |
| square_payment_id | string |
| customer_name | string |
| customer_email | string |
| customer_phone | string |
| cart_items_json | string |
| subtotal_cents | string |
| tax_cents | string |
| total_cents | string |
| currency | string |
| created_at | string |
| paid_at | string |
| fulfillment_status | string |
| payment_state (PAID \| REFUNDED \| PARTIALLY_REFUNDED \| VOIDED) | string |
| refund_state (NONE \| PARTIAL \| FULL) | string |
| refund_amount_cents | string |
| refund_currency | string |
| refund_at | string |
| square_refund_id | string |
| refund_reason | string |
| void_reason | string |
| ops_notes | string |

### Square API Configuration
- **Endpoint:** `https://connect.squareup.com/v2/online-checkout/payment-links`
- **Location ID:** `J4B6A3X6RYA63`
- **Tax Rate:** 9.52%
- **Redirect URL:** `https://www.theutopiadeli.com/payment-confirmed`
- **Square Version Header:** `2026-01-22`
- **Auth:** HTTP Header (generic credential)

---

---

## Phase 1: Intake + Build (The Progressive Cart)

### Workflow: Contact + Item + Cart (FAGmGNVzWmNOW2LP)
- **70 nodes** — Complex form-driven multi-step flow
- **Purpose:** Build structured cart incrementally
- **Key Nodes:**
  - Form triggers (menu selection)
  - Modifier pages per item
  - CART BUILDER (code node — computes pricing)
  - FREEZE_CART_STATE (code node — locks cart)
  - TAX CALCULATION (code node)
  - Commit (code node — generates canonical output)

### Commit Node Output (Canonical CART_STATE)
```javascript
{
  cart_id: "<UUID>",
  created_at: "<ISO>",
  updated_at: "<ISO>",
  status: "OPEN",

  customer_name: "...",
  customer_email: "...",
  customer_phone: "...",

  cart_items_json: "<JSON string>",

  subtotal_cents: <number>,
  tax_cents: <number>,
  total_cents: <number>,

  pass_index: <number|null>,
  frozen_pass_index: <number|null>,
  freeze_timestamp: "<ISO>|null"
}
```

### HTML-Generated CART_STATE (Target Format)
HTML orders must produce this exact structure when writing to CART_STATE:

```javascript
{
  cart_id: "UDO-YYYYMMDD-NNN",          // Same format as HTML v1
  created_at: "2026-06-05T08:16:00Z", // ISO timestamp
  updated_at: "2026-06-05T08:16:00Z",
  status: "OPEN",

  customer_name: "Jane Doe",
  customer_email: "jane@example.com",
  customer_phone: "(501) 555-1234",

  cart_items_json: JSON.stringify([
    {
      type: "primary",
      display_name: "The Cowboy",
      quantity: 1,
      base_price_cents: 1099,
      variant_price_cents: 0,
      modifiers: [
        { mod_name: "+ Avocado", price_delta: 0.50 },
        { mod_name: "no onions", price_delta: 0 }
      ],
      notes: "Extra sauce please"
    }
  ]),

  subtotal_cents: 1099,
  tax_cents: 105,
  total_cents: 1204,

  // Populated after payment link creation (status → LOCKED)
  square_order_id: null,
  payment_link_id: null,
  payment_link_url: null
}
```

### Workflow: Add Another Item (DDIlSP2iCx8V82Bw)
- **52 nodes** — Adds items to existing cart
- Handles multi-pass ordering
- Merges new items with existing cart_items

### Workflow: Cart Renderer + Router (c6a983d4-085b-434c-a329-fab768652f2a)
- **13 nodes** — Displays cart, routes to checkout or add more
- Reads from Google Sheets
- Builds HTML for display
- Checks status = OPEN before allowing edits

---

## Phase 2: Finalization (Order Received — WKFL 4)

### Workflow: Order Received (ap3qRQdhYog9NxqT)
- **20 nodes**
- **Trigger:** Form submission OR webhook with CART_STATE
- **Key Validation:**
  - Validate Total: `subtotal_cents + tax_cents == total_cents`
  - Required-Fields: `customer_email`, `cart_html`, payment link intent
  - Cart Rehydration: Parses `cart_items_json` → `cart_items` array

### Critical Code Nodes (WKFL 4)

#### 1. Cart Rehydration
```javascript
// Input: cart_items_json (string)
// Output: cart_items (array)
let cart_items = JSON.parse(input.cart_items_json);
// Validates it's an array
```

#### 2. Square Line-Item Builder
```javascript
// Builds Square-compatible line items
// Main item: base_price_cents
// Modifiers: each as separate modifier with price_delta
// Tax added as separate line item at end
const line_item = {
  name: item.display_name,
  quantity: String(qty),
  base_price_money: { amount: item.base_price_cents, currency: "USD" },
  modifiers: [] // each modifier with its own price_delta
};
```

#### 3. cart_html BUILDER
```javascript
// Renders cart_items into HTML table
// Handles: identifiers (free), take-offs, add-ons (paid)
// Uses semantic convention: "no | no- | hold | hold-" = take-off
// Outputs: cart_html string for email injection
```

#### 4. FINAL EMAIL COMPOSER
```javascript
// Injects into template:
// __CART_HTML__ → cart_html
// __PAYMENT_LINK__ → styled button
// __CURRENT_YEAR__ → year
```

#### 5. Email Template
- Utopia Deli branded HTML
- Logo, headline, slogan, order summary
- "Complete Payment" CTA button
- Footer with contact info

---

## Phase 3: Post-Payment Lifecycle

### Workflow: Disable Payment Link on Completed (H7bUyLseYgZQfHvE)
- **21 nodes**
- **Trigger:** Square webhook `payment.status == COMPLETED`
- **Actions:**
  1. Verify Square signature (HMAC-SHA256)
  2. Lookup CART_STATE by `square_order_id`
  3. Check status = LOCKED
  4. PATCH Square API → disable payment link
  5. Update Google Sheets → status = PAID
  6. Append to ONLINE_ORDERS sheet
  7. Send confirmation email to customer

### Workflow: Unused Payment Link Deletion (krNiXIrpm8qsvgzD)
- **16 nodes**
- **Trigger:** Schedule (daily)
- **Actions:**
  1. List all Square payment links
  2. Filter: created > 24h ago AND status != INACTIVE
  3. Check if paid in sheets
  4. Delete unused links
  5. Log results

### Workflow: Square Refund/Void Confirmation (YFeegOW7XYmwKmDq)
- **10 nodes**
- **Trigger:** Webhook `/square-refund`
- **Actions:**
  1. Verify Square signature
  2. Lookup ONLINE_ORDERS by `square_payment_id`
  3. Idempotency gate (skip if already processed)
  4. Normalize: REFUND or VOID
  5. Update Google Sheets with resolution

---

## HTML System vs Deli System — Current Gap Analysis

### Current HTML Order V1 (1WEM4rZxjhhy7ooM)
- **11 nodes** — Minimal webhook-only flow
- **Input:** Direct JSON POST with order_items
- **Does NOT:**
  - ❌ Build canonical CART_STATE
  - ❌ Write to Google Sheets (no persistence)
  - ❌ Use cart_items_json / cart_items structure
  - ❌ Use display_name / base_price_cents / variant_price_cents
  - ❌ Handle modifiers as structured objects (just strings)
  - ❌ Participate in lifecycle workflows
  - ❌ Track status (OPEN → LOCKED → PAID)

### What HTML System Currently Does
```
POST → Validate JSON → Build Square line items → Create payment link
→ Send email → Respond with order_id + payment_url
```

### What It Should Do
```
POST → Normalize to CART_STATE → Write to Sheets (OPEN)
→ Validate → Build Square payload → Create payment link
→ Update Sheets (LOCKED, payment_link_id)
→ Send email → Respond
→ Participate in lifecycle (disable link on payment, cleanup, refunds)
```

---

## Required Transformation Layer

### HTML Payload (Current)
```json
{
  "customer_name": "...",
  "email": "...",
  "phone": "...",
  "order_items": [
    { "name": "...", "qty": 1, "price": 10.99, "modifiers": ["..."] }
  ],
  "subtotal": 10.99,
  "tax": 1.04,
  "total": 12.03,
  "pickup_time": "...",
  "special_instructions": "..."
}
```

### Required CART_STATE (Canonical)
```json
{
  "cart_id": "UDO-20260605-123",
  "status": "OPEN",
  "customer_name": "...",
  "customer_email": "...",
  "customer_phone": "...",
  "cart_items": [
    {
      "type": "primary",
      "display_name": "...",
      "quantity": 1,
      "base_price_cents": 1099,
      "variant_price_cents": 0,
      "modifiers": [
        { "mod_name": "...", "price_delta": 0.50 }
      ],
      "notes": "..."
    }
  ],
  "cart_items_json": "<stringified>",
  "subtotal_cents": 1099,
  "tax_cents": 104,
  "total_cents": 1203,
  "source": "html"
}
```

---

## Critical Requirements for HTML System

### 1. Shared Order Registry (Google Sheets)
- MUST write to same sheet as deli system
- MUST use same cart_id format or compatible identifiers
- MUST track status: OPEN → LOCKED → PAID

### 2. Square Payload Parity
- Same line-item structure
- Same modifier handling
- Tax as separate line item
- Same payment link creation

### 3. Email Parity
- Same branded template
- Same cart HTML rendering
- Same payment button styling

### 4. Lifecycle Participation
- HTML orders must trigger Disable Link workflow
- HTML orders must be eligible for cleanup
- HTML orders must feed into refund workflow
- Must write to ONLINE_ORDERS on payment

### 5. Status Flow
```
HTML POST received → status = OPEN
Payment link created → status = LOCKED
Square payment.completed → status = PAID
Square refund/void → status = REFUNDED/VOIDED
```

---

## Google Sheets Schema (Inferred)

### CART_STATE Sheet
| Column | Type | Notes |
|--------|------|-------|
| cart_id | string | UUID or UDO-YYYYMMDD-NNN |
| status | enum | OPEN, LOCKED, PAID, REFUNDED, VOIDED |
| customer_name | string | |
| customer_email | string | |
| customer_phone | string | |
| cart_items_json | string | JSON array |
| subtotal_cents | number | |
| tax_cents | number | |
| total_cents | number | |
| payment_link_id | string | Square link ID |
| square_order_id | string | From Square webhook |
| created_at | ISO | |
| updated_at | ISO | |
| source | string | "deli" or "html" |

### ONLINE_ORDERS Sheet
| Column | Type |
|--------|------|
| cart_id | string |
| square_payment_id | string |
| square_order_id | string |
| payment_amount_cents | number |
| payment_status | string |
| resolved_at | ISO |
| resolution_type | enum | PAID, REFUND, VOID |

---

## Implementation Plan

### Phase A: HTML → CART_STATE Normalizer
1. Transform `order_items` → `cart_items` with proper structure
2. Convert dollar amounts → cents
3. Handle modifiers as objects (not strings)
4. Generate canonical `cart_id`
5. Compute subtotal/tax/total in cents

### Phase B: Google Sheets Integration
1. Add Google Sheets nodes to HTML workflow
2. Write CART_STATE on receipt (status = OPEN)
3. Update on payment link creation (status = LOCKED, payment_link_id)
4. Ensure Disable Link workflow can find HTML orders

### Phase C: Shared Finalization
1. Reuse WKFL 4 code nodes (or extract to CORE_FINALIZER)
2. Same cart_html builder
3. Same Square payload builder
4. Same email template

### Phase D: Lifecycle Compatibility
1. Ensure HTML orders have `square_order_id` mapping
2. Test Disable Link workflow with HTML order
3. Test cleanup with HTML-generated links
4. Test refund webhook with HTML order

---

## Key Files
- `FAGmGNVzWmNOW2LP.json` — Contact + Item + Cart (70 nodes)
- `DDIlSP2iCx8V82Bw.json` — Add Another Item (52 nodes)
- `c6a983d4-085b-434c-a329-fab768652f2a.json` — Cart Renderer + Router (13 nodes)
- `ap3qRQdhYog9NxqT.json` — Order Received / WKFL 4 (20 nodes)
- `H7bUyLseYgZQfHvE.json` — Disable Payment Link (21 nodes)
- `krNiXIrpm8qsvgzD.json` — Unused Link Deletion (16 nodes)
- `YFeegOW7XYmwKmDq.json` — Refund/Void (10 nodes)
- `1WEM4rZxjhhy7ooM.json` — HTML Order V1 (11 nodes, current)
