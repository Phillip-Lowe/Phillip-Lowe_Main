/**
 * PAYMENT CONFIRMED EMAIL TEMPLATE
 *
 * PURPOSE:
 *   Branded confirmation email sent AFTER payment is completed.
 *   Used by Disable Payment Link workflow.
 *
 * TOKENS:
 *   __CART_HTML__     → cart HTML table
 *   __ORDER_TOTAL__   → formatted total (e.g., "$12.04")
 *   __PICKUP_WINDOW__ → estimated pickup time
 *   __BUSINESS_PHONE__ → formatted phone
 *   __BUSINESS_PHONE_RAW__ → digits-only phone for tel: link
 *   __BUSINESS_EMAIL__ → contact email
 *   __CURRENT_YEAR__  → current year
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

      "<!-- Confirmation Headline -->" +
      "<p style=\"" +
        "color:#590B3F;" +
        "font-size:26px;" +
        "font-weight:700;" +
        "line-height:1.35;" +
        "margin:0 0 18px 0;" +
      "\">" +
        "Thank you for your order — we've received your payment." +
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

      "<!-- Confirmation Body -->" +
      "<p style=\"" +
        "color:#1F1B1D;" +
        "font-size:14px;" +
        "margin:0 0 20px 0;" +
      "\">" +
        "Your payment was successful and your order is now being prepared in our kitchen. " +
        "We'll see you soon!" +
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

      "<!-- Footer -->" +
      "<p style=\"" +
        "margin-top:12px;" +
        "font-size:12px;" +
        "color:#8A8585;" +
        "text-align:center;" +
        "line-height:1.6;" +
      "\">" +
        "<strong>Estimated pickup: __PICKUP_WINDOW__</strong><br/><br/>" +

        "Questions? Call us at " +
        "<a href=\"tel:__BUSINESS_PHONE_RAW__\" style=\"color:#590B3F;text-decoration:none;font-weight:600;\">" +
          "__BUSINESS_PHONE__" +
        "</a>" +
        " or email " +
        "<a href=\"mailto:__BUSINESS_EMAIL__\" style=\"color:#590B3F;text-decoration:none;font-weight:600;\">" +
          "__BUSINESS_EMAIL__" +
        "</a>" +
        "<br/><br/>" +

        "© __CURRENT_YEAR__<br/>" +

        "<a href=\"https://www.theutopiadeli.com\"" +
           "target=\"_blank\"" +
           "style=\"color:#590B3F;text-decoration:none;font-weight:600;\">" +
          "The Utopia Deli" +
        "</a><br/>" +

        "801 S Chester St, Little Rock, AR 72202" +
      "</p>" +

    "</div>"
};
