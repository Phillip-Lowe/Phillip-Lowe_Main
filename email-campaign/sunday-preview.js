// ═══════════════════════════════════════════════════════════════════════
// SUNDAY — This Week Preview
// Focus: Next week's meal prep menu + Monday lunch tease + weekly preview
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
// SWAP ZONE: Sunday Preview (Update Weekly)
// ═══════════════════════════════════════════
const sundayContent = {
  // Next week's meal prep menu (all 6+ bowls)
  nextWeekMenu: [
    {
      name: "Street Corn Taco Bowl",
      desc: "Cilantro lime rice, chipotle lentil crumble, roasted corn, pickled onions, chipotle crema",
      image: "https://order.theutopiadeli.com/catering/images/meal-buffalo-chickpea.jpg"
    },
    {
      name: "Nashville Hot Lentil Bowl",
      desc: "Garlic rice, Nashville hot lentils, roasted broccoli, ranch drizzle",
      image: "https://order.theutopiadeli.com/catering/images/meal-cajun-northern-beans.jpg"
    },
    {
      name: "Mediterranean Harvest Bowl",
      desc: "Lemon herb quinoa, crispy oregano chickpeas, cucumber tomato salad, hummus, tahini drizzle",
      image: "https://order.theutopiadeli.com/catering/images/meal-mediterranean-harvest.jpg"
    },
    {
      name: "Thai Peanut Crunch Bowl",
      desc: "Jasmine rice, crispy peanut tofu, sesame cabbage slaw, sweet chili peanut drizzle",
      image: "https://order.theutopiadeli.com/catering/images/meal-thai-peanut-crunch.jpg"
    },
    {
      name: "Cajun Red Beans & Rice",
      desc: "Dirty rice, Cajun beans, peppers & onions, green onion garnish",
      image: "https://order.theutopiadeli.com/catering/images/meal-cajun-northern-beans.jpg"
    },
    {
      name: "Eggplant Parmesan",
      desc: "Parmesan crusted eggplant, homemade marinara, fresh basil",
      image: "https://order.theutopiadeli.com/catering/images/meal-eggplant-parm.jpg"
    }
  ],
  // Dessert + Drink add-ons
  addOns: [
    { name: "Raspberry Dark Chocolate Mousse", image: "https://order.theutopiadeli.com/catering/images/dessert-raspberry-mousse.jpg" },
    { name: "Mango Chia Pudding", image: "https://order.theutopiadeli.com/catering/images/dessert-mango-chia.jpg" },
    { name: "Cold-Pressed Juice", image: "https://order.theutopiadeli.com/images/cold_pressed_juice_v2.jpg" }
  ],
  // Monday lunch tease (2-3 items to drive Monday walk-ups)
  mondayLunch: [
    {
      name: "Stek Philly",
      desc: "The sandwich that built our reputation",
      image: "https://order.theutopiadeli.com/images/menu/stek%20Philly.jpg",
      link: `${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=sunday`
    },
    {
      name: "Chick'n Poppers",
      desc: "5 sauces, unlimited flavor",
      image: "https://order.theutopiadeli.com/images/menu/chicken_poppers_v3.jpg",
      link: `${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=sunday`
    }
  ],
  // "What's happening this week" — optional special events, new items, etc.
  thisWeek: {
    hasContent: false, // Set to true when there's something to announce
    title: "This Week at Utopia",
    items: [
      // { day: "Tuesday", text: "New dessert drop: Peach Cobbler" },
      // { day: "Friday", text: "Live music 6-8PM" }
    ]
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
 .menu-grid { display: block !important; }
 .menu-card { width: 100% !important; margin-bottom: 12px !important; }
 .lunch-grid { display: block !important; }
 .lunch-card { width: 100% !important; margin-bottom: 16px !important; }
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

const buildMenuGrid = () => {
  const cards = sundayContent.nextWeekMenu.map(bowl => `
<div class="menu-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${bowl.image}" style="width:100%;height:110px;object-fit:cover;display:block;">
<div style="padding:10px;">
<p style="margin:0 0 2px;color:#590B3F;font-weight:bold;font-size:13px;">${bowl.name}</p>
<p style="margin:0;color:#888;font-size:11px;line-height:1.3;">${bowl.desc.substring(0, 50)}...${bowl.desc.length > 50 ? '...' : ''}</p>
</div>
</div>
`).join('');

  return `<tr>
<td style="padding:0 28px 16px;">
<h2 style="margin:0 0 16px;color:#590B3F;font-size:20px;">🍱 This Week's Meal Prep Menu</h2>
<div class="menu-grid" style="display:flex;gap:10px;flex-wrap:wrap;">
${cards}
</div>
</td>
</tr>`;
};

const buildAddOns = () => {
  const cards = sundayContent.addOns.map(item => `
<div class="addon-card" style="flex:1;min-width:120px;background:#f8f6f4;border-radius:10px;overflow:hidden;text-align:center;">
<img src="${item.image}" style="width:100%;height:90px;object-fit:cover;display:block;">
<div style="padding:8px;">
<p style="margin:0;color:#590B3F;font-weight:bold;font-size:12px;">${item.name}</p>
</div>
</div>
`).join('');

  return `<tr>
<td style="padding:0 28px 24px;">
<p style="margin:0 0 10px;color:#666;font-size:14px;">Add-ons available:</p>
<div class="addon-row" style="display:flex;gap:10px;">
${cards}
</div>
</td>
</tr>`;
};

const buildMondayLunch = () => {
  const cards = sundayContent.mondayLunch.map(item => `
<div class="lunch-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
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
<div style="border-top:2px dashed #e5e5e5;padding-top:24px;"></div>
<h2 style="margin:0 0 16px;color:#590B3F;font-size:20px;">🥪 Get Lunch Monday</h2>
<p style="margin:0 0 16px;color:#666;font-size:15px;">We're open Monday for walk-ups. Here are two ways to start your week right:</p>
<div class="lunch-grid" style="display:flex;gap:16px;">
${cards}
</div>
</td>
</tr>`;
};

const buildThisWeek = () => {
  if (!sundayContent.thisWeek.hasContent || sundayContent.thisWeek.items.length === 0) return '';

  const items = sundayContent.thisWeek.items.map(item => `
<tr><td style="padding:8px 0;border-bottom:1px solid #eee;">
<p style="margin:0;color:#AF3D4B;font-weight:bold;font-size:13px;">${item.day}</p>
<p style="margin:0;color:#333;font-size:14px;">${item.text}</p>
</td></tr>
`).join('');

  return `<tr>
<td style="padding:0 28px 24px;">
<div style="border-top:2px dashed #e5e5e5;padding-top:24px;"></div>
<h2 style="margin:0 0 16px;color:#590B3F;font-size:20px;">📅 ${sundayContent.thisWeek.title}</h2>
<table width="100%" cellpadding="0" cellspacing="0">
${items}
</table>
</td>
</tr>`;
};

const template = {
  email_subject: "📋 This Week's Menu + Monday Lunch Tease",
  email_body: wrapEmail(`
<!-- MEAL PREP SECTION -->
<tr>
<td style="background:linear-gradient(135deg,#590B3F 0%,#8B1A4E 100%);padding:32px 28px;text-align:center;">
<p style="margin:0 0 8px;color:#FFD700;font-size:14px;font-weight:bold;letter-spacing:1px;">📋 MEAL PREP MENU</p>
<h1 style="margin:0 0 8px;color:#fff;font-size:26px;line-height:1.2;">This Week's Bowls</h1>
<p style="margin:0;color:#fff;opacity:0.9;font-size:15px;">Orders close Wednesday noon · Pickup Thursday</p>
</td>
</tr>

${buildMenuGrid()}

${buildAddOns()}

<tr>
<td style="padding:0 28px 24px;text-align:center;">
<a href="${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=sunday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Order Meal Prep →
</a>
</td>
</tr>

<!-- REGULAR DELI SECTION -->
<tr>
<td style="padding:0 28px;">
<div style="border-top:2px dashed #e5e5e5;padding-top:24px;"></div>
<p style="margin:0 0 8px;color:#AF3D4B;font-size:14px;font-weight:bold;letter-spacing:0.5px;">REGULAR DELI</p>
<h2 style="margin:0 0 16px;color:#590B3F;font-size:24px;">Monday Lunch Tease 🥪</h2>
<p style="margin:0 0 16px;color:#666;font-size:15px;">We're open Monday for walk-ups. Here are two ways to start your week right:</p>
</td>
</tr>

${buildMondayLunch()}

${buildThisWeek()}

<tr>
<td style="padding:0 28px 32px;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f6f4;border-radius:12px;padding:20px;">
<tr><td style="text-align:center;">
<h3 style="margin:0 0 12px;color:#590B3F;font-size:16px;">Meal Prep Schedule</h3>
<p style="margin:0 0 6px;color:#333;font-size:14px;">🟢 Orders open Thursday 8:00 PM</p>
<p style="margin:0 0 6px;color:#333;font-size:14px;">🔴 Orders close Wednesday 12:00 PM</p>
<p style="margin:0;color:#333;font-size:14px;">📦 Pickup Thursday 12:30 PM – 7:30 PM</p>
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
