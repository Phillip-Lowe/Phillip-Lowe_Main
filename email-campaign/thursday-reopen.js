// ═══════════════════════════════════════════════════════════════════════
// THURSDAY — Meal Prep Reopens + Regular Deli
// Focus: "We're back!" — meal prep orders open + daily menu highlights
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
// SWAP ZONE: Thursday Content (Update Weekly)
// ═══════════════════════════════════════════
const thursdayContent = {
  // Next week's bowl lineup (the one now open for ordering)
  nextWeekBowls: [
    { name: "Street Corn Taco", desc: "Cilantro lime rice, chipotle lentil crumble, roasted corn, pickled onions", image: "https://order.theutopiadeli.com/catering/images/meal-buffalo-chickpea.jpg" },
    { name: "Nashville Hot Lentil", desc: "Garlic rice, hot lentils, roasted broccoli, ranch drizzle", image: "https://order.theutopiadeli.com/catering/images/meal-cajun-northern-beans.jpg" },
    { name: "Mediterranean Harvest", desc: "Lemon herb quinoa, crispy chickpeas, cucumber salad, hummus", image: "https://order.theutopiadeli.com/catering/images/meal-mediterranean-harvest.jpg" }
  ],
  // Thursday daily specials (walk-up items, changes daily)
  dailySpecials: [
    { name: "Stek Philly", desc: "Thin-cut steak, peppers, onions, hoagie roll", image: "https://order.theutopiadeli.com/images/menu/stek%20Philly.jpg" },
    { name: "Loaded Bac'n Fry", desc: "Crinkle-cut fries loaded with bac'n, cheeze sauce", image: "https://order.theutopiadeli.com/images/menu/loaded_bacon_fry.jpg" },
    { name: "Chick'n Poppers", desc: "Crispy dippers — BBQ, Garlic Parm, Jerk, Buffalo", image: "https://order.theutopiadeli.com/images/menu/chicken_poppers_v3.jpg" }
  ],
  // Optional: Thursday-only promo
  promo: {
    text: "Walk up today · Open 12:30 PM – 7:30 PM",
    link: `${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=thursday`
  }
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
 .hero-img { height: 280px !important; }
 .bowl-grid { display: block !important; }
 .bowl-card { width: 100% !important; margin-bottom: 12px !important; }
 .daily-grid { display: block !important; }
 .daily-card { width: 100% !important; margin-bottom: 12px !important; }
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

const buildBowlPreview = () => {
  const cards = thursdayContent.nextWeekBowls.map(bowl => `
<div class="bowl-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${bowl.image}" style="width:100%;height:120px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">${bowl.name}</p>
<p style="margin:0;color:#888;font-size:12px;">${bowl.desc}</p>
</div>
</div>
`).join('');

  return `<tr>
<td style="padding:0 28px 20px;">
<h2 style="margin:0 0 16px;color:#590B3F;font-size:20px;">Next Week's Bowls (Now Open)</h2>
<div class="bowl-grid" style="display:flex;gap:12px;flex-wrap:wrap;">
${cards}
</div>
<p style="margin:12px 0 0;color:#888;font-size:13px;">Plus 3 more bowls + dessert + juice add-ons</p>
</td>
</tr>`;
};

const buildDailySpecials = () => {
  const cards = thursdayContent.dailySpecials.map(item => `
<div class="daily-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${item.image}" style="width:100%;height:120px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">${item.name}</p>
<p style="margin:0;color:#888;font-size:12px;">${item.desc}</p>
</div>
</div>
`).join('');

  return `<tr>
<td style="padding:0 28px 24px;">
<h2 style="margin:0 0 16px;color:#590B3F;font-size:20px;">Walk Up Today — We're Open</h2>
<div class="daily-grid" style="display:flex;gap:12px;flex-wrap:wrap;">
${cards}
</div>
</td>
</tr>`;
};

const template = {
  email_subject: "🍱 We're Back! Meal Prep Orders Now Open + Walk-Up Menu",
  email_body: wrapEmail(`
<!-- MEAL PREP SECTION -->
<tr>
<td style="background:linear-gradient(135deg,#590B3F 0%,#8B1A4E 100%);padding:40px 28px;text-align:center;">
<p style="margin:0 0 8px;color:#FFD700;font-size:14px;font-weight:bold;letter-spacing:1px;">✨ MEAL PREP NOW OPEN ✨</p>
<h1 style="margin:0 0 12px;color:#fff;font-size:28px;line-height:1.2;">Next Week's Bowls Are Live!</h1>
<p style="margin:0;color:#fff;opacity:0.9;font-size:16px;line-height:1.5;">Order now for pickup next Thursday.</p>
<p style="margin:16px 0 0;color:#FFD700;font-size:15px;font-weight:bold;">Closes Wednesday at 12:00 PM · Reopens Thursday 8:00 PM</p>
</td>
</tr>

${buildBowlPreview()}

<tr>
<td style="padding:0 28px 24px;text-align:center;">
<a href="${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=thursday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Order Meal Prep →
</a>
</td>
</tr>

<!-- REGULAR DELI SECTION -->
<tr>
<td style="padding:0 28px;">
<div style="border-top:2px dashed #e5e5e5;"></div>
<p style="margin:24px 0 8px;color:#AF3D4B;font-size:14px;font-weight:bold;letter-spacing:0.5px;">REGULAR DELI</p>
<h2 style="margin:0 0 16px;color:#590B3F;font-size:24px;">Walk Up Today 🍽️</h2>
<p style="margin:0 0 20px;color:#666;font-size:16px;">We're open 12:30 PM – 7:30 PM. Come grab lunch or dinner.</p>
</td>
</tr>

${buildDailySpecials()}

<tr>
<td style="padding:0 28px 32px;text-align:center;">
<a href="${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=thursday"
style="display:inline-block;background:transparent;color:#AF3D4B;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;border:2px solid #AF3D4B;">
Full Walk-Up Menu →
</a>
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
