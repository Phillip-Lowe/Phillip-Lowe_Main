/**
 * FINAL EMAIL COMPOSER (WKFL 4 Compatible)
 *
 * PURPOSE:
 *   Injects cart_html and payment_link into branded email template.
 *   Identical logic to WKFL 4 FINAL EMAIL COMPOSER.
 *
 * INPUT:
 *   {
 *     confirmation_email_template: "<html>...__CART_HTML__...__PAYMENT_LINK__...",
 *     cart_html: "<table>...",
 *     payment_link: { url: "..." },
 *     total_cents: N
 *   }
 *
 * OUTPUT:
 *   { final_email_html: "<complete branded email>" }
 */

const input = $json;

// ---- Validate template ----
if (
  !input.confirmation_email_template ||
  typeof input.confirmation_email_template !== "string"
) {
  throw new Error("Missing confirmation_email_template");
}

// ---- Validate cart HTML ----
if (
  !input.cart_html ||
  typeof input.cart_html !== "string"
) {
  throw new Error("Missing cart_html");
}

// ---- Validate payment link URL ----
if (
  !input.payment_link ||
  typeof input.payment_link !== "object" ||
  typeof input.payment_link.url !== "string"
) {
  throw new Error("Missing payment_link.url");
}

// ---- Extract values ----
const paymentLinkUrl = input.payment_link.url;
const currentYear = new Date().getFullYear();

// ---- Inject placeholders ----
let finalEmailHtml = input.confirmation_email_template;

finalEmailHtml = finalEmailHtml.replace(/__CART_HTML__/g, input.cart_html);
finalEmailHtml = finalEmailHtml.replace(
  /__PAYMENT_LINK__/g,
  "<a href=\"" + paymentLinkUrl + "\" style=\"" +
    "background:#8C2F39;" +
    "color:#ffffff;" +
    "padding:14px 24px;" +
    "border-radius:24px;" +
    "text-decoration:none;" +
    "font-weight:bold;" +
    "display:inline-block;" +
  "\">Complete Payment</a>"
);
finalEmailHtml = finalEmailHtml.replace(/__CURRENT_YEAR__/g, String(currentYear));

// ---- Sanity check ----
const unresolvedTokens = finalEmailHtml.match(/__[^_]+__/g);
if (unresolvedTokens) {
  throw new Error(
    "Unresolved placeholders found: " + unresolvedTokens.join(", ")
  );
}

// ---- Output ----
return {
  ...input,
  final_email_html: finalEmailHtml
};
