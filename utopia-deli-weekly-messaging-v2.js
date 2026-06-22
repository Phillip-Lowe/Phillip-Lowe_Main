const day = $input.first().json.campaign_day;

// Image assets hosted on order.theutopiadeli.com
const images = {
  logo: 'https://order.theutopiadeli.com/images/logo.png',
  monday: [
    'https://order.theutopiadeli.com/images/mealprep-mediterranean.jpg',
    'https://order.theutopiadeli.com/images/mealprep-smokey-taco.jpg',
    'https://order.theutopiadeli.com/images/mealprep-bbq-mac.jpg'
  ],
  wednesday: [
    'https://order.theutopiadeli.com/images/mealprep-smokey-taco.jpg',
    'https://order.theutopiadeli.com/images/mealprep-chili-noodles.jpg',
    'https://order.theutopiadeli.com/images/mealprep-peanut-tofu.jpg'
  ],
  friday: [
    'https://order.theutopiadeli.com/images/stek%20Philly.jpg',
    'https://order.theutopiadeli.com/images/mealprep-mediterranean.jpg',
    'https://order.theutopiadeli.com/images/mealprep-coconut-chickpea.jpg'
  ]
};

// Color palette
const C = {
  burgundy: '#590B3F',
  rust: '#AF3D4B',
  cream: '#f8f6f4',
  white: '#ffffff',
  text: '#333333',
  muted: '#888888'
};

const templates = {
  monday: {
    email_subject: "🍱 Meal Prep is Open — Fresh Bowls This Week",
    email_body: `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Meal Prep Open</title>
<style>
@media only screen and (max-width: 600px) {
  .container { width: 100% !important; }
  .hero-img { height: 200px !important; }
  .dish-grid { display: block !important; }
  .dish-card { width: 100% !important; margin-bottom: 16px !important; }
  .header-text { font-size: 20px !important; }
}
</style>
</head>
<body style="margin:0;padding:0;background:${C.cream};font-family:'Georgia','Times New Roman',serif;">
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td align="center" style="padding:24px 12px;">
<table class="container" width="600" cellpadding="0" cellspacing="0" border="0" style="background:${C.white};border-radius:16px;overflow:hidden;max-width:600px;width:100%;">

<!-- Logo Header with Brand Name -->
<tr>
<td style="background:${C.burgundy};padding:20px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr>
<td style="vertical-align:middle;">
<img src="${images.logo}" alt="The Utopia Deli" style="height:56px;display:block;">
</td>
<td style="vertical-align:middle;padding-left:16px;">
<p class="header-text" style="margin:0;color:#fff;font-family:'Georgia','Times New Roman',serif;font-size:24px;font-weight:bold;letter-spacing:0.5px;">The Utopia Deli</p>
</td>
</tr>
</table>
</td>
</tr>

<!-- Hero Image -->
<tr>
<td>
<img src="${images.monday[0]}" alt="Mediterranean Harvest Bowl" class="hero-img" style="width:100%;height:320px;object-fit:cover;display:block;">
</td>
</tr>

<!-- Hero Text -->
<tr>
<td style="padding:32px 28px 20px;">
<h1 style="margin:0 0 16px;color:${C.burgundy};font-size:28px;line-height:1.2;">This Week's Meal Prep is Open 🍱</h1>
<p style="margin:0 0 20px;color:${C.text};font-size:16px;line-height:1.6;">
Fresh, chef-crafted bowls ready for pickup. No cooking, no waiting — just heat and eat.
</p>
<p style="margin:0 0 24px;color:${C.rust};font-size:15px;font-weight:bold;">
⏰ Orders close Wednesday at 12PM · Pickup Thursday
</p>
<a href="https://order.theutopiadeli.com/catering/"
style="display:inline-block;background:${C.rust};color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Order Meal Prep
</a>
</td>
</tr>

<!-- This Week's Menu -->
<tr>
<td style="padding:0 28px 24px;">
<h2 style="margin:0 0 16px;color:${C.burgundy};font-size:20px;">This Week's Lineup</h2>
<div class="dish-grid" style="display:flex;gap:16px;flex-wrap:wrap;">

<div class="dish-card" style="flex:1;min-width:160px;background:${C.cream};border-radius:12px;overflow:hidden;">
<img src="${images.monday[0]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:${C.burgundy};font-weight:bold;font-size:14px;">Mediterranean Harvest</p>
<p style="margin:0;color:${C.muted};font-size:12px;">Quinoa, roasted veg, falafel, tahini</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:${C.cream};border-radius:12px;overflow:hidden;">
<img src="${images.monday[1]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:${C.burgundy};font-weight:bold;font-size:14px;">Smokey Taco Bowl</p>
<p style="margin:0;color:${C.muted};font-size:12px;">Black beans, corn, jackfruit, chipotle crema</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:${C.cream};border-radius:12px;overflow:hidden;">
<img src="${images.monday[2]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:${C.burgundy};font-weight:bold;font-size:14px;">BBQ Mac & Greens</p>
<p style="margin:0;color:${C.muted};font-size:12px;">Smoked jackfruit, vegan mac, collards</p>
</div>
</div>

</div>
</td>
</tr>

<!-- How It Works -->
<tr>
<td style="padding:0 28px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:${C.cream};border-radius:12px;padding:20px;">
<tr><td>
<h3 style="margin:0 0 12px;color:${C.burgundy};font-size:16px;">How Meal Prep Works</h3>
<p style="margin:0 0 8px;color:${C.text};font-size:14px;line-height:1.5;">① Order online by Wednesday noon</p>
<p style="margin:0 0 8px;color:${C.text};font-size:14px;line-height:1.5;">② We cook fresh Thursday morning</p>
<p style="margin:0;color:${C.text};font-size:14px;line-height:1.5;">③ Pick up Thursday 12PM–7PM at 801 S Chester St</p>
</td></tr>
</table>
</td>
</tr>

<!-- CTA -->
<tr>
<td style="padding:0 28px 32px;text-align:center;">
<a href="https://order.theutopiadeli.com/catering/"
style="display:inline-block;background:${C.rust};color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Order Now — Closes Wednesday 12PM
</a>
</td>
</tr>

<!-- Footer -->
<tr>
<td style="padding:20px;background:${C.cream};text-align:center;border-top:1px solid #e5e5e5;">
<p style="margin:0 0 8px;color:${C.muted};font-size:13px;">
The Utopia Deli · 801 S Chester St, Little Rock, AR 72202
</p>
<p style="margin:0;color:${C.muted};font-size:12px;">
<a href="https://n8n.systack.net/webhook/unsubscribe?email=%%EMAIL%%&channel=email"
style="color:${C.rust};text-decoration:underline;">Unsubscribe from emails</a>
</p>
</td>
</tr>

</table>
</td></tr>
</table>
</body>
</html>`,
    sms_body: "Meal prep is open 🍱 Orders close Wed 12PM. order.theutopiadeli.com/catering/"
  },

  wednesday: {
    email_subject: "⏰ Closes Tomorrow at Noon — Don't Miss This Week's Bowls",
    email_body: `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Closing Soon</title>
<style>
@media only screen and (max-width: 600px) {
  .container { width: 100% !important; }
  .hero-img { height: 200px !important; }
  .header-text { font-size: 20px !important; }
}
</style>
</head>
<body style="margin:0;padding:0;background:${C.cream};font-family:'Georgia','Times New Roman',serif;">
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td align="center" style="padding:24px 12px;">
<table class="container" width="600" cellpadding="0" cellspacing="0" border="0" style="background:${C.white};border-radius:16px;overflow:hidden;max-width:600px;width:100%;">

<!-- Logo Header with Brand Name -->
<tr>
<td style="background:${C.burgundy};padding:20px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr>
<td style="vertical-align:middle;">
<img src="${images.logo}" alt="The Utopia Deli" style="height:56px;display:block;">
</td>
<td style="vertical-align:middle;padding-left:16px;">
<p class="header-text" style="margin:0;color:#fff;font-family:'Georgia','Times New Roman',serif;font-size:24px;font-weight:bold;letter-spacing:0.5px;">The Utopia Deli</p>
</td>
</tr>
</table>
</td>
</tr>

<!-- Hero Image -->
<tr>
<td>
<img src="${images.wednesday[0]}" alt="Smokey Taco Bowl" class="hero-img" style="width:100%;height:280px;object-fit:cover;display:block;">
</td>
</tr>

<!-- Urgency Text -->
<tr>
<td style="padding:32px 28px 20px;text-align:center;">
<h1 style="margin:0 0 16px;color:${C.rust};font-size:28px;line-height:1.2;">Closes Tomorrow at 12PM ⏰</h1>
<p style="margin:0 0 20px;color:${C.text};font-size:16px;line-height:1.6;">
This is your last chance to grab this week's meal prep. Fresh bowls, ready Thursday.
</p>
<p style="margin:0 0 24px;color:${C.text};font-size:14px;">
<strong>Order before noon tomorrow</strong> — pickup Thursday 12PM–7PM
</p>
<a href="https://order.theutopiadeli.com/catering/"
style="display:inline-block;background:${C.rust};color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Secure My Bowls
</a>
</td>
</tr>

<!-- Reminder Boxes -->
<tr>
<td style="padding:0 28px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:${C.cream};border-radius:12px;padding:20px;">
<tr><td style="text-align:center;">
<p style="margin:0 0 12px;color:${C.burgundy};font-size:18px;font-weight:bold;">Still Available This Week</p>
<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">
<div style="text-align:center;">
<img src="${images.wednesday[0]}" style="width:120px;height:100px;object-fit:cover;border-radius:8px;display:block;margin:0 auto 8px;">
<p style="margin:0;color:${C.text};font-size:13px;">Smokey Taco Bowl</p>
</div>
<div style="text-align:center;">
<img src="${images.wednesday[1]}" style="width:120px;height:100px;object-fit:cover;border-radius:8px;display:block;margin:0 auto 8px;">
<p style="margin:0;color:${C.text};font-size:13px;">Chili Garlic Noodles</p>
</div>
<div style="text-align:center;">
<img src="${images.wednesday[2]}" style="width:120px;height:100px;object-fit:cover;border-radius:8px;display:block;margin:0 auto 8px;">
<p style="margin:0;color:${C.text};font-size:13px;">Peanut Ginger Tofu</p>
</div>
</div>
</td></tr>
</table>
</td>
</tr>

<!-- Footer -->
<tr>
<td style="padding:20px;background:${C.cream};text-align:center;border-top:1px solid #e5e5e5;">
<p style="margin:0 0 8px;color:${C.muted};font-size:13px;">
The Utopia Deli · 801 S Chester St, Little Rock, AR 72202
</p>
<p style="margin:0;color:${C.muted};font-size:12px;">
<a href="https://n8n.systack.net/webhook/unsubscribe?email=%%EMAIL%%&channel=email"
style="color:${C.rust};text-decoration:underline;">Unsubscribe from emails</a>
</p>
</td>
</tr>

</table>
</td></tr>
</table>
</body>
</html>`,
    sms_body: "Meal prep closes tomorrow ⏰ Last call! order.theutopiadeli.com/catering/"
  },

  friday: {
    email_subject: "Weekend at Utopia 🍽️ Fresh Food, Good Vibes",
    email_body: `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Weekend at Utopia</title>
<style>
@media only screen and (max-width: 600px) {
  .container { width: 100% !important; }
  .hero-img { height: 200px !important; }
  .dish-grid { display: block !important; }
  .dish-card { width: 100% !important; margin-bottom: 16px !important; }
  .header-text { font-size: 20px !important; }
}
</style>
</head>
<body style="margin:0;padding:0;background:${C.cream};font-family:'Georgia','Times New Roman',serif;">
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td align="center" style="padding:24px 12px;">
<table class="container" width="600" cellpadding="0" cellspacing="0" border="0" style="background:${C.white};border-radius:16px;overflow:hidden;max-width:600px;width:100%;">

<!-- Logo Header with Brand Name -->
<tr>
<td style="background:${C.burgundy};padding:20px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr>
<td style="vertical-align:middle;">
<img src="${images.logo}" alt="The Utopia Deli" style="height:56px;display:block;">
</td>
<td style="vertical-align:middle;padding-left:16px;">
<p class="header-text" style="margin:0;color:#fff;font-family:'Georgia','Times New Roman',serif;font-size:24px;font-weight:bold;letter-spacing:0.5px;">The Utopia Deli</p>
</td>
</tr>
</table>
</td>
</tr>

<!-- Hero Image -->
<tr>
<td>
<img src="${images.friday[0]}" alt="Steak Philly" class="hero-img" style="width:100%;height:320px;object-fit:cover;display:block;">
</td>
</tr>

<!-- Intro -->
<tr>
<td style="padding:32px 28px 20px;">
<h1 style="margin:0 0 16px;color:${C.burgundy};font-size:28px;line-height:1.2;">Weekend at Utopia 🍽️</h1>
<p style="margin:0 0 20px;color:${C.text};font-size:16px;line-height:1.6;">
Open Friday & Saturday. Walk up, order fresh, eat happy. No prep needed — we've got you.
</p>
<p style="margin:0 0 24px;color:${C.rust};font-size:15px;font-weight:bold;">
Friday & Saturday · 12:30PM–7:30PM · Walk-ups welcome
</p>
<div style="text-align:center;">
<a href="https://order.theutopiadeli.com/pickup-order/"
style="display:inline-block;background:${C.rust};color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;margin-right:8px;">
Order Ahead
</a>
<a href="https://order.theutopiadeli.com/pickup-order/"
style="display:inline-block;background:transparent;color:${C.rust};padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;border:2px solid ${C.rust};">
View Full Menu
</a>
</div>
</td>
</tr>

<!-- Weekend Specials -->
<tr>
<td style="padding:0 28px 24px;">
<h2 style="margin:0 0 16px;color:${C.burgundy};font-size:20px;">Weekend Favorites</h2>
<div class="dish-grid" style="display:flex;gap:16px;flex-wrap:wrap;">

<div class="dish-card" style="flex:1;min-width:160px;background:${C.cream};border-radius:12px;overflow:hidden;">
<img src="${images.friday[0]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:${C.burgundy};font-weight:bold;font-size:14px;">Steak Philly</p>
<p style="margin:0;color:${C.muted};font-size:12px;">Thin-cut steak, peppers, onions, hoagie</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:${C.cream};border-radius:12px;overflow:hidden;">
<img src="${images.friday[1]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:${C.burgundy};font-weight:bold;font-size:14px;">Mediterranean Harvest</p>
<p style="margin:0;color:${C.muted};font-size:12px;">Quinoa bowl, roasted veg, tahini drizzle</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:${C.cream};border-radius:12px;overflow:hidden;">
<img src="${images.friday[2]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:${C.burgundy};font-weight:bold;font-size:14px;">Coconut Chickpea Curry</p>
<p style="margin:0;color:${C.muted};font-size:12px;">Creamy coconut, chickpeas, spinach, jasmine rice</p>
</div>
</div>

</div>
</td>
</tr>

<!-- Location Box -->
<tr>
<td style="padding:0 28px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:${C.burgundy};border-radius:12px;padding:20px;">
<tr><td style="text-align:center;">
<p style="margin:0 0 4px;color:#fff;font-size:16px;font-weight:bold;">The Utopia Deli</p>
<p style="margin:0 0 4px;color:#fff;font-size:14px;">801 S Chester St, Little Rock, AR 72202</p>
<p style="margin:0;color:#fff;font-size:13px;opacity:0.8;">Friday–Saturday · 12:30PM–7:30PM</p>
</td></tr>
</table>
</td>
</tr>

<!-- Footer -->
<tr>
<td style="padding:20px;background:${C.cream};text-align:center;border-top:1px solid #e5e5e5;">
<p style="margin:0 0 8px;color:${C.muted};font-size:13px;">
The Utopia Deli · 801 S Chester St, Little Rock, AR 72202
</p>
<p style="margin:0;color:${C.muted};font-size:12px;">
<a href="https://n8n.systack.net/webhook/unsubscribe?email=%%EMAIL%%&channel=email"
style="color:${C.rust};text-decoration:underline;">Unsubscribe from emails</a>
</p>
</td>
</tr>

</table>
</td></tr>
</table>
</body>
</html>`,
    sms_body: "Weekend at Utopia 🍽️ Fri–Sat 12:30-7:30. Walk up or order ahead: order.theutopiadeli.com/pickup-order/"
  }
};

const template = templates[day] || templates.monday;
const results = [];

for (const item of $input.all()) {
  const c = item.json;

  // Email output
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

  // SMS output (preserved for when Twilio is re-enabled)
  if (c.phone && !c.unsubscribed_sms) {
    results.push({
      json: {
        contact_id: c.id,
        channel: 'sms',
        to: c.phone,
        body: template.sms_body,
        campaign_day: day,
        media_url: images[day]?.[0] || null
      }
    });
  }
}

return results;
