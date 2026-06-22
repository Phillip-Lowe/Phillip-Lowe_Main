/**
 * CART_HTML BUILDER (WKFL 4 Compatible)
 *
 * PURPOSE:
 *   Renders cart_items into branded HTML table.
 *   Identical logic to WKFL 4 cart_html BUILDER.
 *   Can be used by both deli system AND html system.
 *
 * INPUT:
 *   { cart_items: [...], subtotal_cents: N, tax_cents: N, total_cents: N }
 *   OR
 *   { cart_items_json: "string", subtotal_cents: N, tax_cents: N, total_cents: N }
 *
 * OUTPUT:
 *   { cart_html: "<HTML table>" }
 */

const input = $json;

// ─────────────────────────────────────────────
// 1. Resolve cart_items safely
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
// 2. Helpers
// ─────────────────────────────────────────────
const money = cents =>
  "$" + (Number(cents || 0) / 100).toFixed(2);

// ✅ TAKE‑OFF detector (semantic convention)
const isTakeOff = mod =>
  typeof mod?.mod_name === "string" &&
  /^(no\s|no-|hold\s|hold-)/i.test(mod.mod_name.trim());

// ✅ Note sanitizer
const sanitizeText = txt =>
  String(txt).replace(/[<>]/g, "");

// Brand tokens
const BRAND_MUTED = "#555";
const BRAND_SUBTLE = "#777";

// ─────────────────────────────────────────────
// 3. Build cart rows
// ─────────────────────────────────────────────
let rows = "";

cart_items.forEach(function(item, idx) {
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
    rows += "<tr><td colspan=\"2\" style=\"padding-top:14px;\"></td></tr>";
  }

  // ── ITEM HEADER ────────────────────────────
  rows += "<tr>" +
    "<td><strong>" + (qty > 1 ? qty + " × " : "") + item.display_name + "</strong></td>" +
    "<td style=\"text-align:right;\"><strong>" + money(baseDisplayCents) + "</strong></td>" +
    "</tr>";

  // ── IDENTIFIERS ────────────────────────────
  identifiers.forEach(m => {
    rows += "<tr>" +
      "<td style=\"padding-left:24px; font-style:italic;\">" + m.mod_name + "</td>" +
      "<td></td>" +
      "</tr>";
  });

  // ── TAKE OFF ───────────────────────────────
  if (takeoffs.length > 0) {
    rows += "<tr><td colspan=\"2\" style=\"padding-left:24px; font-size:11px; font-weight:600; color:" + BRAND_MUTED + "; padding-top:4px;\">TAKE OFF</td></tr>";
  }
  takeoffs.forEach(m => {
    rows += "<tr>" +
      "<td style=\"padding-left:24px; font-style:italic; color:" + BRAND_MUTED + ";\">" + m.mod_name + "</td>" +
      "<td></td>" +
      "</tr>";
  });

  // ── ADD‑ONS ────────────────────────────────
  if (addons.length > 0) {
    rows += "<tr><td colspan=\"2\" style=\"padding-left:24px; font-size:11px; font-weight:600; color:" + BRAND_MUTED + "; padding-top:6px;\">ADD‑ONS</td></tr>";
  }
  addons.forEach(m => {
    rows += "<tr>" +
      "<td style=\"padding-left:24px;\">+ " + m.mod_name + "</td>" +
      "<td style=\"text-align:right;\">" + money(Number(m.price_delta) * 100) + "</td>" +
      "</tr>";
  });

  // ── ITEM‑SCOPED NOTES ──────────────────────
  if (item.notes && String(item.notes).trim()) {
    const safeNote = sanitizeText(item.notes);
    rows += "<tr><td colspan=\"2\" style=\"padding-left:24px; font-style:italic; color:" + BRAND_MUTED + "; padding-top:6px;\">Notes: " + safeNote + "</td></tr>";
  }

  // ── ITEM TOTAL ─────────────────────────────
  if (addons.length > 0 && item.line_total_cents) {
    rows += "<tr>" +
      "<td style=\"padding-left:24px; font-weight:600;\">Item total</td>" +
      "<td style=\"text-align:right; font-weight:600;\">" + money(item.line_total_cents) + "</td>" +
      "</tr>";
  }
});

// ─────────────────────────────────────────────
// 4. Final cart HTML
// ─────────────────────────────────────────────
const cart_html = "<table width=\"100%\" cellpadding=\"0\" cellspacing=\"0\">" +
  rows +
  "<tr><td colspan=\"2\"><hr></td></tr>" +
  "<tr><td><strong>Subtotal</strong></td><td style=\"text-align:right;\"><strong>" + money(input.subtotal_cents) + "</strong></td></tr>" +
  "<tr><td>Tax</td><td style=\"text-align:right;\">" + money(input.tax_cents) + "</td></tr>" +
  "<tr><td style=\"padding-top:10px;\"><strong>Total</strong></td><td style=\"padding-top:10px; text-align:right;\"><strong>" + money(input.total_cents) + "</strong></td></tr>" +
  "</table>";

// ─────────────────────────────────────────────
// 5. Output
// ─────────────────────────────────────────────
return {
  ...input,
  cart_html: cart_html
};
