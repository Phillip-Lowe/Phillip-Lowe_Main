# Utopia Deli — Exact Code Change Required

## Node to Change
**Workflow:** `Utopia-Deli-Simple-Checkout-v4`  
**Node:** `Create Square Pickup Order Payment Link` (HTTP Request node)

## Current Code (WRONG)
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

## Replace With (CORRECT)
```javascript
line_items: $json.body.items.map(item => ({
  name: item.name,
  quantity: String(item.qty),
  base_price_money: {
    amount: item.base_price_cents || Math.round(item.total_price_cents / item.qty),
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

## What Changed
Only one line:
- **Before:** `amount: Math.round(item.total_price_cents / item.qty)`
- **After:** `amount: item.base_price_cents || Math.round(item.total_price_cents / item.qty)`

This tells n8n to use the `base_price_cents` that the frontend sends (which already has combo prices subtracted), and only fall back to `total_price_cents / qty` if `base_price_cents` doesn't exist.

## Why This Fixes It

**Before:**
- Frontend sends: item=$15 + combo=$5 = total $20
- n8n calculates base: $20/1 = $20
- Square charges: $20 + $0 (combo at $0) = $20 ❌

**After:**
- Frontend sends: base=$15 (combo subtracted), combo=$0
- n8n uses base: $15
- Square charges: $15 + $0 (combo at $0) = $15 ✅

## Modifier Pattern Summary

| Modifier Type | Code Pattern | Should Charge | Reason |
|--------------|-------------|---------------|--------|
| Combo | `*_COMBO_*` | NO | Price included in item base price |
| Free/Take-off | `*_HOLD_*`, `*_NO_*` | NO | No additional charge |
| Paid Add-on | `*_ADDONS_*`, `*_SAUCE_*` | YES | Extra cost |

All combo modifiers in database have `base_price=0.00`, confirming they should be free.
