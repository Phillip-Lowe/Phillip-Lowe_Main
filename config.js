// ===================== BRAND CONFIGURATION =====================
// Edit this file to rebrand the order page for any business.
// All brand-specific values are isolated here.
// ==============================================================

const BRAND = {
  // Identity
  name:          "The Utopia Deli",
  tagline:       "Plant-based. Little Rock made.",
  shortName:     "Utopia Deli",
  location:      "Little Rock, AR",

  // Contact
  phone:         "(501) 555-0199",     // Replace with real number
  email:         "order@theutopiadeli.com",
  instagram:     "@theutopiadeli",

  // Visual Identity — CSS variable overrides
  colors: {
    primary:       "#590B3F",   // Deep plum
    primaryLight:  "#7a1a55",   // Lighter plum
    accent:        "#AF3D4B",   // Rose / CTA
    accentHover:   "#c44d5b",
    secondary:     "#754681",   // Muted purple
    gold:          "#D59F5C",   // Gold highlight
    goldLight:     "#f5e6d0",
  },

  // Assets
  logo:          "images/logo.png",
  favicon:       "images/logo.png",
  heroImage:     null,            // Optional hero background

  // Hours (CST/Chicago)
  hours: {
    timezone:    "America/Chicago",
    openDays:    [1,2,3,4,5,6],   // Mon-Sat (0=Sun, 6=Sat)
    openTime:    { hour: 12, minute: 30 },
    closeTime:   { hour: 19, minute: 30 },
    closedMessage: "Currently Closed · Opens Mon–Sat 12:30 PM",
    openMessage:   "Open Now · Mon–Sat 12:30 PM – 7:30 PM",
  },

  // Checkout / Payment
  checkout: {
    // Where the order is sent after customer fills the form
    // Set to your checkout server or n8n webhook URL
    endpoint:    "https://order-utopia-deli.systack.net/checkout",

    // Square payment link domain (for display / CTA buttons)
    squareDomain: "square.link",

    // Currency
    currency:    "USD",
    currencySymbol: "$",
  },

  // Legal
  copyrightYear: 2026,
};

// ==============================================================
//  WHITE-LABEL CHECKLIST
// ==============================================================
//  1. Replace BRAND.name, .tagline, .location
//  2. Update BRAND.phone and BRAND.email
//  3. Replace logo.png in images/ folder
//  4. Replace product photos in images/ folder
//  5. Update menu-data.js with your menu items
//  6. Update BRAND.checkout.endpoint to your server/webhook
//  7. Update BRAND.hours to your schedule
//  8. Update CNAME file to your custom domain
//  9. Update DNS CNAME record at your registrar
// ==============================================================
