// ═══════════════════════════════════════════════════════════════════════
// FRIDAY — Weekend Kickoff
// Focus: Weekend energy, walk-ups, atmosphere, lifestyle
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
// SWAP ZONE: Weekend Content (Update Weekly)
// ═══════════════════════════════════════════
const weekendContent = {
  // Hero: lifestyle/vibe image
  heroImage: "https://order.theutopiadeli.com/images/Deli%20Happy%20customer%20lady.jpg",
  // Weekend headline (rotate themes)
  headline: "Weekend at Utopia 🍽️",
  subheadline: "Monday – Saturday · 12:30PM–7:30PM · Walk-ups welcome",
  // Body copy (fun, casual, vibe-forward)
  body: "It's finally here. The weekend. And we've got the food to match the mood. Walk up, order fresh, eat happy. No reservations needed — just bring your appetite.",
  // Featured weekend items
  features: [
    {
      name: "Stek Philly",
      desc: "Thin-cut steak, peppers, onions, hoagie roll",
      image: "https://order.theutopiadeli.com/images/menu/stek%20Philly.jpg",
      tag: "BESTSELLER"
    },
    {
      name: "Chick'n Poppers",
      desc: "Crispy dippers — 5 sauces to choose from",
      image: "https://order.theutopiadeli.com/images/menu/chicken_poppers_v3.jpg",
      tag: "SHAREABLE"
    },
    {
      name: "Loaded Bac'n Fry",
      desc: "Crinkle-cut fries loaded with bac'n, cheeze sauce",
      image: "https://order.theutopiadeli.com/images/menu/loaded_bacon_fry.jpg",
      tag: "CLASSIC"
    },
    {
      name: "Chocolate Chip Cookies",
      desc: "Two fresh-baked cookies, warm from the oven",
      image: "https://order.theutopiadeli.com/images/menu/cookies_v2.jpg",
      tag: "SWEET"
    }
  ],
  // Weekend-only special (optional, leave null if none)
  weekendSpecial: {
    text: "Weekend Combo: Any sandwich + side + drink for $18",
    active: false // Set to true when running a promo
  },
  // CTA
  ctaText: "Order Ahead — Skip the Line",
  ctaLink: `${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=friday`
};
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
 .hero-bg { height: 300px !important; }
 .feature-grid { display: block !important; }
 .feature-card { width: 100% !important; margin-bottom: 16px !important; }
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
  const cards = weekendContent.features.map(item => `
<div class="feature-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<div style="position:relative;">
<img src="${item.image}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="position:absolute;top:8px;left:8px;background:#AF3D4B;color:#fff;padding:4px 10px;border-radius:6px;font-size:11px;font-weight:bold;">${item.tag}</div>
</div>
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">${item.name}</p>
<p style="margin:0;color:#888;font-size:12px;">${item.desc}</p>
</div>
</div>
`).join('');

  return `<tr>
<td style="padding:0 28px 24px;">
<h2 style="margin:0 0 16px;color:#590B3F;font-size:20px;">Weekend Favorites</h2>
<div class="feature-grid" style="display:flex;gap:16px;flex-wrap:wrap;">
${cards}
</div>
</td>
</tr>`;
};

const template = {
  email_subject: `${weekendContent.headline} Fresh Food, Good Vibes`,
  email_body: wrapEmail(`
<tr>
<td
 height="320"
 style="
 background-image:url(${weekendContent.heroImage});
 background-size:cover;
 background-position:center 30%;
 background-repeat:no-repeat;
 "
 class="hero-bg"
>
 &nbsp;
</td>
</tr>

<tr>
<td style="padding:32px 28px 20px;">
<h1 style="margin:0 0 12px;color:#590B3F;font-size:28px;line-height:1.2;">${weekendContent.headline}</h1>
<p style="margin:0 0 20px;color:#333;font-size:16px;line-height:1.6;">${weekendContent.body}</p>
<p style="margin:0 0 24px;color:#AF3D4B;font-size:15px;font-weight:bold;">${weekendContent.subheadline}</p>
${weekendContent.weekendSpecial.active ? `<div style="background:#FFD700;border-radius:10px;padding:16px;margin:0 0 24px;text-align:center;">
<p style="margin:0;color:#590B3F;font-size:16px;font-weight:bold;">⚡ WEEKEND SPECIAL ⚡</p>
<p style="margin:4px 0 0;color:#590B3F;font-size:15px;">${weekendContent.weekendSpecial.text}</p>
</div>` : ''}
<div style="text-align:center;">
<a href="${weekendContent.ctaLink}"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;margin-right:8px;">
${weekendContent.ctaText}
</a>
<a href="${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=friday"
style="display:inline-block;background:transparent;color:#AF3D4B;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;border:2px solid #AF3D4B;">
Order Meal Prep
</a>
</div>
</td>
</tr>

${buildFeatures()}

<tr>
<td style="padding:0 28px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#590B3F;border-radius:12px;padding:20px;">
<tr><td style="text-align:center;">
<p style="margin:0 0 4px;color:#fff;font-size:16px;font-weight:bold;">The Utopia Deli</p>
<p style="margin:0 0 4px;color:#fff;font-size:14px;">801 S Chester St, Little Rock, AR 72202</p>
<p style="margin:0;color:#fff;font-size:13px;opacity:0.8;">Monday – Saturday · 12:30PM–7:30PM</p>
</td></tr>
</table>
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
