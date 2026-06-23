const day = $input.first().json.campaign_day;

const baseURL = "https://order.theutopiadeli.com";

const baseRepoURL = 'https://raw.githubusercontent.com/Phillip-Lowe/utopia-deli/main';

const images = {
  logo: `${baseRepoURL}/TheUtopiaDeliLogo.png`,
  monday: [
    `${baseRepoURL}/catering/images/meal-placeholder.png`,
    `${baseRepoURL}/catering/images/meal-mediterranean-harvest.jpg`,
    `${baseRepoURL}/catering/images/meal-thai-peanut-crunch.jpg`,
    `${baseRepoURL}/catering/images/meal-eggplant-parm.jpg`,
    `${baseRepoURL}/catering/images/meal-cajun-northern-beans.jpg`,
    `${baseRepoURL}/catering/images/cold_pressed_juice_v2.jpg`,
    `${baseRepoURL}/catering/images/dessert-raspberry-mousse.jpg`,
  ],
  tuesday: [
    `${baseRepoURL}/email-campaign/catering-3.jpg`,
    `${baseRepoURL}/email-campaign/catering-1.jpg`,
    `${baseRepoURL}/email-campaign/catering-4.jpg`,
    `${baseRepoURL}/email-campaign/catering-2.jpg`,
  ],
  wednesday: [
    `${baseRepoURL}/catering/images/meal-placeholder.png`,
    `${baseRepoURL}/catering/images/meal-mediterranean-harvest.jpg`,
    `${baseRepoURL}/catering/images/meal-thai-peanut-crunch.jpg`
  ],
  thursday: [
    `${baseRepoURL}/Deli%20Meal%20Prep%20Plate%201.jpg`,
    `${baseRepoURL}/chicken_philly.jpg`,
    `${baseRepoURL}/loaded_bacon_fry.jpg`,
    `${baseRepoURL}/chicken_poppers_v3.jpg`,
  ],
  friday: [
    `${baseRepoURL}/Deli%20Happy%20customer%20lady.jpg`,
    `${baseRepoURL}/chicken_philly.jpg`,
    `${baseRepoURL}/loaded_bacon_fry.jpg`,
    `${baseRepoURL}/chicken_poppers_v3.jpg`,
    `${baseRepoURL}/cookies_v2.jpg`,
    `${baseRepoURL}/cold_pressed_juice_v2.jpg`
  ],
  saturday: [
    `${baseRepoURL}/chicken_philly.jpg`,
    `${baseRepoURL}/chicken_poppers_v3.jpg`,
    `${baseRepoURL}/loaded_bacon_fry.jpg`,
    `${baseRepoURL}/cold_pressed_juice_v2.jpg`,
  ],
  sunday: [
    `${baseRepoURL}/Deli%20Meal%20Prep%20Plate%201.jpg`,
    `${baseRepoURL}/chicken_philly.jpg`,
    `${baseRepoURL}/chicken_poppers_v3.jpg`,
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
  // MONDAY — Meal Prep is Open
  // ═══════════════════════════════════════════
  monday: {
    email_subject: "🍱 Meal Prep is Open — Fresh Bowls This Week",
    email_body: wrapEmail(`
<tr>
<td>
<img src="${images.monday[0]}" alt="Utopia Deli Meal Prep Bowl" class="hero-img" style="width:100%;height:320px;object-fit:cover;display:block;">
</td>
</tr>

<tr>
<td style="padding:32px 28px 20px;">
<h1 style="margin:0 0 16px;color:#590B3F;font-size:28px;line-height:1.2;">This Week's Meal Prep is Open 🍱</h1>
<p style="margin:0 0 20px;color:#333;font-size:16px;line-height:1.6;">
Fresh, chef-crafted bowls ready for pickup. No cooking, no waiting — just heat and eat.
</p>
<p style="margin:0 0 24px;color:#AF3D4B;font-size:15px;font-weight:bold;">
⏰ Orders close Wednesday at 12:00 PM · Pickup Thursday
</p>
<a href="${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=monday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Get Your Meals
</a>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<h2 style="margin:0 0 16px;color:#590B3F;font-size:20px;">Meal Prep Favorites </h2>
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
<p style="margin:0;color:#888;font-size:12px;">Parmesan crusted eggplant layered with fragrant homemade marinara sauce, topped with fresh basil — 530 cal</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.monday[4]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Cajun Red Beans & Dirty Rice Bowl</p>
<p style="margin:0;color:#888;font-size:12px;">Dirty rice, Cajun beans, peppers & onions, green onion garnish — 460 cal</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<div style="width:100%;height:140px;background:#f8f6f4;display:flex;align-items:center;justify-content:center;font-size:48px;">🌮</div>
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Street Corn Taco Bowl</p>
<p style="margin:0;color:#888;font-size:12px;">Cilantro lime rice, chipotle lentil taco crumble, roasted corn, black beans, pickled onions, chipotle crema — 470 cal</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<div style="width:100%;height:140px;background:#f8f6f4;display:flex;align-items:center;justify-content:center;font-size:48px;">🌶️</div>
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Nashville Hot Lentil Bowl</p>
<p style="margin:0;color:#888;font-size:12px;">Garlic rice, Nashville hot lentils, roasted broccoli, ranch drizzle — 480 cal</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<div style="width:100%;height:140px;background:#f8f6f4;display:flex;align-items:center;justify-content:center;font-size:48px;">🥔</div>
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Loaded BBQ Potato Bowl</p>
<p style="margin:0;color:#888;font-size:12px;">Roasted potatoes, BBQ lentil crumble, broccoli, smoked cheeze sauce, green onions — 510 cal</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.monday[5]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Raspberry Dark Chocolate Mousse</p>
<p style="margin:0;color:#888;font-size:12px;">Rich dark chocolate mousse topped with fresh raspberries — sugar free</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.monday[6]}" style="width:100%;height:140px;object-fit:cover;display:block;">
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
Order Now — Closes Wednesday 12:00 PM
</a>
</td>
</tr>
`),
    sms_body: "Meal prep is open 🍱 Orders close Wed 12:00 PM. order.theutopiadeli.com/catering/"
  },

  // ═══════════════════════════════════════════
  // TUESDAY — Catering Push
  // ═══════════════════════════════════════════
  tuesday: {
    email_subject: "🎉 Planning an Event? Let's Cater It",
    email_body: wrapEmail(`
<tr>
<td>
<img src="${images.tuesday[0]}" alt="Utopia Deli Catering" class="hero-img" style="width:100%;height:320px;object-fit:cover;display:block;">
</td>
</tr>

<tr>
<td style="padding:32px 28px 20px;">
<h1 style="margin:0 0 16px;color:#590B3F;font-size:28px;line-height:1.2;">Planning an Event? Let's Make It Delicious 🎉</h1>
<p style="margin:0 0 20px;color:#333;font-size:16px;line-height:1.6;">
Weddings, birthdays, celebrations — we cater events of all sizes. From intimate gatherings to full-scale celebrations, Utopia Deli brings bold, plant-forward flavors that everyone remembers.
</p>
<p style="margin:0 0 24px;color:#AF3D4B;font-size:15px;font-weight:bold;">
Minimum 10 guests · 3 days advance notice
</p>
<a href="${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=tuesday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Get a Catering Quote
</a>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<h2 style="margin:0 0 16px;color:#590B3F;font-size:20px;">Catering Menu</h2>
<div class="dish-grid" style="display:flex;gap:16px;flex-wrap:wrap;">

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.tuesday[0]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Full-Service Catering</p>
<p style="margin:0;color:#888;font-size:12px;">Pasta, garlic bread, fresh salad, sweet tea — full buffet spread for any occasion</p>
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
  // WEDNESDAY — Meal Prep Deadline
  // ═══════════════════════════════════════════
  wednesday: {
    email_subject: "⏰ Closes Today at Noon — Don't Miss This Week's Bowls",
    email_body: wrapEmail(`
<tr>
<td>
<img src="${images.wednesday[0]}" alt="Smokey Taco Bowl" class="hero-img" style="width:100%;height:280px;object-fit:cover;display:block;">
</td>
</tr>

<tr>
<td style="padding:32px 28px 20px;text-align:center;">
<h1 style="margin:0 0 16px;color:#AF3D4B;font-size:28px;line-height:1.2;">Closes Today at 12:00 PM ⏰</h1>
<p style="margin:0 0 20px;color:#333;font-size:16px;line-height:1.6;">
This is your last chance to grab this week's meal prep. Fresh bowls, ready Thursday.
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
<p style="margin:0 0 12px;color:#590B3F;font-size:18px;font-weight:bold;">Meal Prep Favorites</p>
<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">
<div style="text-align:center;">
<div style="width:120px;height:100px;background:#f8f6f4;display:flex;align-items:center;justify-content:center;border-radius:8px;font-size:32px;">🌮</div>
<p style="margin:8px 0 0;color:#333;font-size:12px;">Street Corn Taco Bowl</p>
</div>
<div style="text-align:center;">
<div style="width:120px;height:100px;background:#f8f6f4;display:flex;align-items:center;justify-content:center;border-radius:8px;font-size:32px;">🌶️</div>
<p style="margin:8px 0 0;color:#333;font-size:12px;">Nashville Hot Lentil</p>
</div>
<div style="text-align:center;">
<img src="${images.wednesday[1]}" style="width:120px;height:100px;object-fit:cover;border-radius:8px;display:block;margin:0 auto 8px;">
<p style="margin:0;color:#333;font-size:12px;">Mediterranean Harvest</p>
</div>
<div style="text-align:center;">
<img src="${images.wednesday[2]}" style="width:120px;height:100px;object-fit:cover;border-radius:8px;display:block;margin:0 auto 8px;">
<p style="margin:0;color:#333;font-size:12px;">Thai Peanut Crunch</p>
</div>
</div>
</td></tr>
</table>
</td>
</tr>
`),
    sms_body: "⏰ Meal prep closes today at noon! order.theutopiadeli.com/catering/"
  },

  // ═══════════════════════════════════════════
  // THURSDAY — Meal Prep Reopens + Walk-Up Menu
  // ═══════════════════════════════════════════
  thursday: {
    email_subject: "🍱 Meal Prep Orders Reopen at 8PM + We're Open Today",
    email_body: wrapEmail(`
<tr>
<td>
<img src="${images.thursday[0]}" alt="Next Week's Meal Prep" class="hero-img" style="width:100%;height:300px;object-fit:cover;display:block;">
</td>
</tr>

<tr>
<td style="padding:32px 28px 20px;">
<h1 style="margin:0 0 16px;color:#590B3F;font-size:28px;line-height:1.2;">Next Week's Meal Prep Opens Tonight at 8PM 🍱</h1>
<p style="margin:0 0 20px;color:#333;font-size:16px;line-height:1.6;">
Orders reopen tonight at 8:00 PM for next week's bowls. Get your order in early — closes Wednesday at noon.
</p>
<p style="margin:0 0 24px;color:#AF3D4B;font-size:15px;font-weight:bold;">
🟢 Reopens 8:00 PM tonight · 🔴 Closes Wednesday 12:00 PM · 📦 Pickup Thursday
</p>
<a href="${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=thursday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Order Meal Prep
</a>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<h2 style="margin:0 0 16px;color:#590B3F;font-size:20px;">Walk Up Today — We're Open 🍽️</h2>
<div class="dish-grid" style="display:flex;gap:16px;flex-wrap:wrap;">

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.thursday[1]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Stek Philly</p>
<p style="margin:0;color:#888;font-size:12px;">Thin-cut steak, peppers, onions, hoagie</p>
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
style="display:inline-block;background:transparent;color:#AF3D4B;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;border:2px solid #AF3D4B;">
Walk Up Menu →
</a>
</td>
</tr>
`),
    sms_body: "🍱 Meal prep reopens tonight 8PM. Order online today 12:30-7:30. order.theutopiadeli.com"
  },

  // ═══════════════════════════════════════════
  // FRIDAY — Weekend Kickoff
  // ═══════════════════════════════════════════
  friday: {
    email_subject: "Weekend at Utopia 🍽️ Fresh Food, Good Vibes",
    email_body: wrapEmail(`
<tr>
 <td
 height="320"
 style="
 background-image:url(${images.friday[0]});
 background-size:cover;
 background-position:center 30%;
 background-repeat:no-repeat;
 "
 >
 &nbsp;
 </td>
</tr>

<tr>
<td style="padding:32px 28px 20px;">
<h1 style="margin:0 0 16px;color:#590B3F;font-size:28px;line-height:1.2;">Weekend at Utopia 🍽️</h1>
<p style="margin:0 0 20px;color:#333;font-size:16px;line-height:1.6;">
Open Friday & Saturday. Order online, get fresh food, eat happy. No prep needed — we've got you.
</p>
<p style="margin:0 0 24px;color:#AF3D4B;font-size:15px;font-weight:bold;">
Friday & Saturday · 12:30PM–7:30PM · Order online
</p>
<div style="text-align:center;">
<a href="${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=friday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;margin-right:8px;">
Order Ahead
</a>
<a href="${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=friday"
style="display:inline-block;background:transparent;color:#AF3D4B;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;border:2px solid #AF3D4B;">
Order Meal Prep or Catering
</a>
</div>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<h2 style="margin:0 0 16px;color:#590B3F;font-size:20px;">Weekend Favorites</h2>
<div class="dish-grid" style="display:flex;gap:16px;flex-wrap:wrap;">

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.friday[1]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Stek Philly</p>
<p style="margin:0;color:#888;font-size:12px;">Thin-cut steak, peppers, onions, hoagie</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.friday[2]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Loaded Bac'n Fry</p>
<p style="margin:0;color:#888;font-size:12px;">Crinkle-cut Fries Loaded with Bac'n</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.friday[3]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Chick'n Poppers</p>
<p style="margin:0;color:#888;font-size:12px;">Crispy chik'n dippers — choice of sauce: BBQ, Garlic Parm, Jerk, Buffalo, Lemon Pepper Wet</p>
</div>
</div>

<div class="dish-card" style="flex:1;background:#f8f6f4;border-radius:12px;overflow:hidden;">
 <img src="${images.friday[4]}" style="width:100%;height:140px;object-fit:cover;">
 <div style="padding:12px;">
 <p style="margin:0;color:#590B3F;font-weight:bold;font-size:14px;">Chocolate Chip Cookies</p>
 <p style="margin:0;color:#888;font-size:12px;">Two fresh-baked cookies</p>
 </div>
</div>

<div class="dish-card" style="flex:1;background:#f8f6f4;border-radius:12px;overflow:hidden;">
 <img src="${images.friday[5]}" style="width:100%;height:140px;object-fit:cover;">
 <div style="padding:12px;">
 <p style="margin:0;color:#590B3F;font-weight:bold;font-size:14px;">Cold-Pressed Juice</p>
 <p style="margin:0;color:#888;font-size:12px;">Fresh 10oz juice</p>
 </div>
</div>

</div>
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
`),
    sms_body: "Weekend at Utopia 🍽️ Order online Fri & Sat 12:30-7:30. order.theutopiadeli.com"
  },

  // ═══════════════════════════════════════════
  // SATURDAY — Weekend Reminder
  // ═══════════════════════════════════════════
  saturday: {
    email_subject: "🙌 We're Open Today! Saturday at Utopia",
    email_body: wrapEmail(`
<tr>
<td>
<img src="${images.saturday[0]}" alt="Stek Philly" class="hero-img" style="width:100%;height:300px;object-fit:cover;display:block;">
</td>
</tr>

<tr>
<td style="padding:32px 28px 20px;">
<h1 style="margin:0 0 16px;color:#590B3F;font-size:28px;line-height:1.2;">We're Open Saturday 🙌</h1>
<p style="margin:0 0 20px;color:#333;font-size:16px;line-height:1.6;">
Today 12:30PM–7:30PM. Order online, get fresh food, eat happy. No reservations needed — just bring your appetite.
</p>
<p style="margin:0 0 24px;color:#AF3D4B;font-size:15px;font-weight:bold;">
Order online welcome · Order ahead to skip the line
</p>
<a href="${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=saturday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Order Ahead
</a>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<h2 style="margin:0 0 16px;color:#590B3F;font-size:20px;">What's Cooking Today</h2>
<div class="dish-grid" style="display:flex;gap:16px;flex-wrap:wrap;">

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.saturday[0]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Stek Philly</p>
<p style="margin:0;color:#888;font-size:12px;">Thin-cut steak, peppers, onions, hoagie</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.saturday[1]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Chick'n Poppers</p>
<p style="margin:0;color:#888;font-size:12px;">Crispy dippers — BBQ, Garlic Parm, Jerk, Buffalo, Lemon Pepper</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.saturday[2]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Loaded Bac'n Fry</p>
<p style="margin:0;color:#888;font-size:12px;">Crinkle-cut fries loaded with bac'n, cheeze sauce</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.saturday[3]}" style="width:100%;height:140px;object-fit:cover;display:block;">
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
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0ece8;border-radius:12px;padding:20px;">
<tr><td style="text-align:center;">
<p style="margin:0;color:#666;font-size:14px;">🍱 Meal prep orders close Wednesday at noon · Pickup Thursday</p>
</td></tr>
</table>
</td>
</tr>

<tr>
<td style="padding:0 28px 32px;text-align:center;">
<a href="${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=saturday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Order Ahead — Skip the Line
</a>
</td>
</tr>
`),
    sms_body: "🙌 We're open today! Order online 12:30-7:30. order.theutopiadeli.com"
  },

  // ═══════════════════════════════════════════
  // SUNDAY — This Week Preview + Monday Lunch
  // ═══════════════════════════════════════════
  sunday: {
    email_subject: "📋 This Week's Meal Prep Menu + Monday Lunch",
    email_body: wrapEmail(`
<tr>
<td>
<img src="${images.sunday[0]}" alt="This Week's Meal Prep" class="hero-img" style="width:100%;height:300px;object-fit:cover;display:block;">
</td>
</tr>

<tr>
<td style="padding:32px 28px 20px;">
<h1 style="margin:0 0 16px;color:#590B3F;font-size:28px;line-height:1.2;">This Week's Meal Prep Menu 🍱</h1>
<p style="margin:0 0 20px;color:#333;font-size:16px;line-height:1.6;">
Next week's bowls are here. Orders close Wednesday at noon — pickup Thursday.
</p>
<p style="margin:0 0 24px;color:#AF3D4B;font-size:15px;font-weight:bold;">
🟢 Orders open Thursday 8:00 PM · 🔴 Close Wednesday 12:00 PM · 📦 Pickup Thursday
</p>
<a href="${baseURL}/catering/?utm_source=email&utm_medium=campaign&utm_campaign=sunday"
style="display:inline-block;background:#AF3D4B;color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;">
Order Meal Prep
</a>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<h2 style="margin:0 0 16px;color:#590B3F;font-size:20px;">Get Lunch Monday 🥪</h2>
<p style="margin:0 0 16px;color:#666;font-size:15px;">We're open Monday for walk-ups. Start your week right:</p>
<div class="dish-grid" style="display:flex;gap:16px;flex-wrap:wrap;">

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.sunday[1]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Stek Philly</p>
<p style="margin:0;color:#888;font-size:12px;">The sandwich that built our reputation</p>
</div>
</div>

<div class="dish-card" style="flex:1;min-width:160px;background:#f8f6f4;border-radius:12px;overflow:hidden;">
<img src="${images.sunday[2]}" style="width:100%;height:140px;object-fit:cover;display:block;">
<div style="padding:12px;">
<p style="margin:0 0 4px;color:#590B3F;font-weight:bold;font-size:14px;">Chick'n Poppers</p>
<p style="margin:0;color:#888;font-size:12px;">5 sauces, unlimited flavor</p>
</div>
</div>

</div>
</td>
</tr>

<tr>
<td style="padding:0 28px 24px;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f6f4;border-radius:12px;padding:20px;">
<tr><td>
<h3 style="margin:0 0 12px;color:#590B3F;font-size:16px;">Meal Prep Schedule</h3>
<p style="margin:0 0 8px;color:#333;font-size:14px;line-height:1.5;">🟢 Orders open Thursday 8:00 PM</p>
<p style="margin:0 0 8px;color:#333;font-size:14px;line-height:1.5;">🔴 Orders close Wednesday 12:00 PM</p>
<p style="margin:0;color:#333;font-size:14px;line-height:1.5;">📦 Pickup Thursday 12:30 PM – 7:30 PM</p>
</td></tr>
</table>
</td>
</tr>

<tr>
<td style="padding:0 28px 32px;text-align:center;">
<a href="${baseURL}/pickup-order/?utm_source=email&utm_medium=campaign&utm_campaign=sunday"
style="display:inline-block;background:transparent;color:#AF3D4B;padding:14px 32px;border-radius:10px;text-decoration:none;font-size:16px;font-weight:bold;border:2px solid #AF3D4B;">
Walk Up Menu →
</a>
</td>
</tr>
`),
    sms_body: "📋 This week's meal prep menu is live. order.theutopiadeli.com/catering/"
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
