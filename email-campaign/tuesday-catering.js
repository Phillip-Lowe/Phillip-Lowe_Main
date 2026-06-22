// ═══════════════════════════════════════════════════════════════════════
// TUESDAY — Catering Push (3-Week Rotating Cycle)
// Focus: Drive catering bookings — events, corporate, pickup platters
// ═══════════════════════════════════════════════════════════════════════

const day = $input.first().json.campaign_day;
const baseURL = "https://order.theutopiadeli.com";

// MEAL PREP SCHEDULE (Online Orders Only)
// - Closes: Every Wednesday 12:00 PM
// - Reopens: Every Thursday 8:00 PM
// - Pickup: Thursday 12:30 PM – 7:30 PM
//
// WALK-UP HOURS (Regular Deli)
// - Monday – Saturday: 12:30 PM – 7:30 PM

// ═══════════════════════════════════════════
// SWAP ZONE: Catering Focus (Update per cycle)
// ═══════════════════════════════════════════
// Use weekCycle to rotate between 3 themes automatically
// Week 1 = events, Week 2 = corporate, Week 3 = platters
const weekCycle = ($input.first().json.week_number || 1) % 3; // 0,1,2

const cateringThemes = [
  {
    // Week 1: Events & Parties
    headline: "Planning an Event? Let's Make It Delicious",
    subheadline: "Weddings, birthdays, celebrations — we cater events of all sizes",
    heroImage: "https://order.theutopiadeli.com/images/Deli%20Catering%20Salad.jpg",
    body: "From intimate gatherings to full-scale celebrations, Utopia Deli brings bold, plant-forward flavors that everyone remembers. Our catering team handles the food so you can handle the hosting. Minimum 10 guests, 3 days notice required.",
    ctaText: "Get a Catering Quote",
    ctaLink: `${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=tuesday-events`,
    features: [
      { icon: "🎉", title: "Any Occasion", desc: "Weddings, birthdays, graduations, retirements" },
      { icon: "🍽️", title: "Flexible Service", desc: "Drop-off, staffed buffet, or plated service" },
      { icon: "📋", title: "Custom Menus", desc: "Work with us to build the perfect spread" }
    ],
    socialProof: "\"The Utopia Deli catered our office party and everyone was blown away. Even the meat-eaters went back for seconds.\" — Sarah M.",
    subject: "🎉 Planning an Event? Let's Cater It"
  },
  {
    // Week 2: Corporate / Office
    headline: "Feed Your Team — Corporate Catering Made Easy",
    subheadline: "Office lunches, team meetings, client presentations — we've got you covered",
    heroImage: "https://order.theutopiadeli.com/images/Deli%20Catering%20Fruit%20Salad.jpg",
    body: "Keep your team fueled and focused with fresh, flavorful catering that actually excites people. No sad sandwich platters here — we're talking loaded bowls, crispy sliders, and desserts that disappear first. Set up recurring weekly orders or book one-time events.",
    ctaText: "Book Corporate Catering",
    ctaLink: `${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=tuesday-corporate`,
    features: [
      { icon: "🏢", title: "Office-Friendly", desc: "Easy setup, minimal cleanup, maximum flavor" },
      { icon: "🔄", title: "Recurring Orders", desc: "Weekly team lunch on autopilot" },
      { icon: "💼", title: "Client-Ready", desc: "Impress prospects with premium catering" }
    ],
    socialProof: "\"We order Utopia every Friday for our team lunch. It's the highlight of the week.\" — Marcus T., Tech Lead",
    subject: "🏢 Feed Your Team — Corporate Catering"
  },
  {
    // Week 3: Pickup Platters
    headline: "Pickup Platters — Party Food Without the Work",
    subheadline: "Pre-made platters ready for pickup. Perfect for last-minute gatherings.",
    heroImage: "https://order.theutopiadeli.com/images/menu/cowboy_chicken.webp",
    body: "Need food fast? Our pickup platters are ready to go — no minimum headcount, no lengthy booking process. Just order, grab, and go. Great for game nights, casual get-togethers, or when you just don't feel like cooking.",
    ctaText: "Order Pickup Platters",
    ctaLink: `${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=tuesday-platters`,
    features: [
      { icon: "⚡", title: "Ready Fast", desc: "Order today, pickup tomorrow" },
      { icon: "🍗", title: "Slider Platters", desc: "Buffalo, bourbon, or mixed — 12 or 24 count" },
      { icon: "🥗", title: "Sides & Salads", desc: "Complete the spread with fresh sides" }
    ],
    socialProof: "\"Ordered the slider platter for game night. Gone in 20 minutes. Already ordering for next weekend.\" — James R.",
    subject: "🍽️ Pickup Platters — Easy & Delicious"
  }
];

const theme = cateringThemes[weekCycle];
// ═══════════════════════════════════════════
// END SWAP ZONE
// ═══════════════════════════════════════════

const images = {
  logo: 'https://order.theutopiadeli.com/images/logo.png'
};

const buildHeader = () => `<tr>
<td style="background:#590B3F;padding:20px 24px;">
 <table width="100%" cellpadding="0" cellspacing="0" border="0">
 <tr>
 <td style="vertical-align:middle;">
 <img src="${images.logo}" alt="The Utopia Deli" style="height:56px;display:block;">
 </td>
 <td style="vertical-align:middle;padding-left:16px;">
 <p style="margin:0;color:#fff;font-family:'Georgia','Times New Roman',serif;font-size:24px;font-weight:bold;letter-spacing:0.5px;">
 The Utopia Deli
 </p>
 </td>
 </tr>
 </table>
</td>
</tr>
`;

const buildFooter = () => `<tr>
<td style="padding:20px;background:#f8f6f4;font-family:'Georgia','Times New Roman',serif;text-align:center;border-top:1px solid #e5e5e5;">
<p style="margin:0 0 6px;font-size:13px;color:#888;">
The Utopia Deli · 801 S Chester St · Little Rock, AR 72202
</p>
<p style="margin:0;font-size:12px;">
<a href="https://n8n.systack.net/webhook/unsubscribe?email=%%EMAIL%%&channel=email" style="color:#AF3D4B;text-decoration:underline;">Unsubscribe from emails</a>
</p>
</td>
</tr>
`;

const wrapEmail = (content) => `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
@media only screen and (max-width: 600px) {
 .container { width: 100% !important; }
 .hero-img { height: 280px !important; }
 .feature-grid { display: block !important; }
 .feature-card { width: 100% !important; margin-bottom: 12px !important; }
}
</style>
</head>
<body style="margin:0;padding:0;background:#f8f6f4;font-family:'Georgia','Times New Roman',serif;">
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td align="center" style="padding:24px 12px;">
<table class="container" width="600" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;border-radius:16px;overflow:hidden;max-width:600px;width:100%;">
${buildHeader()}
${content}
${buildFooter()}
</table>
</td></tr>
</table>
</body>
</html>
`;

const buildFeatures = () => {
  return `<tr>
<td style="padding:0 28px 24px;">
<div class="feature-grid" style="display:flex;gap:12px;">
${theme.features.map(f => `
<div class="feature-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;padding:20px;text-align:center;">
<p style="margin:0 0 8px;font-size:28px;">${f.icon}</p>
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">${f.title}</p>
<p style="margin:0;color:#888;font-size:12px;line-height:1.4;">${f.desc}</p>
</div>
`).join('')}
</div>
</td>
</tr>`;
};

const template = {
  email_subject: theme.subject,
  email_body: wrapEmail(`
<tr>
<td>
<img src="${theme.heroImage}" alt="${theme.headline}" class="hero-img" style="width:100%;height:340px;object-fit:cover;display:block;">
</td>
</tr>

<tr>
<td style="padding:32px 28px 20px;">
<p style="margin:0 0 8px;color:#AF3D4B;font-size:14px;font-weight:bold;letter-spacing:0.5px;">CATERING</p>
<h1 style="margin:0 0 12px;color:#590B3F;font-size:28px;line-height:1.2;">${theme.headline}</h1>
<p style="margin:0 0 20px;color:#666;font-size:16px;line-height:1.5;font-style:italic;">${theme.subheadline}</p>
<p style="margin:0 0 24px;color:#333;font-size:16px;line-height:1.6;">${theme.body}</p>
<a href="${theme.ctaLink}"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
${theme.ctaText}
</a>
</td>
</tr>

${buildFeatures()}

<tr>
<td style="padding:0 28px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f6f4;border-left:4px solid #AF3D4B;border-radius:0 12px 12px 0;padding:20px;">
<tr><td>
<p style="margin:0;color:#590B3F;font-size:15px;line-height:1.6;font-style:italic;">${theme.socialProof}</p>
</td></tr>
</table>
</td>
</tr>

<tr>
<td style="padding:0 28px 32px;">
<p style="margin:0 0 8px;color:#888;font-size:13px;">Questions? Call or text us at <a href="tel:5015515944" style="color:#AF3D4B;">(501) 551-5944</a></p>
<p style="margin:0;color:#888;font-size:13px;">Minimum 10 guests · 3 days advance notice for full catering</p>
</td>
</tr>
`)
};

const results = [];
for (const item of $input.all()) {
  const c = item.json;
  if (c.email && !c.unsubscribed_email) {
    results.push({
      json: {
        contact_id: c.id,
        channel: 'email',
        to: c.email,
        subject: template.email_subject,
        body: template.email_body.replace(/%%EMAIL%%/g, encodeURIComponent(c.email)),
        campaign_day: day
      }
    });
  }
}

return results;
