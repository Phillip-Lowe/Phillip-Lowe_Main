// ═══════════════════════════════════════════════════════════════════════
// MONDAY — Item of the Week
// Focus: Spotlight one dish/menu item to drive interest
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
// SWAP ZONE: Item of the Week (Update Weekly)
// ═══════════════════════════════════════════
const itemOfTheWeek = {
  // MEAL PREP SECTION (Top — the weekly bowls)
  heroImage: "https://order.theutopiadeli.com/catering/images/meal-mediterranean-harvest.jpg",
  mealPrepHeadline: "This Week's Meal Prep is Open 🍱",
  mealPrepSubheadline: "Fresh, chef-crafted bowls ready for pickup Thursday",
  mealPrepBody: "Our Mediterranean Harvest Bowl leads this week's lineup — crispy oregano chickpeas, lemon herb quinoa, cucumber tomato salad, housemade hummus, tahini drizzle, and pickled red onion. Order by Wednesday noon.",
  promoLine: "⏰ Orders close Wednesday 12:00 PM · Pickup Thursday 12:30–7:30 PM",
  ctaText: "Order Meal Prep",
  ctaLink: `${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=monday`,
  
  // This week's bowls (update weekly)
  thisWeekBowls: [
    { name: "Mediterranean Harvest", desc: "Quinoa, crispy chickpeas, cucumber salad, hummus, tahini", image: "https://order.theutopiadeli.com/catering/images/meal-mediterranean-harvest.jpg" },
    { name: "Thai Peanut Crunch", desc: "Jasmine rice, peanut tofu, sesame slaw, sweet chili drizzle", image: "https://order.theutopiadeli.com/catering/images/meal-thai-peanut-crunch.jpg" },
    { name: "Eggplant Parmesan", desc: "Parmesan crusted eggplant, marinara, fresh basil", image: "https://order.theutopiadeli.com/catering/images/meal-eggplant-parm.jpg" },
    { name: "Street Corn Taco", desc: "Cilantro lime rice, chipotle lentil crumble, roasted corn", image: "https://order.theutopiadeli.com/catering/images/meal-buffalo-chickpea.jpg" },
    { name: "Nashville Hot Lentil", desc: "Garlic rice, hot lentils, roasted broccoli, ranch drizzle", image: "https://order.theutopiadeli.com/catering/images/meal-cajun-northern-beans.jpg" },
    { name: "Cajun Red Beans & Rice", desc: "Dirty rice, Cajun beans, peppers & onions", image: "https://order.theutopiadeli.com/catering/images/meal-cajun-northern-beans.jpg" }
  ],
  
  // REGULAR DELI SECTION (Bottom — walk-up items)
  deliHeadline: "Or Walk Up Anytime 🍽️",
  deliSubheadline: "Monday – Saturday · 12:30 PM – 7:30 PM",
  deliItems: [
    { name: "Stek Philly", desc: "Thin-cut steak, peppers, onions, hoagie roll", image: "https://order.theutopiadeli.com/images/menu/stek%20Philly.jpg", link: `${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=monday` },
    { name: "Chick'n Poppers", desc: "Crispy dippers — BBQ, Garlic Parm, Jerk, Buffalo, Lemon Pepper", image: "https://order.theutopiadeli.com/images/menu/chicken_poppers_v3.jpg", link: `${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=monday` },
    { name: "Loaded Bac'n Fry", desc: "Crinkle-cut fries loaded with bac'n, cheeze sauce", image: "https://order.theutopiadeli.com/images/menu/loaded_bacon_fry.jpg", link: `${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=monday` },
    { name: "Chocolate Chip Cookies", desc: "Two fresh-baked cookies, warm from the oven", image: "https://order.theutopiadeli.com/images/menu/cookies_v2.jpg", link: `${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=monday` }
  ],
  
  footerPromo: {
    text: "Walk up Monday–Saturday 12:30–7:30PM · Meal prep closes Wed noon",
    link: `${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=monday`
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
 .thumb-grid { display: block !important; }
 .thumb-card { width: 100% !important; margin-bottom: 12px !important; }
 .also-grid { display: block !important; }
 .also-card { width: 100% !important; margin-bottom: 16px !important; }
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

// Build meal prep bowl grid
const buildMealPrepBowls = () => {
  const cards = itemOfTheWeek.thisWeekBowls.map(bowl => `
<div class="bowl-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${bowl.image}" style="width:100%;height:120px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">${bowl.name}</p>
<p style="margin:0;color:#888;font-size:12px;">${bowl.desc}</p>
</div>
</div>
`).join('');

  return `<tr>
<td style="padding:0 28px 16px;">
<div class="bowl-grid" style="display:flex;gap:12px;flex-wrap:wrap;">
${cards}
</div>
</td>
</tr>`;
};

// Build regular deli section
const buildDeliSection = () => {
  const cards = itemOfTheWeek.deliItems.map(item => `
<div class="deli-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<a href="${item.link}" style="text-decoration:none;color:inherit;">
<img src="${item.image}" style="width:100%;height:130px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">${item.name}</p>
<p style="margin:0;color:#888;font-size:12px;">${item.desc}</p>
</div>
</a>
</div>
`).join('');

  return `<tr>
<td style="padding:0 28px 24px;">
<div style="border-top:2px dashed #e5e5e5;padding-top:24px;margin-bottom:24px;"></div>
<p style="margin:0 0 8px;color:#AF3D4B;font-size:14px;font-weight:bold;letter-spacing:0.5px;">REGULAR DELI</p>
<h2 style="margin:0 0 12px;color:#590B3F;font-size:24px;line-height:1.2;">${itemOfTheWeek.deliHeadline}</h2>
<p style="margin:0 0 20px;color:#666;font-size:16px;line-height:1.5;">${itemOfTheWeek.deliSubheadline}</p>
<div class="deli-grid" style="display:flex;gap:16px;flex-wrap:wrap;">
${cards}
</div>
</td>
</tr>`;
};

const template = {
  email_subject: `✨ This Week: ${itemOfTheWeek.mealPrepHeadline.replace("🍱 ", "")}`,
  email_body: wrapEmail(`
<tr>
<td>
<img src="${itemOfTheWeek.heroImage}" alt="${itemOfTheWeek.mealPrepHeadline}" class="hero-img" style="width:100%;height:340px;object-fit:cover;display:block;">
</td>
</tr>

<tr>
<td style="padding:32px 28px 20px;">
<p style="margin:0 0 8px;color:#AF3D4B;font-size:14px;font-weight:bold;letter-spacing:0.5px;">MEAL PREP</p>
<h1 style="margin:0 0 12px;color:#590B3F;font-size:28px;line-height:1.2;">${itemOfTheWeek.mealPrepHeadline}</h1>
<p style="margin:0 0 20px;color:#666;font-size:16px;line-height:1.5;">${itemOfTheWeek.mealPrepSubheadline}</p>
<p style="margin:0 0 24px;color:#333;font-size:16px;line-height:1.6;">${itemOfTheWeek.mealPrepBody}</p>
<p style="margin:0 0 24px;color:#AF3D4B;font-size:15px;font-weight:bold;">${itemOfTheWeek.promoLine}</p>
<a href="${itemOfTheWeek.ctaLink}"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
${itemOfTheWeek.ctaText}
</a>
</td>
</tr>

${buildMealPrepBowls()}

${buildDeliSection()}

<tr>
<td style="padding:0 28px 32px;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#590B3F;border-radius:12px;padding:20px;">
<tr><td style="text-align:center;">
<p style="margin:0 0 4px;color:#fff;font-size:16px;font-weight:bold;">The Utopia Deli</p>
<p style="margin:0 0 4px;color:#fff;font-size:14px;">801 S Chester St, Little Rock, AR 72202</p>
<p style="margin:0;color:#fff;font-size:13px;opacity:0.8;">Walk up Monday–Saturday · 12:30PM–7:30PM · Meal prep: closes Wed noon, pickup Thu</p>
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
