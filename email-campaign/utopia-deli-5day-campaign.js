const day = $input.first().json.campaign_day;

const baseURL = "https://order.theutopiadeli.com";

const images = {
  logo: 'https://order.theutopiadeli.com/images/logo.png',
  monday: [
    'https://raw.githubusercontent.com/Phillip-Lowe/utopia-deli/refs/heads/main/Deli%20Meal%20Prep%20Plate%201.jpg',
    'https://order.theutopiadeli.com/catering/images/meal-mediterranean-harvest.jpg',
    'https://order.theutopiadeli.com/catering/images/meal-thai-peanut-crunch.jpg',
    'https://order.theutopiadeli.com/catering/images/meal-eggplant-parm.jpg',
    'https://order.theutopiadeli.com/catering/images/meal-cajun-northern-beans.jpg',
    'https://order.theutopiadeli.com/catering/images/cold_pressed_juice_v2.jpg',
    'https://order.theutopiadeli.com/catering/images/dessert-raspberry-mousse.jpg',
  ],
  tuesday: [
    'https://raw.githubusercontent.com/Phillip-Lowe/utopia-deli/refs/heads/main/email-campaign/catering-3.jpg',
    'https://raw.githubusercontent.com/Phillip-Lowe/utopia-deli/refs/heads/main/email-campaign/catering-1.jpg',
    'https://raw.githubusercontent.com/Phillip-Lowe/utopia-deli/refs/heads/main/email-campaign/catering-4.jpg',
    'https://raw.githubusercontent.com/Phillip-Lowe/utopia-deli/refs/heads/main/email-campaign/catering-2.jpg',
  ],
  wednesday: [
    'https://order.theutopiadeli.com/catering/images/meal-mediterranean-harvest.jpg',
    'https://order.theutopiadeli.com/catering/images/meal-thai-peanut-crunch.jpg',
    'https://order.theutopiadeli.com/catering/images/meal-eggplant-parm.jpg',
  ],
  thursday: [
    'https://raw.githubusercontent.com/Phillip-Lowe/utopia-deli/refs/heads/main/Deli%20Meal%20Prep%20Plate%201.jpg',
    'https://order.theutopiadeli.com/images/stek%20Philly.jpg',
    'https://order.theutopiadeli.com/images/loaded_bacon_fry.jpg',
    'https://order.theutopiadeli.com/images/chicken_poppers_v3.jpg',
  ],
  friday: [
    'https://raw.githubusercontent.com/Phillip-Lowe/utopia-deli/refs/heads/main/Deli%20Meal%20Prep%20Plate%201.jpg',
    'https://order.theutopiadeli.com/catering/images/meal-mediterranean-harvest.jpg',
    'https://order.theutopiadeli.com/catering/images/meal-thai-peanut-crunch.jpg',
    'https://order.theutopiadeli.com/catering/images/meal-eggplant-parm.jpg',
    'https://order.theutopiadeli.com/catering/images/meal-cajun-northern-beans.jpg',
    'https://order.theutopiadeli.com/catering/images/cold_pressed_juice_v2.jpg',
    'https://order.theutopiadeli.com/catering/images/dessert-raspberry-mousse.jpg',
  ]
};

const buildHeader = () => `
<tr>
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

const buildFooter = () => `
<tr>
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

const wrapEmail = (content) => `
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
@media only screen and (max-width: 600px) {
 .container { width: 100% !important; }
 .hero-img { height: 200px !important; }
 .dish-grid { display: block !important; }
 .dish-card { width: 100% !important; margin-bottom: 16px !important; }
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

const templates = {

  // ═══════════════════════════════════════════
  // MONDAY — We're Open + Meal Prep Closes Wed
  // ═══════════════════════════════════════════
  monday: {
    email_subject: "🍽️ We're Open Today — Meal Prep Closes Wednesday",
    email_body: wrapEmail(`
<tr>
<td>
<img src="${images.monday[0]}" alt="Utopia Deli Meal Prep Bowl" class="hero-img" style="width:100%;height:320px;object-fit:cover;display:block;">
</td>
</tr>

<tr>
<td style="padding:32px 28px 20px;">
<h1 style="margin:0 0 16px;color:#590B3F;font-size:28px;line-height:1.2;">We're Open Today 🍽️</h1>
<p style="margin:0 0 20px;color:#333;font-size:16px;line-height:1.6;">
Order online for pickup — we're serving fresh from 12:30 to 7:30. And don't forget: meal prep orders close Wednesday at noon.
</p>
<p style="margin:0 0 24px;color:#AF3D4B;font-size:15px;font-weight:bold;">
🕐 Open today 12:30PM–7:30PM · ⏰ Meal prep closes Wednesday 12:00 PM
</p>
<div style="text-align:center;">
<a href="${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=monday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;margin-right:8px;">
Order Online
</a>
<a href="${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=monday"
style="display:inline-block;background:transparent;color:#AF3D4B;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;border:2px solid #AF3D4B;">
Order Meal Prep
</a>
</div>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<h2 style="margin:0 0 16px;color:#590B3F;font-size:20px;">Meal Prep — Order Before Wednesday Noon</h2>
<div class="dish-grid" style="display:flex;gap:16px;flex-wrap:wrap;">

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.monday[1]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Mediterranean Harvest Bowl</p>
<p style="margin:0;color:#888;font-size:12px;">Lemon herb quinoa, crispy oregano chickpeas, cucumber tomato salad, hummus, tahini drizzle, pickled red onion — 500 cal</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.monday[2]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Thai Peanut Crunch Bowl</p>
<p style="margin:0;color:#888;font-size:12px;">Jasmine rice, crispy peanut tofu, sesame cabbage slaw, sweet chili peanut drizzle — 490 cal</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.monday[3]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Eggplant Parmesan</p>
<p style="margin:0;color:#888;font-size:12px;">Parmesan crusted eggplant layered with homemade marinara, topped with fresh basil — 530 cal</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.monday[4]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Cajun Red Beans & Dirty Rice</p>
<p style="margin:0;color:#888;font-size:12px;">Dirty rice, Cajun beans, peppers & onions, green onion garnish — 460 cal</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.monday[6]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Raspberry Dark Chocolate Mousse</p>
<p style="margin:0;color:#888;font-size:12px;">Rich dark chocolate mousse topped with fresh raspberries — sugar free</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.monday[5]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Cold-Pressed Juice</p>
<p style="margin:0;color:#888;font-size:12px;">Fresh 10oz juice</p>
</div>
</div>

</div>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f6f4;border-radius:12px;padding:20px;">
<tr><td>
<h3 style="margin:0 0 12px;color:#590B3F;font-size:16px;">How Meal Prep Works</h3>
<p style="margin:0 0 8px;color:#333;font-size:14px;line-height:1.5;">① Order online by Wednesday noon</p>
<p style="margin:0 0 8px;color:#333;font-size:14px;line-height:1.5;">② We prepare fresh Thursday morning</p>
<p style="margin:0;color:#333;font-size:14px;line-height:1.5;">③ Pick up Thursday 12:30PM–7:30PM at 801 S Chester St</p>
</td></tr>
</table>
</td>
</tr>

<tr>
<td style="padding:0 28px 32px;text-align:center;">
<a href="${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=monday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Order Meal Prep — Closes Wednesday 12:00 PM
</a>
</td>
</tr>
`),
    sms_body: "We're open today 🍽️ Meal prep closes Wed noon. order.theutopiadeli.com"
  },

  // ═══════════════════════════════════════════
  // TUESDAY — Catering Push
  // ═══════════════════════════════════════════
  tuesday: {
    email_subject: "🎉 Planning an Event? Let's Cater It",
    email_body: wrapEmail(`
<tr>
<td>
<img src="${images.tuesday[0]}" alt="Utopia Deli Catering Spread" class="hero-img" style="width:100%;height:320px;object-fit:cover;display:block;">
</td>
</tr>

<tr>
<td style="padding:32px 28px 20px;">
<h1 style="margin:0 0 16px;color:#590B3F;font-size:28px;line-height:1.2;">Planning an Event? Let's Make It Delicious 🎉</h1>
<p style="margin:0 0 20px;color:#333;font-size:16px;line-height:1.6;">
Weddings, birthdays, corporate lunches, graduation parties — we cater events from 10 to 500 guests. Drop-off, staffed buffet, or full-service. Bold, plant-forward flavors that everyone remembers.
</p>
<p style="margin:0 0 24px;color:#AF3D4B;font-size:15px;font-weight:bold;">
Minimum 10 guests · 3 days advance notice · 50% deposit to book
</p>
<a href="${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=tuesday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Get a Catering Quote
</a>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<h2 style="margin:0 0 16px;color:#590B3F;font-size:20px;">What We Bring to the Table</h2>
<div class="dish-grid" style="display:flex;gap:16px;flex-wrap:wrap;">

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.tuesday[0]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Full-Service Catering</p>
<p style="margin:0;color:#888;font-size:12px;">Pasta, garlic bread, fresh salad, sweet tea — complete buffet spread for any occasion</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.tuesday[1]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Baked Ziti & Lasagna</p>
<p style="margin:0;color:#888;font-size:12px;">Cheesy baked pasta casseroles with Italian herbs — crowd favorites</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.tuesday[2]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Fresh Fruit Platters</p>
<p style="margin:0;color:#888;font-size:12px;">Watermelon, cantaloupe, mango, pineapple — beautifully arranged on wooden boards</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.tuesday[3]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Fresh Glazed Donuts</p>
<p style="margin:0;color:#888;font-size:12px;">Old-fashioned cake donuts with crackly sugar glaze — perfect for morning meetings</p>
</div>
</div>

</div>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f6f4;border-radius:12px;padding:20px;">
<tr><td>
<h3 style="margin:0 0 12px;color:#590B3F;font-size:16px;">How Catering Works</h3>
<p style="margin:0 0 8px;color:#333;font-size:14px;line-height:1.5;">① Fill out our quick catering form</p>
<p style="margin:0 0 8px;color:#333;font-size:14px;line-height:1.5;">② We'll follow up with a custom quote within 24 hours</p>
<p style="margin:0;color:#333;font-size:14px;line-height:1.5;">③ Confirm, and we handle the rest — food, setup, everything</p>
</td></tr>
</table>
</td>
</tr>

<tr>
<td style="padding:0 28px 32px;text-align:center;">
<a href="${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=tuesday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Start Your Catering Order
</a>
</td>
</tr>
`),
    sms_body: "Planning an event? 🎉 Catering from Utopia Deli. order.theutopiadeli.com/catering/"
  },

  // ═══════════════════════════════════════════
  // WEDNESDAY — Last Call Meal Prep + We're Open
  // ═══════════════════════════════════════════
  wednesday: {
    email_subject: "⏰ Meal Prep Closes at Noon — Last Call",
    email_body: wrapEmail(`
<tr>
<td>
<img src="${images.wednesday[0]}" alt="Mediterranean Harvest Bowl" class="hero-img" style="width:100%;height:280px;object-fit:cover;display:block;">
</td>
</tr>

<tr>
<td style="padding:32px 28px 20px;text-align:center;">
<h1 style="margin:0 0 16px;color:#AF3D4B;font-size:28px;line-height:1.2;">Meal Prep Closes Today at Noon ⏰</h1>
<p style="margin:0 0 20px;color:#333;font-size:16px;line-height:1.6;">
This is your last chance to grab this week's bowls. Fresh, chef-crafted meals ready for pickup Thursday.
</p>
<p style="margin:0 0 24px;color:#333;font-size:14px;">
<strong>Order before noon today</strong> — pickup Thursday 12:30 PM–7:30 PM
</p>
<a href="${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=wednesday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Secure My Bowls
</a>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f6f4;border-radius:12px;padding:20px;">
<tr><td style="text-align:center;">
<p style="margin:0 0 12px;color:#590B3F;font-size:18px;font-weight:bold;">This Week's Bowls</p>
<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">
<div style="text-align:center;">
<img src="${images.wednesday[0]}" style="width:120px;height:100px;object-fit:cover;border-radius:8px;display:block;margin:0 auto 8px;">
<p style="margin:0;color:#333;font-size:12px;">Mediterranean Harvest</p>
</div>
<div style="text-align:center;">
<img src="${images.wednesday[1]}" style="width:120px;height:100px;object-fit:cover;border-radius:8px;display:block;margin:0 auto 8px;">
<p style="margin:0;color:#333;font-size:12px;">Thai Peanut Crunch</p>
</div>
<div style="text-align:center;">
<img src="${images.wednesday[2]}" style="width:120px;height:100px;object-fit:cover;border-radius:8px;display:block;margin:0 auto 8px;">
<p style="margin:0;color:#333;font-size:12px;">Eggplant Parmesan</p>
</div>
</div>
</td></tr>
</table>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#590B3F;border-radius:12px;padding:20px;">
<tr><td style="text-align:center;">
<p style="margin:0 0 4px;color:#fff;font-size:16px;font-weight:bold;">We're Open Today 🍽️</p>
<p style="margin:0;color:#fff;font-size:14px;">Order online for pickup 12:30PM–7:30PM · 801 S Chester St</p>
</td></tr>
</table>
</td>
</tr>

<tr>
<td style="padding:0 28px 32px;text-align:center;">
<a href="${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=wednesday"
style="display:inline-block;background:transparent;color:#AF3D4B;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;border:2px solid #AF3D4B;">
Order Online for Pickup
</a>
</td>
</tr>
`),
    sms_body: "⏰ Meal prep closes today at noon! order.theutopiadeli.com/catering/"
  },

  // ═══════════════════════════════════════════
  // THURSDAY — Pick Up Your Bowls + We're Open
  // ═══════════════════════════════════════════
  thursday: {
    email_subject: "📦 Pick Up Your Bowls Today + We're Open",
    email_body: wrapEmail(`
<tr>
<td>
<img src="${images.thursday[0]}" alt="Utopia Deli Meal Prep Pickup" class="hero-img" style="width:100%;height:300px;object-fit:cover;display:block;">
</td>
</tr>

<tr>
<td style="padding:32px 28px 20px;">
<h1 style="margin:0 0 16px;color:#590B3F;font-size:28px;line-height:1.2;">Pick Up Your Bowls Today 📦</h1>
<p style="margin:0 0 20px;color:#333;font-size:16px;line-height:1.6;">
Your meal prep is ready! Swing by 801 S Chester St between 12:30 and 7:30 PM. Have your name ready at the window.
</p>
<p style="margin:0 0 24px;color:#AF3D4B;font-size:15px;font-weight:bold;">
🕐 Pickup 12:30PM–7:30PM · 📍 801 S Chester St, Little Rock
</p>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<h2 style="margin:0 0 16px;color:#590B3F;font-size:20px;">Order Online for Pickup — We're Open 🍽️</h2>
<div class="dish-grid" style="display:flex;gap:16px;flex-wrap:wrap;">

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.thursday[1]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Stek Philly</p>
<p style="margin:0;color:#888;font-size:12px;">Thin-cut steak, peppers, onions, hoagie roll</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.thursday[2]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Loaded Bac'n Fry</p>
<p style="margin:0;color:#888;font-size:12px;">Crinkle-cut fries loaded with bac'n, cheeze sauce</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.thursday[3]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Chick'n Poppers</p>
<p style="margin:0;color:#888;font-size:12px;">Crispy dippers — BBQ, Garlic Parm, Jerk, Buffalo, Lemon Pepper</p>
</div>
</div>

</div>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f6f4;border-radius:12px;padding:20px;">
<tr><td>
<h3 style="margin:0 0 12px;color:#590B3F;font-size:16px;">Catering This Week?</h3>
<p style="margin:0 0 8px;color:#333;font-size:14px;line-height:1.5;">Got an event coming up? We cater parties, meetings, weddings — 10 to 500 guests.</p>
<p style="margin:0;color:#333;font-size:14px;line-height:1.5;"><a href="${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=thursday" style="color:#AF3D4B;font-weight:bold;">Request a catering quote →</a></p>
</td></tr>
</table>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#590B3F;border-radius:12px;padding:20px;">
<tr><td style="text-align:center;">
<p style="margin:0 0 4px;color:#fff;font-size:16px;font-weight:bold;">The Utopia Deli</p>
<p style="margin:0 0 4px;color:#fff;font-size:14px;">801 S Chester St, Little Rock, AR 72202</p>
<p style="margin:0;color:#fff;font-size:13px;opacity:0.8;">Monday–Saturday · 12:30PM–7:30PM</p>
</td></tr>
</table>
</td>
</tr>

<tr>
<td style="padding:0 28px 32px;text-align:center;">
<a href="${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=thursday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Order Online
</a>
</td>
</tr>
`),
    sms_body: "📦 Pick up your meal prep today 12:30–7:30PM at 801 S Chester St!"
  },

  // ═══════════════════════════════════════════
  // FRIDAY — New Week Fresh Bowls + Weekend
  // ═══════════════════════════════════════════
  friday: {
    email_subject: "🍱 New Week, Fresh Bowls — Meal Prep Is Live",
    email_body: wrapEmail(`
<tr>
<td>
<img src="${images.friday[0]}" alt="Utopia Deli Fresh Meal Prep" class="hero-img" style="width:100%;height:320px;object-fit:cover;display:block;">
</td>
</tr>

<tr>
<td style="padding:32px 28px 20px;">
<h1 style="margin:0 0 16px;color:#590B3F;font-size:28px;line-height:1.2;">New Week, Fresh Bowls 🍱</h1>
<p style="margin:0 0 20px;color:#333;font-size:16px;line-height:1.6;">
This week's meal prep is live. Chef-crafted bowls, fresh ingredients, zero cooking on your end. Order now — closes Wednesday at noon.
</p>
<p style="margin:0 0 24px;color:#AF3D4B;font-size:15px;font-weight:bold;">
🟢 Orders open now · 🔴 Closes Wednesday 12:00 PM · 📦 Pickup Thursday
</p>
<a href="${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=friday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Order Meal Prep
</a>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<h2 style="margin:0 0 16px;color:#590B3F;font-size:20px;">This Week's Bowls</h2>
<div class="dish-grid" style="display:flex;gap:16px;flex-wrap:wrap;">

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.friday[1]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Mediterranean Harvest Bowl</p>
<p style="margin:0;color:#888;font-size:12px;">Lemon herb quinoa, crispy oregano chickpeas, cucumber tomato salad, hummus, tahini drizzle, pickled red onion — 500 cal</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.friday[2]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Thai Peanut Crunch Bowl</p>
<p style="margin:0;color:#888;font-size:12px;">Jasmine rice, crispy peanut tofu, sesame cabbage slaw, sweet chili peanut drizzle — 490 cal</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.friday[3]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Eggplant Parmesan</p>
<p style="margin:0;color:#888;font-size:12px;">Parmesan crusted eggplant layered with homemade marinara, topped with fresh basil — 530 cal</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.friday[4]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Cajun Red Beans & Dirty Rice</p>
<p style="margin:0;color:#888;font-size:12px;">Dirty rice, Cajun beans, peppers & onions, green onion garnish — 460 cal</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.friday[6]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Raspberry Dark Chocolate Mousse</p>
<p style="margin:0;color:#888;font-size:12px;">Rich dark chocolate mousse topped with fresh raspberries — sugar free</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.friday[5]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Cold-Pressed Juice</p>
<p style="margin:0;color:#888;font-size:12px;">Fresh 10oz juice</p>
</div>
</div>

</div>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f6f4;border-radius:12px;padding:20px;">
<tr><td>
<h3 style="margin:0 0 12px;color:#590B3F;font-size:16px;">How Meal Prep Works</h3>
<p style="margin:0 0 8px;color:#333;font-size:14px;line-height:1.5;">① Order online by Wednesday noon</p>
<p style="margin:0 0 8px;color:#333;font-size:14px;line-height:1.5;">② We prepare fresh Thursday morning</p>
<p style="margin:0;color:#333;font-size:14px;line-height:1.5;">③ Pick up Thursday 12:30PM–7:30PM at 801 S Chester St</p>
</td></tr>
</table>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#590B3F;border-radius:12px;padding:20px;">
<tr><td style="text-align:center;">
<p style="margin:0 0 4px;color:#fff;font-size:16px;font-weight:bold;">Weekend Hours</p>
<p style="margin:0 0 4px;color:#fff;font-size:14px;">Friday & Saturday · 12:30PM–7:30PM</p>
<p style="margin:0;color:#fff;font-size:13px;opacity:0.8;">Order online for pickup — we've got you</p>
</td></tr>
</table>
</td>
</tr>

<tr>
<td style="padding:0 28px 32px;text-align:center;">
<a href="${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=friday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Order Meal Prep Now
</a>
</td>
</tr>
`),
    sms_body: "🍱 New week meal prep is live! Order by Wed noon. order.theutopiadeli.com/catering/"
  }
};

const template = templates[day] || templates.monday;
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
