# Systack Template System

## How It Works

One master template (`template-landing.html`) with `{{VARIABLE}}` markers.
Swap the variables → your niche-specific landing page is ready.
Same design, same pricing, industry-specific language.

---

## Quick Start (60 seconds)

### 1. Pick a niche folder or create one
```
niches/food/      → Restaurants, food trucks, delis
niches/services/  → Salons, auto shops, cleaning, etc.
niches/[new]/     → Any new vertical
```

### 2. Copy the template
```bash
cp templates/template-landing.html niches/[your-niche]/index.html
```

### 3. Open the file and replace all `{{VARIABLE}}` markers
Use find-and-replace. Every variable is documented below.

### 4. Deploy
Each niche folder is a self-contained site. Push to a GitHub Pages repo
or drop into any static host.

---

## Variable Reference

### Brand & Identity
| Variable | What It Is | Example (Services) | Example (Food) |
|----------|-----------|-------------------|----------------|
| `{{SITE_TITLE}}` | Browser tab title | `Systack.net — Automated Booking` | `Systack.net — Direct Online Ordering` |
| `{{BRAND_TEXT}}` | Logo text in nav + header | `SyStack.net` | `SyStack.net` |
| `{{BRAND_TAGLINE}}` | One-line description under logo | `Automated Booking & Payment Systems for Any Business` | `Direct Online Ordering. No Platform Fees.` |
| `{{FOOTER_BRAND}}` | Brand in footer | `SyStack.net` | `SyStack.net` |
| `{{FOOTER_TAGLINE}}` | Footer tagline | `Automated Booking & Payment Systems` | `Direct Online Ordering for Restaurants` |

### Hero Section
| Variable | What It Is | Example (Services) | Example (Food) |
|----------|-----------|-------------------|----------------|
| `{{LOSS_WHAT}}` | What they're losing | `Customers` | `Revenue` |
| `{{PAIN_POINT}}` | The enemy (highlighted text) | `Phone Tag` | `Platform Fees` |
| `{{HERO_SUB}}` | Sub-headline value prop | `Your customers want to book and pay. Right now.` | `Your customers want to order directly from you.` |
| `{{HERO_PAIN}}` | Pain point description | `Turn your services into an instant booking system` | `Turn your menu into a direct ordering system` |

### Phone
| Variable | What It Is | Example |
|----------|-----------|---------|
| `{{PHONE_E164}}` | Phone in E.164 format (for tel: links) | `15012746231` |
| `{{PHONE_DISPLAY}}` | Formatted phone for display | `(501) 274-6231` |
| `{{SMS_KEYWORD}}` | Text keyword to trigger callback | `BOOKING SYSTEM` |

### Who This Is For
| Variable | What It Is | Example |
|----------|-----------|---------|
| `{{WHO_HEADLINE}}` | Section headline | `If You Take Bookings or Payments, This Works For You` |
| `{{#BIZ_CARDS}}...{{/BIZ_CARDS}}` | Mustache loop — each card has `emoji`, `name`, `detail` | 16 cards in the generic version |

*Note: The template uses Mustache-style loops for lists. If you don't want to use a template engine, just copy-paste the HTML block and edit each card manually.*

### Friction / Before-After
| Variable | What It Is |
|----------|-----------|
| `{{FRICTION_HEADLINE}}` | `The Hidden Cost of Phone Tag` |
| `{{FRICTION_SUB}}` | Supporting sub-text |
| `{{BEFORE_LABEL}}` | `Manual Booking` |
| `{{AFTER_LABEL}}` | `SyStack System` |
| `{{#BEFORE_ITEMS}}` | List: pain points of current process |
| `{{#AFTER_ITEMS}}` | List: how SyStack fixes each one |

### Platform vs Direct
| Variable | What It Is |
|----------|-----------|
| `{{PLATFORM_NOTE}}` | Purple box note about existing platforms |
| `{{PLATFORM_HEADLINE}}` | `Platform Fees Are a Forever Tax` |
| `{{PLATFORM_SUB}}` | Describes the comparison |
| `{{PLATFORM_BEFORE_TITLE}}` | `Platform Booking — $100 Service` |
| `{{PLATFORM_AFTER_TITLE}}` | `SyStack Direct — $100 Service` |

### Demo Mockup
| Variable | What It Is |
|----------|-----------|
| `{{DEMO_TYPE}}` | `Booking` or `Ordering` |
| `{{DEMO_TITLE}}` | `Booking Summary` or `Order Summary` |
| `{{DEMO_BUSINESS}}` | Placeholder business name |
| `{{DEMO_TOTAL_LABEL}}` | `Total (with deposit)` or `Order Total` |
| `{{DEMO_TOTAL}}` | Price |
| `{{DEMO_FOOTER}}` | Description of what happens next |

### Features
| Variable | What It Is |
|----------|-----------|
| `{{FEATURES_HEADLINE}}` | `More Than a Form — A Revenue System` |
| `{{FEATURES_SUB}}` | Supporting text |

### Pricing
| Variable | What It Is | Example |
|----------|-----------|---------|
| `{{TRANSACTION_UNIT}}` | `bookings` or `orders` |
| `{{FORM_TYPE}}` | `booking form` or `ordering page` |
| `{{LOG_TYPE}}` | `Booking log` or `Order log` |
| `{{SCHEDULING_FEATURE}}` | `Time slot management` or `Menu management` |

### Testimonials
Use `{{#TESTIMONIALS}}...{{/TESTIMONIALS}}` loop. Each has `quote` and `attribution`.

### Final CTA
| Variable | What It Is |
|----------|-----------|
| `{{FINAL_HEADLINE}}` | `Ready to Stop Losing Customers?` |

---

## Folder Structure

```
systack-site/
├── index.html                  ← LIVE: generic services (deployed to systack.net)
├── templates/
│   ├── template-landing.html   ← Master template with {{VARIABLES}}
│   ├── template-sales.md       ← Sales one-pager template (future)
│   └── README.md               ← This file
├── niches/
│   ├── food/                   ← Restaurant/deli/food truck version
│   │   ├── index.html
│   │   └── sales.md
│   └── services/               ← General service version
│       ├── index.html
│       └── sales.md
├── brand/                      ← Logos, colors, assets
└── README.md                   ← Project overview
```

---

## Pro Tips

- **Clone for a pitch:** `cp -r niches/services niches/salon-pitch` → customize → deploy to a subdomain or separate repo
- **A/B test:** Deploy two variants to different subdomains, track which converts
- **Seasonal:** Clone, swap holiday-specific copy, deploy
- **Track source:** Add `?ref=linkedin` etc. to CTA links for attribution
