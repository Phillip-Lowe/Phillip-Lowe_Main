# N8N Workflow Build Plan — Utopia Deli HTML Order v2

**Date:** 2026-06-05 03:24 CDT
**Status:** Ready for Copilot-assisted build
**Your instruction:** "just give me the templates and ill have copilot help me build it"

---

## PHASE 1: GitHub Backup (DONE ✅)

**Already deployed:**
- Repo: https://github.com/Phillip-Lowe/systack-n8n-workflows
- All 30 workflows exported
- Daily backup at 6 AM via cron

---

## PHASE 2: Monitoring (DONE ✅)

**Already deployed:**
- Website downtime monitor active
- Checks every hour
- Monitors: systack.net, n8n.systack.net, utopia-deli.com

---

## PHASE 3: Build Deli V2 (YOUR TASK)

### What You Need

**Files ready for you:**
1. `~/systack-n8n-workflows/workflows/systack/Utopia_Deli_HTML_Order_v2__CART_STATE_Aligned.json` (broken SQL deploy — rebuild via UI)
2. `~/systack-n8n-workflows/workflows/systack/Order_Received.json` (WKFL 4 — reference)
3. `~/systack-n8n-workflows/all-templates/ALL-TEMPLATES-PACK.md` (this doc + all template references)

### Build Steps

#### Step 1: Open n8n UI
```
https://n8n.systack.net/
```

#### Step 2: Create New Workflow
- Click "Add Workflow"
- Name: "Utopia Deli HTML Order v2 — CART_STATE Aligned"

#### Step 3: Add Nodes (14 total)

**Node 1: Webhook Trigger**
- Type: Webhook
- Method: POST
- Path: `utopia-deli-html-order-v2`
- Response Mode: responseNode

**Node 2: Validate JSON**
- Type: Function (legacy) or Code
- Checks required fields: customer_name, email, phone, order_items, subtotal, tax, total, pickup_time

**Node 3: Valid? (If/Else)**
- Condition: `$json.valid === true`
- True → continue
- False → Error Response

**Node 4: Normalize HTML → CART_STATE**
- Type: Code
- Transform order_items to cart_items structure
- Compute subtotal_cents, tax_cents, total_cents
- Generate cart_id: `UDO-YYYYMMDD-NNN`

**Node 5: Write CART_STATE → Sheets**
- Type: Google Sheets
- Operation: Append
- Document: `1jF85_1dx9WBETfhQyda2nnnKzzvTgzSbQ_uqcgArpm0`
- Sheet: CART_STATE (gid: 2016519037)
- Fields: cart_id, status=OPEN, customer_name, email, phone, cart_items_json, subtotal_cents, tax_cents, total_cents

**Node 6: Create Payment Link (Square)**
- Type: HTTP Request
- Method: POST
- URL: `https://connect.squareup.com/v2/online-checkout/payment-links`
- Auth: httpHeaderAuth (Square API credential)
- Headers: Square-Version=2026-01-22, Content-Type=application/json
- Body: JSON with order reference_id=cart_id, line_items, metadata

**Node 7: Normalize Payment Response**
- Type: Code
- Extract payment_link.url and payment_link.id from HTTP response

**Node 8: Build cart_html**
- Type: Code
- Renders cart_items into branded HTML table
- Handles: items, modifiers, take-offs, add-ons, totals

**Node 9: Email Template**
- Type: Code or Set
- Loads branded HTML template with __CART_HTML__, __PAYMENT_LINK__, __CURRENT_YEAR__ placeholders

**Node 10: Update CART_STATE → LOCKED**
- Type: Google Sheets
- Operation: Update
- Match on: cart_id
- Fields: status=LOCKED, payment_link_id, payment_link_url, updated_at

**Node 11: Compose Final Email**
- Type: Code
- Inject cart_html and payment_link into template
- Replace placeholders

**Node 12: Send Payment Email**
- Type: Email Send
- SMTP credential: deli gmail
- From: theutopiadelilittlerock@gmail.com
- To: customer_email
- Subject: "Your Utopia Deli Order — Payment Required"
- HTML body: final_email_html

**Node 13: Success Response**
- Type: Respond to Webhook
- Status: 200
- Body: `{success: true, order_id: cart_id, payment_url: payment_link_url}`

**Node 14: Error Response**
- Type: Respond to Webhook
- Status: 400
- Body: `{success: false, error: error_message}`

#### Step 4: Connect Nodes

```
Webhook → Validate → If Valid?
  ├── NO → Error Response
  └── YES → Normalize CART_STATE → [Write Sheets + Create Payment Link (parallel)]
                                      ↓                          ↓
                                Build cart_html          Normalize Payment Response
                                      ↓                          ↓
                                Email Template          Update CART_STATE → LOCKED
                                      ↓                          ↓
                                Compose Final Email ←─────── (merge here)
                                      ↓
                                Send Email
                                      ↓
                                Success Response
```

#### Step 5: Add Credentials

| Service | Credential ID | Type |
|---------|--------------|------|
| SMTP/Email | `ZOvYr6kSP7zE8tBv` | deli gmail |
| Square API | `9FQ7SQhaUqssIJJb` | httpHeaderAuth |
| Google Sheets | (OAuth) | Auto-resolved |

#### Step 6: Test

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
    "pickup_time": "14:30"
  }'
```

#### Step 7: Activate
- Toggle "Active" in n8n UI
- Webhook URL becomes live

---

## COPLLOT PROMPTS

### Prompt 1: Build the whole workflow
```
Build an n8n workflow with this exact architecture:

1. Webhook trigger (POST /webhook/utopia-deli-html-order-v2)
2. Validate JSON fields (customer_name, email, phone, order_items[], subtotal, tax, total, pickup_time)
3. If valid: continue, else: return 400 error
4. Code node: Transform order_items to cart_items with structure {type, display_name, quantity, base_price_cents, modifiers[{mod_name, price_delta}]}
5. Code node: Generate cart_id as "UDO-" + YYYYMMDD + random 3 digits
6. Parallel branches:
   a) Google Sheets append to CART_STATE sheet (status=OPEN)
   b) HTTP Request to Square API POST /v2/online-checkout/payment-links with line_items and tax as separate item
7. After both complete: 
   a) Code node: Build branded cart HTML with items, modifiers, take-offs, add-ons, totals
   b) Code node: Inject cart_html and payment_link into email template
   c) Email Send node via SMTP (credential deli gmail, from theutopiadelilittlerock@gmail.com)
   d) Update CART_STATE status to LOCKED with payment_link_id
8. Respond to webhook with {success: true, order_id, payment_url}

Square location_id: J4B6A3X6RYA63
Tax rate: 9.52% as separate line item
```

### Prompt 2: Build just the CART_STATE normalizer
```
Write n8n Code node (ES5 compatible) that:
- Takes input payload with order_items[{name, qty, price, modifiers: [string]}]
- Transforms to cart_items[{type: "primary", display_name, quantity, base_price_cents, variant_price_cents: 0, modifiers[{mod_name, price_delta}], notes, line_total_cents}]
- Parses modifier strings: "+ Addon Name ($0.50)" → {mod_name: "+ Addon Name ($0.50)", price_delta: 0.50}
- "no onions" → {mod_name: "no onions", price_delta: 0}
- Computes subtotal_cents, tax_cents, total_cents
- Validates: subtotal + tax == total
- Returns cart_id, status="OPEN", customer fields, cart_items_json (stringified), totals
```

### Prompt 3: Build just the email HTML builder
```
Write n8n Code node (ES5 compatible) that:
- Takes cart_items array and subtotal_cents, tax_cents, total_cents
- Builds HTML table with branded styling (Utopia Deli colors: #590B3F, #FBF6F6, #8C2F39)
- Handles: item headers, identifiers (free modifiers), take-offs ("no" prefix), add-ons (+ prefix with price)
- Money formatting: "$" + (cents/100).toFixed(2)
- Returns cart_html string
```

---

## REFERENCE TEMPLATES

| Template | URL | What to copy |
|----------|-----|-------------|
| **Order Received (WKFL 4)** | In your n8n instance | cart_html BUILDER, Square Line-Item Builder, Email Template, FINAL EMAIL COMPOSER |
| **Concert Ticket Booking** | https://n8n.io/workflows/13453 | Validation agent pattern, audit trail, SLA escalation |
| **Website Downtime** | https://n8n.io/workflows/11763 | Email alert format, monitoring pattern |
| **Personal Agent** | https://n8n.io/workflows/8237 | Telegram + voice + memory (future kitchen interface) |

---

## DELIVERY

**All files are in:**
```
~/systack-n8n-workflows/
├── workflows/systack/Order_Received.json          ← Copy cart_html builder from here
├── workflows/systack/Contact__Item__Cart.json       ← Copy CART_STATE format from here
├── all-templates/ALL-TEMPLATES-PACK.md              ← Full template reference
└── architecture/PERSONAL-AGENT-SPEC.md              ← Future: kitchen Telegram bot
```

**GitHub:** https://github.com/Phillip-Lowe/systack-n8n-workflows

---

## YOUR ACTION ITEMS

1. ✅ Open n8n UI
2. ✅ Create new workflow
3. ✅ Build 14 nodes (use Copilot for code nodes)
4. ✅ Connect nodes
5. ✅ Add credentials
6. ✅ Test with curl
7. ✅ Activate
8. ✅ Update frontend webhook URL to `/webhook/utopia-deli-html-order-v2`

**Need help?** Ask Copilot using the prompts above.

---

**Plan complete. Ready to build.**
