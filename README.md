# Utopia Deli — Online Order Page

A beautiful, mobile-first online ordering page for **The Utopia Deli** in Little Rock, AR.

Built to be **productized** — every brand-specific detail lives in `config.js`, so this same codebase can be white-labeled for any food truck, deli, or small restaurant.

---

## 🌐 Live Site

**https://order.theutopiadeli.com**

---

## 📁 File Structure

```
utopia-deli-order/
├── index.html          ← Main order page (generic, reads from config.js)
├── config.js           ← 🔧 ALL brand-specific values (edit this to rebrand)
├── menu-data.js        ← Menu items, modifiers, prices
├── CNAME               ← Custom domain (GitHub Pages)
├── images/
│   ├── logo.png        ← Replace with your logo
│   └── *.jpg / *.webp  ← Product photos
└── README.md           ← This file
```

---

## 🚀 Quick Start (For a New Business)

1. **Fork this repo** (or clone and push to your own)
2. **Edit `config.js`** — replace name, colors, phone, hours, checkout endpoint
3. **Replace images** in `images/` folder — logo, product photos
4. **Edit `menu-data.js`** — your menu items, modifiers, prices
5. **Update `CNAME`** — your custom domain (e.g. `order.yourbusiness.com`)
6. **Enable GitHub Pages** — Settings → Pages → Source: `main`, Folder: `/ (root)`
7. **Add DNS CNAME** at your registrar — `order` → `your-username.github.io`
8. **Wait 5-15 minutes** for HTTPS to provision

---

## ⚙️ Configuration (`config.js`)

Everything brand-specific is in one file:

```js
const BRAND = {
  name:     "Your Business Name",
  tagline:  "Your catchy tagline",
  phone:    "(555) 123-4567",
  email:    "order@yourbusiness.com",
  logo:     "images/logo.png",
  colors: {
    primary:      "#your-color",
    accent:       "#your-cta-color",
    secondary:    "#your-secondary",
    gold:         "#your-highlight",
  },
  hours: {
    timezone:  "America/Chicago",
    openDays:  [1,2,3,4,5,6],     // Mon-Sat
    openTime:  { hour: 11, minute: 0 },
    closeTime: { hour: 20, minute: 0 },
  },
  checkout: {
    endpoint: "https://your-checkout-server.com/checkout",
  },
};
```

---

## 🛒 How It Works

| Step | What Happens |
|---|---|
| 1. Customer browses | Menu renders from `menu-data.js` with photos, prices, modifiers |
| 2. Customer builds order | Taps items, selects modifiers (sauces, extras, combos), adds to cart |
| 3. Customer checks out | Fills name, email, phone, pickup time, notes |
| 4. Order is sent | POST to `BRAND.checkout.endpoint` (your n8n webhook or server) |
| 5. Backend handles it | Creates Square payment link → emails customer → stores in database |
| 6. Customer pays | Clicks Square link in email → completes payment → order confirmed |

---

## 🔌 Backend Integration

This frontend is **backend-agnostic**. It expects a single POST endpoint that accepts:

```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "(555) 123-4567",
  "pickup_time": "12:45 PM",
  "notes": "Extra napkins please",
  "cart": [...],
  "total_cents": 2650,
  "frontend_total_cents": 2650
}
```

And returns:
```json
{
  "ok": true,
  "message": "Order received!",
  "square_link": "https://checkout.square.link/..."
}
```

### Compatible Backends
- **n8n webhook** (what Utopia Deli uses)
- **Custom checkout server** (Python/Node/whatever)
- **Zapier / Make / Pipedream**
- Any HTTP endpoint that accepts JSON and returns `{ok, message, square_link}`

---

## 🎨 Design System

| Element | Default | Override |
|---|---|---|
| Primary color | `#590B3F` (deep plum) | `BRAND.colors.primary` |
| CTA / accent | `#AF3D4B` (rose) | `BRAND.colors.accent` |
| Highlight | `#D59F5C` (gold) | `BRAND.colors.gold` |
| Font | Open Sans (Google Fonts) | Edit `<link>` in `index.html` |
| Border radius | 14px | Edit CSS vars in `index.html` |
| Shadows | Soft, layered | Edit CSS vars in `index.html` |

---

## 📱 Mobile-First

- Designed for **phone ordering** (the primary use case)
- Sticky header with cart
- One-tap modifier selection
- Collapsible cart drawer
- Touch-friendly 44px+ tap targets

---

## 🔒 HTTPS & Security

- Hosted on **GitHub Pages** (free HTTPS via Let's Encrypt)
- No server-side code in the repo
- No secrets or credentials in the frontend
- Payment handled by **Square** (PCI compliant)

---

## 🏢 White-Label License

This codebase is built to be **forked and sold**.

For each new client:
1. Fork this repo
2. Edit `config.js` + `menu-data.js` + images
3. Deploy to client's GitHub or your own org
4. Charge setup + monthly maintenance

---

## 📞 Support

Built by **[Systack, LLC](https://systack.net)** for The Utopia Deli.

For white-label inquiries or customizations:
- Email: `green@systack.net`
- Phone: `(501) 555-0199`

---

## 📝 Changelog

| Date | Change |
|---|---|
| 2026-05-14 | Initial build — Netlify hosting, inline menu |
| 2026-05-16 | Menu extracted to `menu-data.js`, modifiers system added |
| 2026-05-18 | Checkout server built, tunnel routing fixed |
| 2026-05-20 | Email confirmations, admin dashboard, n8n audit |
| 2026-05-21 | Logo styling tweaks |
| 2026-05-25 | **Migrated to GitHub Pages**, config.js brand separation, productization prep |

---

*This is a living document. Last updated: 2026-05-25*
