# ORACLE HANDOUT — Utopia Deli Combo Fix
**Date:** 2026-06-26
**Session:** SOL (with user frustration due to assistant confusion)
**Status:** INCOMPLETE — needs Oracle verification

---

## What Happened (The Confusion)

SOL (the assistant) got lost trying to figure out which n8n workflow is active. He looked at:
- `Utopia_Deli__HTML_Order_Fleet_Canon.json` (OLD workflow, not active)
- `Utopia-Deli-Simple-Checkout-v4.json` (the ACTUAL active workflow)
- Wrong git repos (`Phillip-Lowe_Main` instead of `Phillip-Lowe/utopia-deli`)

**Result:** SOL wasted time on the wrong files and confused everyone.

---

## What Was Actually Fixed

### 1. Frontend (DEPLOYED ✅)
**Repo:** `Phillip-Lowe/utopia-deli`
**File:** `pickup-order/order-form.js`
**Commit:** `11763ba`

**Changes:**
- Updated webhook URL from `utopia-deli-html-order-v1` to `utopia-deli-order-v4`
- Changed payload format to match V4 workflow expectations:
  ```javascript
  {
    body: {
      customer: { name, email, phone },
      items: [{
        name,
        qty,
        base_price_cents,
        modifiers: [{ label, price_delta }]
      }],
      notes
    }
  }
  ```

### 2. n8n Workflow (NEEDS MANUAL UPDATE)
**Workflow:** `Utopia-Deli-Simple-Checkout-v4`
**Node:** `Create Square Payment Link`

**Current code (WRONG — no modifiers):**
```javascript
line_items: $json.body.items.map(item => ({
  name: item.name,
  quantity: String(item.qty),
  base_price_money: {
    amount: Math.round(item.total_price_cents / item.qty),
    currency: "USD"
  }
}))
```

**New code (CORRECT — with modifiers):**
```javascript
line_items: $json.body.items.map(item => ({
  name: item.name,
  quantity: String(item.qty),
  base_price_money: {
    amount: Math.round(item.base_price_cents || (item.total_price_cents / item.qty)),
    currency: "USD"
  },
  modifiers: (item.modifiers || []).map(mod => ({
    name: mod.label || mod.mod_name || 'Unknown',
    base_price_money: {
      amount: Math.round((mod.price_delta || 0) * 100),
      currency: "USD"
    }
  }))
}))
```

**Action needed:** Paste the "New code" block into the `Create Square Payment Link` node in n8n.

---

## Why This Matters

**Before fix:**
- Customer orders "Cowboy Chik'n Sandwich + COMBO: Fries"
- Square shows kitchen: "Cowboy Chik'n Sandwich — $18.00"
- Kitchen can't tell if it's fries or salad → wrong order

**After fix:**
- Customer orders "Cowboy Chik'n Sandwich + COMBO: Fries"
- Square shows kitchen: "Cowboy Chik'n Sandwich — $18.00" + "COMBO: Fries"
- Kitchen sees exactly what to make

---

## Files Changed (Local Copies Only)

| File | Location | Status |
|------|----------|--------|
| `order-form.js` | `~/.openclaw/workspaces/sol/utopia-deli-temp/pickup-order/` | ✅ Pushed to GitHub |
| `Utopia-Deli-Simple-Checkout-v4.json` | `~/.openclaw/workspaces/sol/Systack/n8n-workflows/deli/` | ❌ NOT imported to n8n |

**Important:** The n8n workflow JSON file was updated locally but NOT imported into the active n8n instance. You need to manually paste the code into the existing workflow.

---

## What Still Needs To Happen

1. ✅ **Frontend deployed** — `order.theutopiadeli.com` now posts to V4
2. ❌ **n8n workflow updated** — Need to paste modifier code into active workflow
3. ❌ **Test order placed** — Verify kitchen sees "COMBO: Fries"

---

## For Oracle

**What to check:**
1. Log into n8n.systack.net
2. Find workflow: `Utopia-Deli-Simple-Checkout-v4`
3. Open node: `Create Square Payment Link`
4. Replace the `line_items` code with the block above
5. Save workflow
6. Place test order with combo
7. Verify kitchen notification shows combo selection

**If something breaks:**
- The old code is backed up in the same node (just undo)
- Frontend can be reverted to `utopia-deli-html-order-v1` if needed

---

## Source of Truth

**Active workflow:** `Utopia-Deli-Simple-Checkout-v4`
**Webhook URL:** `https://n8n.systack.net/webhook/utopia-deli-order-v4`
**Frontend repo:** `https://github.com/Phillip-Lowe/utopia-deli`
**Deployed site:** `https://order.theutopiadeli.com`

---

## Lesson Learned

SOL got confused because:
1. Didn't check memory first to find the correct repo
2. Looked at exported JSON files instead of asking "what's active in n8n?"
3. Tried to export/import a whole workflow when only 20 lines needed changing
4. Got lost in file paths instead of focusing on the actual problem

**Next time:** Ask "what's the active webhook URL?" first, then give code.
