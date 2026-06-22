/**
 * HTML TO CART_STATE NORMALIZER
 *
 * PURPOSE:
 *   Transform HTML frontend payload into canonical CART_STATE format
 *   so HTML orders can enter the SAME finalization pipeline as deli workflows.
 *
 * INPUT (HTML Payload):
 *   {
 *     customer_name: "Jane Doe",
 *     email: "jane@example.com",
 *     phone: "(501) 555-1234",
 *     order_items: [
 *       { name: "The Cowboy", qty: 1, price: 10.99, modifiers: ["+ Avocado", "no onions"] }
 *     ],
 *     subtotal: 10.99,
 *     tax: 1.05,
 *     total: 12.04,
 *     pickup_time: "14:30",
 *     special_instructions: "Extra napkins please"
 *   }
 *
 * OUTPUT (Canonical CART_STATE):
 *   {
 *     cart_id: "UDO-20260605-123",
 *     status: "OPEN",
 *     customer_name: "Jane Doe",
 *     customer_email: "jane@example.com",
 *     customer_phone: "(501) 555-1234",
 *     cart_items: [...],
 *     cart_items_json: "<stringified>",
 *     subtotal_cents: 1099,
 *     tax_cents: 105,
 *     total_cents: 1204,
 *     created_at: "<ISO>",
 *     updated_at: "<ISO>",
 *     source: "html"
 *   }
 */

const input = $json.payload || $json;

// ─────────────────────────────────────────────
// 1. Generate cart_id (same format as HTML v1)
// ─────────────────────────────────────────────
const now = new Date();
const date = now.toISOString().slice(0, 10).replace(/-/g, "");
const random = Math.floor(Math.random() * 900) + 100;
const cartId = "UDO-" + date + "-" + random;

// ─────────────────────────────────────────────
// 2. Transform order_items → cart_items
// ─────────────────────────────────────────────
const orderItems = Array.isArray(input.order_items) ? input.order_items : [];

const cartItems = orderItems.map(function(item, idx) {
  const qty = Number(item.qty || 1);
  const priceDollars = Number(item.price || 0);
  const basePriceCents = Math.round(priceDollars * 100);

  // Parse modifiers from string array to structured objects
  const rawModifiers = Array.isArray(item.modifiers) ? item.modifiers : [];
  const modifiers = rawModifiers.map(function(modStr) {
    const trimmed = String(modStr).trim();

    // Detect add-ons: starts with "+ " and has price in parens
    const addonMatch = trimmed.match(/^\+\s+(.+?)\s*\(\$?([\d.]+)\)$/);
    if (addonMatch) {
      return {
        mod_name: trimmed,           // Keep full string for display
        price_delta: Number(addonMatch[2])  // e.g., 0.50
      };
    }

    // Detect take-offs: starts with "no " or "no-" or "hold " or "hold-"
    if (/^(no\s|no-|hold\s|hold-)/i.test(trimmed)) {
      return {
        mod_name: trimmed,
        price_delta: 0
      };
    }

    // Everything else (identifiers, choices) = $0
    return {
      mod_name: trimmed,
      price_delta: 0
    };
  });

  // Calculate line total
  const addonTotalCents = modifiers.reduce(function(sum, m) {
    return sum + Math.round(Number(m.price_delta || 0) * 100 * qty);
  }, 0);
  const lineTotalCents = (basePriceCents * qty) + addonTotalCents;

  return {
    type: "primary",
    display_name: item.name || "Item " + (idx + 1),
    quantity: qty,
    base_price_cents: basePriceCents,
    variant_price_cents: 0,
    modifiers: modifiers,
    notes: item.notes || "",
    line_total_cents: lineTotalCents
  };
});

// ─────────────────────────────────────────────
// 3. Compute canonical totals in cents
// ─────────────────────────────────────────────
const subtotalCents = Math.round(Number(input.subtotal || 0) * 100);
const taxCents = Math.round(Number(input.tax || 0) * 100);
const totalCents = Math.round(Number(input.total || 0) * 100);

// Validate: subtotal + tax == total
if (subtotalCents + taxCents !== totalCents) {
  throw new Error(
    "TOTAL_MISMATCH: subtotal (" + subtotalCents + ") + tax (" + taxCents + 
    ") != total (" + totalCents + ")"
  );
}

// ─────────────────────────────────────────────
// 4. Build canonical CART_STATE
// ─────────────────────────────────────────────
const cartState = {
  cart_id: cartId,
  status: "OPEN",

  customer_name: input.customer_name || "",
  customer_email: input.email || "",
  customer_phone: input.phone || "",

  cart_items: cartItems,
  cart_items_json: JSON.stringify(cartItems),

  subtotal_cents: subtotalCents,
  tax_cents: taxCents,
  total_cents: totalCents,

  created_at: now.toISOString(),
  updated_at: now.toISOString(),

  source: "html"
};

// ─────────────────────────────────────────────
// 5. Also build Square line items for immediate use
// ─────────────────────────────────────────────
const squareLineItems = cartItems.map(function(item) {
  const lineItem = {
    name: item.display_name,
    quantity: String(item.quantity),
    base_price_money: {
      amount: item.base_price_cents,
      currency: "USD"
    },
    modifiers: []
  };

  if (Array.isArray(item.modifiers)) {
    item.modifiers.forEach(function(mod) {
      lineItem.modifiers.push({
        name: mod.mod_name,
        base_price_money: {
          amount: Math.round(Number(mod.price_delta || 0) * 100),
          currency: "USD"
        }
      });
    });
  }

  return lineItem;
});

// Add tax as separate line item (WKFL 4 pattern)
if (taxCents > 0) {
  squareLineItems.push({
    name: "Tax",
    quantity: "1",
    base_price_money: {
      amount: taxCents,
      currency: "USD"
    }
  });
}

// ─────────────────────────────────────────────
// 6. Output
// ─────────────────────────────────────────────
return {
  ...cartState,
  square_line_items: squareLineItems,       // Without tax (for other uses)
  square_line_items_with_tax: squareLineItems,  // With tax (for Square API)
  pickup_time: input.pickup_time || "",
  special_instructions: input.special_instructions || ""
};
