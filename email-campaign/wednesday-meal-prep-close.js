// ═══════════════════════════════════════════════════════════════════════
// WEDNESDAY — Meal Prep Deadline (Closes at Noon)
// Focus: Urgency — last chance to order this week's meal prep
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
// SWAP ZONE: Meal Prep Menu (Update Weekly)
// ═══════════════════════════════════════════
const thisWeekMenu = {
  // MEAL PREP SECTION (Top — this week's bowls)
  bowls: [
    { name: "Smokey Taco Bowl", desc: "Black beans, corn, jackfruit, chipotle crema", image: "https://order.theutopiadeli.com/images/mealprep-smokey-taco.jpg" },
    { name: "Chili Garlic Noodles", desc: "Rice noodles, chili crisp, garlic, sesame", image: "https://order.theutopiadeli.com/images/mealprep-chili-noodles.jpg" },
    { name: "Peanut Ginger Bowl", desc: "Crispy peanut tofu, sesame cabbage slaw, sweet chili drizzle", image: "https://order.theutopiadeli.com/images/mealprep-peanut-tofu.jpg" },
    { name: "Mediterranean Harvest", desc: "Quinoa, roasted veg, falafel, tahini", image: "https://order.theutopiadeli.com/catering/images/meal-mediterranean-harvest.jpg" },
    { name: "Thai Peanut Crunch", desc: "Jasmine rice, peanut tofu, sesame slaw", image: "https://order.theutopiadeli.com/catering/images/meal-thai-peanut-crunch.jpg" },
    { name: "Eggplant Parmesan", desc: "Parmesan crusted eggplant, marinara, fresh basil", image: "https://order.theutopiadeli.com/catering/images/meal-eggplant-parm.jpg" }
  ],
  dessert: { name: "Raspberry Dark Chocolate Mousse", desc: "Rich dark chocolate, sugar free — 340 cal", image: "https://order.theutopiadeli.com/catering/images/dessert-raspberry-mousse.jpg" },
  juice: { name: "Cold-Pressed Juice", desc: "Fresh 10oz pineapple, apple, lemon", image: "https://order.theutopiadeli.com/images/cold_pressed_juice_v2.jpg" },
  
  // REGULAR DELI SECTION (Bottom — walk-up items)
  deliHeadline: "Or Walk Up Today 🍽️",
  deliSubheadline: "We're open 12:30 PM – 7:30 PM",
  deliItems: [
    { name: "Stek Philly", desc: "Thin-cut steak, peppers, onions, hoagie roll", image: "https://order.theutopiadeli.com/images/menu/stek%20Philly.jpg", link: `${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=wednesday` },
    { name: "Chick'n Poppers", desc: "Crispy dippers — 5 sauces to choose from", image: "https://order.theutopiadeli.com/images/menu/chicken_poppers_v3.jpg", link: `${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=wednesday` },
    { name: "Loaded Bac'n Fry", desc: "Crinkle-cut fries loaded with bac'n, cheeze sauce", image: "https://order.theutopiadeli.com/images/menu/loaded_bacon_fry.jpg", link: `${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=wednesday` }
  ]
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
 .addon-row { display: block !important; }
 .addon-card { width: 100% !important; margin-bottom: 12px !important; }
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

const buildBowlGrid = () => {
  const cards = thisWeekMenu.bowls.map(bowl => `
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
<h2 style="margin:0 0 16px;color:#590B3F;font-size:20px;">This Week's Bowls</h2>
<div class="bowl-grid" style="display:flex;gap:12px;flex-wrap:wrap;">
${cards}
</div>
</td>
</tr>`;
};

const buildAddons = () => {
  return `<tr>
<td style="padding:0 28px 24px;">
<h3 style="margin:0 0 12px;color:#590B3F;font-size:16px;">Don't Forget Add-Ons</h3>
<div class="addon-row" style="display:flex;gap:12px;">
<div class="addon-card" style="flex:1;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${thisWeekMenu.dessert.image}" style="width:100%;height:100px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">${thisWeekMenu.dessert.name}</p>
<p style="margin:0;color:#888;font-size:12px;">${thisWeekMenu.dessert.desc}</p>
</div>
</div>
<div class="addon-card" style="flex:1;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${thisWeekMenu.juice.image}" style="width:100%;height:100px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">${thisWeekMenu.juice.name}</p>
<p style="margin:0;color:#888;font-size:12px;">${thisWeekMenu.juice.desc}</p>
</div>
</div>
</div>
</td>
</tr>`;
};

const buildDeliSection = () => {
  const cards = thisWeekMenu.deliItems.map(item => `
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
<h2 style="margin:0 0 12px;color:#590B3F;font-size:24px;line-height:1.2;">${thisWeekMenu.deliHeadline}</h2>
<p style="margin:0 0 20px;color:#666;font-size:16px;line-height:1.5;">${thisWeekMenu.deliSubheadline}</p>
<div class="deli-grid" style="display:flex;gap:16px;flex-wrap:wrap;">
${cards}
</div>
</td>
</tr>`;
};

const template = {
  email_subject: "⏰ Closes at Noon Today — Don't Miss This Week's Bowls",
  email_body: wrapEmail(`
<tr>
<td>
<img src="${thisWeekMenu.bowls[0].image}" alt="This Week's Meal Prep" class="hero-img" style="width:100%;height:300px;object-fit:cover;display:block;">
</td>
</tr>

<tr>
<td style="padding:32px 28px 20px;text-align:center;">
<p style="margin:0 0 8px;color:#AF3D4B;font-size:14px;font-weight:bold;letter-spacing:0.5px;">FINAL HOURS</p>
<h1 style="margin:0 0 16px;color:#AF3D4B;font-size:28px;line-height:1.2;">Orders Close Today at 12:00 PM ⏰</h1>
<p style="margin:0 0 20px;color:#333;font-size:16px;line-height:1.6;">
This is your last chance to grab this week's fresh meal prep bowls. We cook Thursday morning, you pick up Thursday afternoon.
</p>
<p style="margin:0 0 24px;color:#333;font-size:15px;">
<strong>Pickup Thursday · 12:30 PM – 7:30 PM</strong>
</p>
<a href="${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=wednesday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Order Before Noon
</a>
</td>
</tr>

${buildBowlGrid()}

${buildAddons()}

${buildDeliSection()}

<tr>
<td style="padding:0 28px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#590B3F;border-radius:12px;padding:20px;">
<tr><td style="text-align:center;">
<p style="margin:0 0 8px;color:#fff;font-size:16px;font-weight:bold;">⏰ Deadline: 12:00 PM Today</p>
<p style="margin:0;color:#fff;font-size:14px;opacity:0.9;">Orders reopen Thursday at 8:00 PM for next week</p>
</td></tr>
</table>
</td>
</tr>

<tr>
<td style="padding:0 28px 32px;">
<p style="margin:0;color:#888;font-size:13px;text-align:center;">
Questions? Call or text <a href="tel:5015515944" style="color:#AF3D4B;">(501) 551-5944</a>
</p>
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
