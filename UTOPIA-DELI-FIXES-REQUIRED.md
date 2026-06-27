# Utopia Deli Fixes Required (Based on Oracle's Findings)

## Fix 1: n8n V4 Workflow — Add Modifiers to Square Line Items
**Location:** `Utopia-Deli-Simple-Checkout-v4` → `Create Square Payment Link` node

**Replace the line_items code with:**
```javascript
line_items: $json.body.items.map(item => ({
  name: item.name,
  quantity: String(item.qty),
  base_price_money: {
    amount: Math.round(item.total_price_cents / item.qty),
    currency: "USD"
  },
  modifiers: (item.modifiers || []).map(mod => ({
    name: mod.label || 'Unknown',
    base_price_money: {
      amount: mod.price_cents || 0,
      currency: "USD"
    }
  }))
}))
```

**Critical:** Use `mod.price_cents` (not `price_delta`) based on actual payload.

---

## Fix 2: Frontend — Stop Double-Charging Combos
**Location:** `order-form.js` → `addToCart()` function

**Issue:** Combo modifiers have `price: 500` in menu data, so they're added to item total AND sent as modifiers.

**Solution:** When building the payload for V4, set combo modifier prices to 0:

```javascript
modifiers: cartItem.modifiers.map(m => ({
  code: m.code,
  label: m.label,
  price_cents: m.code.includes('COMBO') ? 0 : (m.price || 0)
}))
```

**OR** in the n8n Compute Totals node, subtract combo modifier prices from total.

---

## Fix 3: Frontend Display Page Update
**Location:** `index.html` → Order confirmation/success message

**Current message:** (whatever it says now)

**New message should say:**
"Order received. Click on the payment link below to complete your payment. We will start working on your order once payment is completed."

---

## Fix 4: SQLite Save Failure
**Error:** `"db_saved": false`

**Location:** `Save to SQLite` node in V4 workflow

**Action:** Check SQLite node configuration — likely wrong table name, column mismatch, or connection issue.

---

## What Oracle Confirmed
✅ Frontend IS sending combo modifiers  
✅ Webhook IS receiving modifiers  
✅ Compute Totals IS preserving modifiers  
❌ Square payload drops modifiers  
❌ Combo is being double-charged  
❌ SQLite save is failing  

---

## Priority Order
1. Fix double-charging (affects revenue)
2. Fix Square modifiers (affects kitchen visibility)
3. Fix SQLite save (affects order tracking)
4. Update display message (UX improvement)
