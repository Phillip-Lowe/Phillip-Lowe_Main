# Frankenstein V1 — Working Code Extraction
# Date: 2026-06-05
# These are the nodes with code that the user says is correct

## NODE: Validate JSON
## Type: n8n-nodes-base.function (v1)

```javascript
let input = items[0].json.body || items[0].json;

const required = [
  "customer_name",
  "email",
  "phone",
  "order_items",
  "subtotal",
  "tax",
  "total"
];

for (const field of required) {
  if (!input[field]) {
    throw new Error(`Missing field: ${field}`);
  }
}

return [{ json: input }];
```

---

## NODE: Normalize + Carry Data
## Type: n8n-nodes-base.function (v1)

```javascript
const httpResponse = items[0].json;

// Debug: log what we received
console.log("HTTP Response keys:", Object.keys(httpResponse));
console.log("HTTP Response:", JSON.stringify(httpResponse, null, 2).substring(0, 500));

// Extract payment link data
let paymentUrl = "";
let paymentId = "";

if (httpResponse.payment_link) {
  paymentUrl = httpResponse.payment_link.url || "";
  paymentId = httpResponse.payment_link.id || "";
} else if (httpResponse.body && httpResponse.body.payment_link) {
  paymentUrl = httpResponse.body.payment_link.url || "";
  paymentId = httpResponse.body.payment_link.id || "";
}

const original = items[0].json;

// Get order items from original payload
let orderItems = [];
try {
  const payload = original.payload || original;
  if (payload.order_items) {
    orderItems = typeof payload.order_items === 'string' 
      ? JSON.parse(payload.order_items) 
      : payload.order_items;
  }
} catch(e) {
  orderItems = [];
}

return [{
  json: {
    payment_link_url: paymentUrl,
    payment_link_id: paymentId,
    email: original.email,
    customer_name: original.customer_name,
    order_id: original.order_id,
    phone: original.phone,
    pickup_time: original.pickup_time,
    special_instructions: original.special_instructions || "",
    order_items: orderItems,
    order_items_sql: original.order_items_sql,
    subtotal: original.subtotal,
    tax: original.tax,
    total: original.total
  }
}];
```

---

## NODE: Build Payment Email
## Type: n8n-nodes-base.code (v1)

```javascript
var data = $json;

var items = Array.isArray(data.order_items) ? data.order_items : [];

var subtotal = Number(data.subtotal || 0);
var tax = Number(data.tax || 0);
var total = Number(data.total || 0);
var customerEmail = data.email || "";
var customerName = data.customer_name || "";
var orderId = data.order_id || "";
var paymentUrl = data.payment_link_url || "#";

// Build cart
var cartHtml = "<table style='width:100%;border-collapse:collapse;'>";

for (var i = 0; i < items.length; i++) {
  var item = items[i];
  var itemTotal = Number(item.price || 0) * Number(item.qty || 1);

  cartHtml += "<tr>";
  cartHtml += "<td style='padding:8px 0;border-bottom:1px solid #E6E1E1;'>";
  cartHtml += "<strong style='color:#590B3F;font-size:15px;'>" + (item.name || "Item") + "</strong><br/>";

  if (item.modifiers && item.modifiers.length > 0) {
    cartHtml += "<span style='color:#8A8585;font-size:12px;'>" + item.modifiers.join(", ") + "</span>";
  }

  cartHtml += "</td>";
  cartHtml += "<td style='padding:8px 0;border-bottom:1px solid #E6E1E1;text-align:right;color:#590B3F;font-weight:600;'>$" + itemTotal.toFixed(2) + "</td>";
  cartHtml += "</tr>";
}

cartHtml += "<tr><td style='padding:12px 0;font-size:14px;color:#1F1B1D;'>Subtotal</td>";
cartHtml += "<td style='padding:12px 0;text-align:right;font-weight:600;'>$" + subtotal.toFixed(2) + "</td></tr>";

cartHtml += "<tr><td style='padding:8px 0;font-size:14px;color:#1F1B1D;'>Tax</td>";
cartHtml += "<td style='padding:8px 0;text-align:right;font-weight:600;'>$" + tax.toFixed(2) + "</td></tr>";

cartHtml += "<tr><td style='padding:12px 0;font-size:16px;font-weight:700;color:#590B3F;'>Total</td>";
cartHtml += "<td style='padding:12px 0;text-align:right;font-size:16px;font-weight:700;color:#590B3F;'>$" + total.toFixed(2) + "</td></tr>";

cartHtml += "</table>";

var year = new Date().getFullYear();

var btn = "<a href='" + paymentUrl + "' style='background:#8C2F39;color:#ffffff;padding:14px 24px;border-radius:24px;text-decoration:none;font-weight:bold;display:inline-block;'>Complete Payment</a>";

var h = "";
h += "<div style='font-family:Arial,sans-serif;max-width:600px;margin:auto;background:#FBF6F6;padding:24px;'>";
h += "<div style='text-align:center;margin-bottom:24px;'>";
h += "<a href='https://www.theutopiadeli.com' target='_blank' style='text-decoration:none;'>";
h += "<img src='https://cdn.shopify.com/s/files/1/0763/5042/3270/files/TheUtopiaDeliLogo_menu.png?v=1774974380' alt='The Utopia Deli' style='max-width:220px;height:auto;border:none;' />";
h += "</a></div>";

h += "<p style='color:#590B3F;font-size:26px;font-weight:700;line-height:1.35;margin:0 0 18px 0;'>We will begin preparing your order once we receive your payment.</p>";
h += "<p style='font-style:italic;color:#754681;font-size:16px;margin:0 0 22px 0;'>The Utopia Deli. It is just good food.</p>";
h += "<p style='color:#1F1B1D;font-size:14px;margin:0 0 20px 0;'>Please review your order and complete your secure payment below:</p>";

h += "<h3 style='color:#590B3F;margin-top:32px;margin-bottom:12px;font-size:18px;'>Order Summary</h3>";
h += cartHtml;

h += "<hr style='border:none;border-top:1px solid #E6E1E1;margin:24px 0;' />";
h += "<div style='margin:24px 0;text-align:center;'>" + btn + "</div>";

h += "<p style='margin-top:12px;font-size:12px;color:#8A8585;text-align:center;line-height:1.6;'>";
h += "&copy; " + year + "<br/>";
h += "<a href='https://www.theutopiadeli.com' target='_blank' style='color:#590B3F;text-decoration:none;font-weight:600;'>The Utopia Deli</a><br/>";
h += "Pickup Order &middot; 801 S Chester St, Little Rock, AR 72202<br/>";
h += "<a href='tel:+15015515944' style='color:#8A8585;text-decoration:none;'>+1 (501) 551-5944</a> &middot; ";
h += "<a href='mailto:theutopiadelilittlerock@gmail.com' style='color:#8A8585;text-decoration:none;'>theutopiadelilittlerock@gmail.com</a>";
h += "</p>";
h += "</div>";

return [{
  json: {
    order_id: orderId,
    customer_email: customerEmail,
    customer_name: customerName,
    email_html: h,
    payment_url: paymentUrl
  }
}];

```

---

## NODE: PREP_RESPONSE
## Type: n8n-nodes-base.code (v1)

```javascript
return [{
  json: {
    order_id: items[0].json.order_id,
    payment_url: items[0].json.payment_url
  }
}];
```

---

## NODE: NORMALIZE_TO_CART_STATE
## Type: n8n-nodes-base.function (v1)

```javascript
const input = $json;

const cart_items = input.order_items.map(item => ({
  display_name: item.name,
  quantity: item.qty,
  base_price_cents: Math.round(Number(item.price) * 100),
  variant_price_cents: 0,
  modifiers: [],
  line_total_cents:
    Math.round(Number(item.price) * 100) * item.qty
}));

const now = new Date();

return {
  cart_id: "HTML-" + now.getTime(),

  status: "OPEN",

  customer_email: input.email,
  customer_name: input.customer_name,
  customer_phone: input.phone,

  cart_items,
  cart_items_json: JSON.stringify(cart_items),

  subtotal_cents: Math.round(input.subtotal * 100),
  tax_cents: Math.round(input.tax * 100),
  total_cents: Math.round(input.total * 100),

  source: "html_webhook"
};
```

---

## NODE: Validate Total
## Type: n8n-nodes-base.code (v2)

```javascript
if (
  $json.total_cents !==
  ($json.subtotal_cents + $json.tax_cents)
) {
  throw new Error(
    `TOTAL_MISMATCH: subtotal (${ $json.subtotal_cents }) + tax (${ $json.tax_cents }) != total (${ $json.total_cents })`
  );
}

return $json;
``
```

---

## NODE: Required‑Fields
## Type: n8n-nodes-base.code (v2)

```javascript
const missing = [];

if (!$json.customer_email) missing.push("customer_email");
if (!$json.payment_link_url && !$json.create_payment_link) {
  // payment_link_url may be created later, but at least intent must exist
  missing.push("payment_link_url or payment link creation step");
}
if (!$json.cart_html) missing.push("cart_html");

if (missing.length) {
  throw new Error(
    `WKFL-4 PRECONDITION FAILED: missing ${missing.join(", ")}`
  );
}

return $json;
```

---

## NODE: cart_html BUILDER
## Type: n8n-nodes-base.code (v2)

```javascript
const input = $json;

// ─────────────────────────────────────────────
// Resolve cart_items safely (live or committed)
// ─────────────────────────────────────────────
let cart_items = input.cart_items;

if (!Array.isArray(cart_items)) {
  if (typeof input.cart_items_json === "string") {
    try {
      cart_items = JSON.parse(input.cart_items_json);
    } catch {
      throw new Error("cart_items_json is invalid JSON");
    }
  }
}

if (!Array.isArray(cart_items)) {
  throw new Error("cart_html builder requires cart_items or cart_items_json");
}

// ─────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────
const money = cents =>
  `$${(Number(cents || 0) / 100).toFixed(2)}`;

// ✅ TAKE‑OFF detector (semantic convention)
const isTakeOff = mod =>
  typeof mod?.mod_name === "string" &&
  /^(no |no-|hold |hold-)/i.test(mod.mod_name.trim());

// ✅ Note sanitizer (defensive; notes are trusted today,
// but this future‑proofs rendering)
const sanitizeText = txt =>
  String(txt).replace(/[<>]/g, "");

// Brand tokens (email + HTML safe)
const BRAND_MUTED = "#555";
const BRAND_SUBTLE = "#777";

// ─────────────────────────────────────────────
// Build cart rows
// ─────────────────────────────────────────────
let rows = "";

cart_items.forEach((item, idx) => {
  const qty = Number(item.quantity || 1);

  const baseUnitCents =
    Number(item.base_price_cents || 0) +
    Number(item.variant_price_cents || 0);

  const baseDisplayCents = baseUnitCents * qty;

  const modifiers = Array.isArray(item.modifiers) ? item.modifiers : [];

  // ✅ IDENTIFIERS (protein / choice, $0)
  const identifiers = modifiers.filter(
    m => !isTakeOff(m) && Number(m.price_delta) === 0
  );

  // ✅ TAKE‑OFFS
  const takeoffs = modifiers.filter(isTakeOff);

  // ✅ ADD‑ONS
  const addons = modifiers.filter(
    m => !isTakeOff(m) && Number(m.price_delta) > 0
  );

  // Spacer between items
  if (idx > 0) {
    rows += `
      <tr>
        <td colspan="2" style="padding-top:14px;"></td>
      </tr>
    `;
  }

  // ── ITEM HEADER ────────────────────────────
  rows += `
    <tr>
      <td>
        <strong>${qty > 1 ? `${qty} × ` : ""}${item.display_name}</strong>
      </td>
      <td style="text-align:right;">
        <strong>${money(baseDisplayCents)}</strong>
      </td>
    </tr>
  `;

  // ── IDENTIFIERS (FIRST) ────────────────────
  identifiers.forEach(m => {
    rows += `
      <tr>
        <td style="padding-left:24px; font-style:italic;">
          ${m.mod_name}
        </td>
        <td></td>
      </tr>
    `;
  });

  // ── TAKE OFF ───────────────────────────────
  if (takeoffs.length > 0) {
    rows += `
      <tr>
        <td colspan="2"
            style="padding-left:24px;
                   font-size:11px;
                   font-weight:600;
                   color:${BRAND_MUTED};
                   padding-top:4px;">
          TAKE OFF
        </td>
      </tr>
    `;
  }

  takeoffs.forEach(m => {
    rows += `
      <tr>
        <td style="padding-left:24px; font-style:italic; color:${BRAND_MUTED};">
          ${m.mod_name}
        </td>
        <td></td>
      </tr>
    `;
  });

  // ── ADD‑ONS ────────────────────────────────
  if (addons.length > 0) {
    rows += `
      <tr>
        <td colspan="2"
            style="padding-left:24px;
                   font-size:11px;
                   font-weight:600;
                   color:${BRAND_MUTED};
                   padding-top:6px;">
          ADD‑ONS
        </td>
      </tr>
    `;
  }

  addons.forEach(m => {
    rows += `
      <tr>
        <td style="padding-left:24px;">
          + ${m.mod_name}
        </td>
        <td style="text-align:right;">
          ${money(Number(m.price_delta) * 100)}
        </td>
      </tr>
    `;
  });

  // ── ITEM‑SCOPED NOTES (MODEL 3) ────────────
  if (item.notes && String(item.notes).trim()) {
    const safeNote = sanitizeText(item.notes);

    rows += `
      <tr>
        <td colspan="2"
            style="padding-left:24px;
                   font-style:italic;
                   color:${BRAND_MUTED};
                   padding-top:6px;">
          Notes: ${safeNote}
        </td>
      </tr>
    `;
  }

  // ── ITEM TOTAL (ONLY IF ADD‑ONS EXIST) ─────
  if (addons.length > 0) {
    rows += `
      <tr>
        <td style="padding-left:24px; font-weight:600;">
          Item total
        </td>
        <td style="text-align:right; font-weight:600;">
          ${money(item.line_total_cents)}
        </td>
      </tr>
    `;
  }
});

// ─────────────────────────────────────────────
// Final cart HTML
// ─────────────────────────────────────────────
const cart_html = `
<table width="100%" cellpadding="0" cellspacing="0">
  ${rows}

  <tr><td colspan="2"><hr></td></tr>

  <tr>
    <td><strong>Subtotal</strong></td>
    <td style="text-align:right;"><strong>${money(input.subtotal_cents)}</strong></td>
  </tr>

  <tr>
    <td>Tax</td>
    <td style="text-align:right;">${money(input.tax_cents)}</td>
  </tr>

  <tr>
    <td style="padding-top:10px;"><strong>Total</strong></td>
    <td style="padding-top:10px; text-align:right;"><strong>${money(input.total_cents)}</strong></td>
  </tr>
</table>
`;

// ─────────────────────────────────────────────
// Output
// ─────────────────────────────────────────────
return {
  ...input,
  cart_html,
};

```

---

## NODE: Cart Rehydration
## Type: n8n-nodes-base.code (v2)

```javascript
const input = $json;

// ----------------------------------
// Guard
// ----------------------------------
if (!input.cart_items_json) {
  throw new Error("Missing cart_items_json for cart rehydration");
}

let cart_items;

try {
  cart_items = JSON.parse(input.cart_items_json);
} catch {
  throw new Error("cart_items_json is not valid JSON");
}

if (!Array.isArray(cart_items)) {
  throw new Error("cart_items_json must parse to an array");
}

// ----------------------------------
// Output hydrated cart
// ----------------------------------
return {
  ...input,
  cart_items
};
```

---

## NODE: Square Line‑Item Builder
## Type: n8n-nodes-base.code (v2)

```javascript
const input = $json;

// ----------------------------------
// Guards
// ----------------------------------
if (!Array.isArray(input.cart_items) || input.cart_items.length === 0) {
  throw new Error("WKFL-4: cart_items missing or empty");
}

const square_line_items = [];

input.cart_items.forEach(item => {
  const quantity = String(item.quantity || 1);

  if (
    !Number.isInteger(item.base_price_cents) ||
    item.base_price_cents <= 0
  ) {
    throw new Error(`Invalid base_price_cents for ${item.display_name}`);
  }

  // ✅ Main line item (BASE PRICE ONLY)
  const line_item = {
    name: item.display_name,
    quantity,
    base_price_money: {
      amount: item.base_price_cents,
      currency: "USD"
    },
    modifiers: []
  };

  // ✅ Modifiers (protein, add-ons, take-offs)
  if (Array.isArray(item.modifiers)) {
    item.modifiers.forEach(mod => {
      const deltaCents = Math.round(
        Number(mod.price_delta || 0) * 100
      );

      line_item.modifiers.push({
        name: mod.mod_name,
        base_price_money: {
          amount: deltaCents, // 0 allowed
          currency: "USD"
        }
      });
    });
  }

  square_line_items.push(line_item);
});

// ----------------------------------
// Output
// ----------------------------------
return {
  ...input,
  square_line_items
};
```

---

## NODE: FINAL EMAIL COMPOSER
## Type: n8n-nodes-base.code (v2)

```javascript
// ===============================
// FINAL EMAIL COMPOSER (PAYMENT)
// ===============================

// ---- Validate template ----
if (
  !$json.confirmation_email_template ||
  typeof $json.confirmation_email_template !== 'string'
) {
  throw new Error('❌ Final Email Composer: Missing confirmation_email_template');
}

// ---- Validate cart HTML ----
if (
  !$json.cart_html ||
  typeof $json.cart_html !== 'string'
) {
  throw new Error('❌ Final Email Composer: Missing cart_html');
}

// ---- Validate payment link URL ----
if (
  !$json.payment_link ||
  typeof $json.payment_link !== 'object' ||
  typeof $json.payment_link.url !== 'string'
) {
  throw new Error('❌ Final Email Composer: Missing payment_link.url');
}

// ---- Extract values ----
const paymentLinkUrl = $json.payment_link.url;
const currentYear = new Date().getFullYear();

// ---- Inject placeholders ----
let finalEmailHtml = $json.confirmation_email_template;

finalEmailHtml = finalEmailHtml.replace(/__CART_HTML__/g, $json.cart_html);
finalEmailHtml = finalEmailHtml.replace(
  /__PAYMENT_LINK__/g,
  `<a href="${paymentLinkUrl}" style="
    background:#8C2F39;
    color:#ffffff;
    padding:14px 24px;
    border-radius:24px;
    text-decoration:none;
    font-weight:bold;
    display:inline-block;
  ">Complete Payment</a>`
);
finalEmailHtml = finalEmailHtml.replace(/__CURRENT_YEAR__/g, String(currentYear));

// ---- Sanity check ----
const unresolvedTokens = finalEmailHtml.match(/__[^_]+__/g);
if (unresolvedTokens) {
  throw new Error(
    `❌ Final Email Composer: Unresolved placeholders found: ${unresolvedTokens.join(', ')}`
  );
}

// ---- Output ----
return {
  ...$json,
  final_email_html: finalEmailHtml,
};
```

---

## NODE: Email Template
## Type: n8n-nodes-base.code (v2)

```javascript
return {
  ...$json,
  confirmation_email_template: `
<div style="
  font-family: Arial, sans-serif;
  max-width:600px;
  margin:auto;
  background:#FBF6F6;
  padding:24px;
">

  <!-- Logo -->
  <div style="text-align:center;margin-bottom:24px;">
    <a href="https://www.theutopiadeli.com" target="_blank" style="text-decoration:none;">
      <img
        src="https://cdn.shopify.com/s/files/1/0763/5042/3270/files/TheUtopiaDeliLogo_menu.png?v=1774974380"
        alt="The Utopia Deli"
        style="max-width:220px;height:auto;border:none;"
      />
    </a>
  </div>

  <!-- Headline -->
  <p style="
    color:#590B3F;
    font-size:26px;
    font-weight:700;
    line-height:1.35;
    margin:0 0 18px 0;
  ">
    We will begin preparing your order once we receive your payment.
  </p>

  <!-- Slogan -->
  <p style="
    font-style:italic;
    color:#754681;
    font-size:16px;
    margin:0 0 22px 0;
  ">
    The Utopia Deli. It’s just good food.
  </p>

  <!-- Instruction -->
  <p style="
    color:#1F1B1D;
    font-size:14px;
    margin:0 0 20px 0;
  ">
    Please review your order and complete your secure payment below:
  </p>

  <!-- Order Summary -->
  <h3 style="
    color:#590B3F;
    margin-top:32px;
    margin-bottom:12px;
    font-size:18px;
  ">
    Order Summary
  </h3>

  __CART_HTML__

  <hr style="border:none;border-top:1px solid #E6E1E1;margin:24px 0;">

  <!-- CTA -->
  <div style="margin:24px 0;text-align:center;">
    __PAYMENT_LINK__
  </div>

  <!-- Footer -->
  <p style="
    margin-top:12px;
    font-size:12px;
    color:#8A8585;
    text-align:center;
    line-height:1.6;
  ">

    © __CURRENT_YEAR__<br/>

    <a href="https://www.theutopiadeli.com"
       target="_blank"
       style="color:#590B3F;text-decoration:none;font-weight:600;">
      The Utopia Deli
    </a><br/>

    Pickup Order · 801 S Chester St,<br/>
    Little Rock, AR 72202<br/>

    <a href="tel:+15015515944" style="color:#8A8585;text-decoration:none;">
      +1 (501) 551‑5944
    </a>
    &nbsp;·&nbsp;
    <a href="mailto:theutopiadelilittlerock@gmail.com"
       style="color:#8A8585;text-decoration:none;">
      theutopiadelilittlerock@gmail.com
    </a>

  </p>

</div>
`
};
```

---

## NODE: Build Square Line Items With Tax
## Type: n8n-nodes-base.code (v2)

```javascript
const input = $json;

// Ensure existing line items exist
if (!Array.isArray(input.square_line_items)) {
  throw new Error("square_line_items is missing or not an array");
}

// Ensure tax exists
if (!Number.isInteger(input.tax_cents) || input.tax_cents <= 0) {
  throw new Error("tax_cents is missing or invalid");
}

// Clone the existing line items (do not mutate original)
const square_line_items_with_tax = [
  ...input.square_line_items,

  {
    name: "Tax",
    quantity: "1",
    base_price_money: {
      amount: input.tax_cents,
      currency: "USD"
    }
  }
];

return {
  ...input,

  // ✅ new payload for Square
  square_line_items_with_tax
};
```

---

