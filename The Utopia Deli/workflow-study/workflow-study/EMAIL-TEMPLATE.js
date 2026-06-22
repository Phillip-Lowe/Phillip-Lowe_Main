/**
 * CONFIRMATION EMAIL TEMPLATE (WKFL 4 Compatible)
 *
 * PURPOSE:
 *   Branded Utopia Deli email template with placeholder tokens.
 *   Identical to WKFL 4 Email Template node.
 *
 * TOKENS:
 *   __CART_HTML__      → cart HTML table
 *   __PAYMENT_LINK__   → styled payment button
 *   __CURRENT_YEAR__   → current year
 *
 * OUTPUT:
 *   { confirmation_email_template: "<html string>" }
 */

return {
  ...$json,
  confirmation_email_template:
    "<div style=\"" +
      "font-family: Arial, sans-serif;" +
      "max-width:600px;" +
      "margin:auto;" +
      "background:#FBF6F6;" +
      "padding:24px;" +
    "\">" +

      "<!-- Logo -->" +
      "<div style=\"text-align:center;margin-bottom:24px;\">" +
        "<a href=\"https://www.theutopiadeli.com\" target=\"_blank\" style=\"text-decoration:none;\">" +
          "<img" +
            " src=\"https://cdn.shopify.com/s/files/1/0763/5042/3270/files/TheUtopiaDeliLogo_menu.png?v=1774974380\"" +
            " alt=\"The Utopia Deli\"" +
            " style=\"max-width:220px;height:auto;border:none;\"" +
          " />" +
        "</a>" +
      "</div>" +

      "<!-- Headline -->" +
      "<p style=\"" +
        "color:#590B3F;" +
        "font-size:26px;" +
        "font-weight:700;" +
        "line-height:1.35;" +
        "margin:0 0 18px 0;" +
      "\">" +
        "We will begin preparing your order once we receive your payment." +
      "</p>" +

      "<!-- Slogan -->" +
      "<p style=\"" +
        "font-style:italic;" +
        "color:#754681;" +
        "font-size:16px;" +
        "margin:0 0 22px 0;" +
      "\">" +
        "The Utopia Deli. It's just good food." +
      "</p>" +

      "<!-- Instruction -->" +
      "<p style=\"" +
        "color:#1F1B1D;" +
        "font-size:14px;" +
        "margin:0 0 20px 0;" +
      "\">" +
        "Please review your order and complete your secure payment below:" +
      "</p>" +

      "<!-- Order Summary -->" +
      "<h3 style=\"" +
        "color:#590B3F;" +
        "margin-top:32px;" +
        "margin-bottom:12px;" +
        "font-size:18px;" +
      "\">" +
        "Order Summary" +
      "</h3>" +

      "__CART_HTML__" +

      "<hr style=\"border:none;border-top:1px solid #E6E1E1;margin:24px 0;\" />" +

      "<!-- CTA -->" +
      "<div style=\"margin:24px 0;text-align:center;\">" +
        "__PAYMENT_LINK__" +
      "</div>" +

      "<!-- Footer -->" +
      "<p style=\"" +
        "margin-top:12px;" +
        "font-size:12px;" +
        "color:#8A8585;" +
        "text-align:center;" +
        "line-height:1.6;" +
      "\">" +
        "© __CURRENT_YEAR__<br/>" +

        "<a href=\"https://www.theutopiadeli.com\"" +
           "target=\"_blank\"" +
           "style=\"color:#590B3F;text-decoration:none;font-weight:600;\">" +
          "The Utopia Deli" +
        "</a><br/>" +

        "Pickup Order · 801 S Chester St,<br/>" +
        "Little Rock, AR 72202<br/>" +

        "<a href=\"tel:+15015515944\" style=\"color:#8A8585;text-decoration:none;\">" +
          "+1 (501) 551‑5944" +
        "</a>" +
      "</p>" +

    "</div>"
};
