// ═══════════════════════════════════════════════════════════════════════
// SATURDAY — Weekend Reminder
// Focus: "We're open today!" — lighter touch, drive walk-ups
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
// SWAP ZONE: Saturday Content (Update Weekly)
// ═══════════════════════════════════════════
const saturdayContent = {
  // Saturday headline (keep it short, punchy)
  headline: "We're Open Saturday 🙌",
  subheadline: "Today 12:30PM–7:30PM · Walk-ups welcome",
  // Optional: Today's feature or special
  todayFeature: {
    name: "Stek Philly",
    desc: "Our #1 seller — thin-cut steak, grilled peppers & onions, hoagie roll",
    image: "https://order.theutopiadeli.com/images/menu/stek%20Philly.jpg",
    cta: "Order Ahead →"
  },
  // Quick menu highlights (3 items, no descriptions)
  quickMenu: [
    { name: "Chick'n Poppers", image: "https://order.theutopiadeli.com/images/menu/chicken_poppers_v3.jpg" },
    { name: "Loaded Fries", image: "https://order.theutopiadeli.com/images/menu/loaded_bacon_fry.jpg" },
    { name: "Cold-Pressed Juice", image: "https://order.theutopiadeli.com/images/cold_pressed_juice_v2.jpg" }
  ],
  // Optional weekend special (same as Friday, or different)
  weekendSpecial: null, // Set to { text: "..." } if active
  // Meal prep reminder (subtle)
  mealPrepReminder: true // Show "orders close Wednesday" note
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
 .quick-grid { display: block !important; }
 .quick-card { width: 100% !important; margin-bottom: 12px !important; }
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

const buildQuickMenu = () => {
  const cards = saturdayContent.quickMenu.map(item => `
<div class="quick-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;text-align:center;">
<img src="${item.image}" style="width:100%;height:120px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0;color:#590B3F;font-weight:bold;font-size:14px;">${item.name}</p>
</div>
</div>
`).join('');

  return `<tr>
<td style="padding:0 28px 24px;">
<h2 style="margin:0 0 16px;color:#590B3F;font-size:18px;">What's Cooking Today</h2>
<div class="quick-grid" style="display:flex;gap:12px;">
${cards}
</div>
</td>
</tr>`;
};

const template = {
  email_subject: "🙌 We're Open Today! Saturday at Utopia",
  email_body: wrapEmail(`
<tr>
<td style="background:linear-gradient(135deg,#590B3F 0%,#8B1A4E 100%);padding:40px 28px;text-align:center;">
<p style="margin:0 0 8px;color:#FFD700;font-size:14px;font-weight:bold;letter-spacing:1px;">🍽️ OPEN TODAY</p>
<h1 style="margin:0 0 12px;color:#fff;font-size:28px;line-height:1.2;">${saturdayContent.headline}</h1>
<p style="margin:0;color:#fff;opacity:0.9;font-size:16px;">${saturdayContent.subheadline}</p>
</td>
</tr>

<tr>
<td style="padding:28px 28px 20px;">
${saturdayContent.todayFeature ? `
<div style="display:flex;gap:16px;align-items:center;background:#f8f6f4;border-radius:12px;padding:16px;margin:0 0 20px;">
<img src="${saturdayContent.todayFeature.image}" style="width:120px;height:120px;object-fit:cover;border-radius:10px;flex-shrink:0;">
<div>
<p style="margin:0 0 4px;color:#AF3D4B;font-size:12px;font-weight:bold;letter-spacing:0.5px;">TODAY'S FEATURE</p>
<p style="margin:0 0 6px;color:#590B3F;font-weight:bold;font-size:16px;">${saturdayContent.todayFeature.name}</p>
<p style="margin:0 0 12px;color:#666;font-size:14px;line-height:1.4;">${saturdayContent.todayFeature.desc}</p>
<a href="${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=saturday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:10px 24px;border-radius:8px;text-decoration:none;font-size:14px;font-weight:bold;">
${saturdayContent.todayFeature.cta}
</a>
</div>
</div>
` : ''}
<p style="margin:0 0 20px;color:#333;font-size:16px;line-height:1.6;">
Walk up, order fresh, eat happy. No reservations needed — just bring your appetite.
</p>
</td>
</tr>

${buildQuickMenu()}

<tr>
<td style="padding:0 28px 24px;text-align:center;">
<a href="${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=saturday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Order Ahead — Skip the Line
</a>
</td>
</tr>

${saturdayContent.mealPrepReminder ? `
<tr>
<td style="padding:0 28px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0ece8;border-radius:10px;padding:16px;">
<tr><td style="text-align:center;">
<p style="margin:0;color:#666;font-size:14px;">🍱 Meal prep orders close Wednesday at noon · Pickup Thursday</p>
</td></tr>
</table>
</td>
</tr>
` : ''}
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
