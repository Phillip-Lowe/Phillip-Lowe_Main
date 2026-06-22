# SyStack.net Site Schema v1.0

## Overview

| Property | Value |
|----------|-------|
| Primary Domain | `https://systack.net` |
| Fallback / Origin | `https://phillip-lowe.github.io/systack-site` |
| Platform | GitHub Pages (Cloudflare DNS) |
| Build Type | Static HTML |
| Brand Name | SyStack.net |
| Tagline | "Automated Booking & Payment Systems for Any Business" |
| Phone | (501) 274-6231 |
| Phone E.164 | `+15012746231` |

---

## File Structure (Canonical)

```
systack-site/
├── index.html                          # 🎯 MAIN: Generic services landing
├── CNAME                               # GitHub Pages custom domain
│   └── Contents: "systack.net"
├── README.md                           # Repository documentation
│
├── brand/
│   └── logo.svg                        # Brand logo (hexagon stack, cyan gradient)
│
├── templates/
│   ├── template-landing.html           # Master template with {{VARIABLES}}
│   └── README.md                       # Customization guide
│
└── niches/
    ├── food/
    │   ├── index.html                  # Restaurant / deli / food truck variant
    │   └── sales.md                    # One-pager for food businesses
    └── services/
        ├── index.html                  # Generic service business variant
        └── sales.md                    # One-pager for service businesses
```

---

## Component Schema

### 1. Global Head Elements (All Pages)

```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{{META_DESCRIPTION}}">
<meta property="og:title" content="{{OG_TITLE}}">
<meta property="og:description" content="{{OG_DESCRIPTION}}">
<meta property="og:url" content="{{OG_URL}}">
<meta property="og:type" content="website">
<link rel="icon" type="image/svg+xml" href="brand/logo.svg">
<title>{{PAGE_TITLE}}</title>
```

### 2. Navigation Bar

```html
<nav>
  <div class="nav-logo">
    <img src="brand/logo.svg" alt="Systack" class="nav-logo-img">
    <div class="nav-logo-text">Sy<span>Stack</span>.net</div>
  </div>
  <a href="tel:{{PHONE_E164}}" class="nav-cta">📞 Get Started</a>
</nav>
```

**CSS Specs:**
| Element | Size | Properties |
|---------|------|------------|
| `.nav-logo-img` | 40×40px | border-radius: 10px, object-fit: cover |
| `.nav-logo-text` | 24px, weight 800 | color: var(--navy), letter-spacing: -0.5px |
| `.nav-cta` | padding 10×22px | background: var(--cyan), border-radius: 8px |

### 3. Header / Brand Block

```html
<header>
  <div class="brand">
    <div class="brand-mark">
      <img src="brand/logo.svg" alt="Systack">
    </div>
    <div class="brand-text">
      <div class="brand-name">Sy<span>Stack</span>.net</div>
      <div class="brand-tagline">{{TAGLINE}}</div>
    </div>
  </div>
</header>
```

**CSS Specs:**
| Element | Size | Properties |
|---------|------|------------|
| `.brand-mark` | 56×56px | border-radius: 14px, box-shadow, overflow: hidden |
| `.brand-mark img` | 100% | object-fit: cover |
| `.brand-name` | 36px, weight 800 | color: var(--navy), span color: var(--cyan) |
| `.brand-tagline` | 15px | color: var(--gray-600) |

### 4. Hero Section

```html
<div class="hero">
  <h1>{{HEADLINE_LINE1}}<br>to <span class="highlight">{{HEADLINE_HIGHLIGHT}}</span></h1>
  <p class="hero-sub">{{HERO_SUBTITLE}}</p>
  <p class="hero-pain">{{HERO_DESCRIPTION}}</p>
  <a href="tel:{{PHONE_E164}}" class="cta-btn">📞 Call to Get Started</a>
  <a href="#pricing" class="cta-secondary">See Plans & Pricing</a>
</div>
```

**CSS Specs:**
| Element | Size | Properties |
|---------|------|------------|
| `.hero` | padding 60px | background: var(--navy), border-radius: 16px |
| `h1` | 40px, weight 800 | line-height: 1.2, color: white |
| `.highlight` | inherit | color: var(--cyan-bright) |
| `.cta-btn` | padding 16×32px | background: white, color: var(--navy) |
| `.cta-secondary` | padding 16×32px | border: 2px solid rgba(255,255,255,0.4) |

### 5. Social Proof / Testimonial

```html
<div class="testimonial">
  <blockquote>"{{TESTIMONIAL_QUOTE}}"</blockquote>
  <cite>— {{TESTIMONIAL_BUSINESS}}, {{TESTIMONIAL_LOCATION}}</cite>
</div>
```

**CSS Specs:**
| Element | Properties |
|---------|------------|
| `.testimonial` | background: var(--gray-100), border-left: 4px solid var(--cyan), padding: 40px |
| `blockquote` | font-size: 20px, italic |
| `cite` | font-size: 14px, weight 600, color: var(--gray-600) |

### 6. Pricing Section

```html
<div class="section" id="pricing">
  <h2>Pick the Plan That Matches Your Day</h2>
  <div class="pricing-table">
    <div class="pricing-card">
      <h3>{{TIER_1_NAME}}</h3>
      <div class="price">${{TIER_1_PRICE}}</div>
      <div class="who">{{TIER_1_AUDIENCE}}</div>
      <ul><!-- features --></ul>
      <p>Setup: ${{TIER_1_SETUP}}</p>
    </div>
    <div class="pricing-card featured">
      <div class="best-value">BEST VALUE</div>
      <h3>{{TIER_2_NAME}}</h3>
      <div class="price">${{TIER_2_PRICE}}</div>
      <!-- ... -->
    </div>
    <div class="pricing-card">
      <h3>{{TIER_3_NAME}}</h3>
      <div class="price">${{TIER_3_PRICE}}</div>
      <!-- ... -->
    </div>
  </div>
</div>
```

**CSS Specs:**
| Element | Properties |
|---------|------------|
| `.pricing-table` | grid, gap: 20px, auto-fit minmax(260px, 1fr) |
| `.pricing-card` | padding: 30px, border: 2px solid var(--gray-200) |
| `.pricing-card.featured` | border-color: var(--navy), background: var(--gray-50) |
| `.price` | 36px, weight 800, color: var(--navy) |
| `.best-value` | absolute positioned badge, background: var(--navy), color: white |

### 7. Risk Killers (Trust Signals)

```html
<div class="risk-killers">
  <div class="risk-killer"><span class="check">✓</span> No contract</div>
  <div class="risk-killer"><span class="check">✓</span> Cancel anytime</div>
  <div class="risk-killer"><span class="check">✓</span> Live in 2–3 days</div>
  <div class="risk-killer"><span class="check">✓</span> Pays for itself in one busy week</div>
</div>
```

### 8. Final CTA

```html
<div class="final-cta">
  <h2>Ready to {{CTA_HEADLINE}}?</h2>
  <p>{{CTA_DESCRIPTION}}</p>
  <div class="phone">📞 {{PHONE_DISPLAY}}</div>
  <p>Or text "{{CTA_KEYWORD}}" and we'll call you back.</p>
  <a href="tel:{{PHONE_E164}}" class="cta-btn">Call Now — Let's Talk</a>
</div>
```

### 9. Footer

```html
<footer>
  <img src="brand/logo.svg" alt="Systack" style="width:40px;height:40px;">
  <p>SyStack.net — {{TAGLINE_SHORT}}</p>
  <p>Built by operators for operators.</p>
</footer>
```

---

## Color System (CSS Variables)

| Variable | Value | Usage |
|----------|-------|-------|
| `--navy` | `#001a2d` | Dark backgrounds, primary text |
| `--navy-light` | `#002845` | Gradients, hover states |
| `--teal` | `#007da9` | Secondary accent |
| `--cyan` | `#00a1db` | Primary accent, CTAs |
| `--cyan-bright` | `#00c5e0` | Highlights, spans |
| `--white` | `#ffffff` | Text on dark, backgrounds |
| `--gray-50` | `#f8fafc` | Light backgrounds |
| `--gray-100` | `#f1f5f9` | Cards, sections |
| `--gray-200` | `#e2e8f0` | Borders |
| `--gray-400` | `#94a3b8` | Secondary text |
| `--gray-600` | `#475569` | Body text |
| `--gray-800` | `#1e293b` | Headings |
| `--green` | `#22c55e` | Success, checks |
| `--red` | `#ef4444` | Error, before-states |

---

## Brand Logo Specs

| Property | Value |
|----------|-------|
| Format | SVG |
| ViewBox | `0 0 80 80` |
| Primary Shape | Hexagon stack (outer + inner + center S) |
| Primary Gradient | `#00c5e0` → `#00a1db` → `#007da9` |
| Stroke | `#001a2d` (3px outer, 2.5px inner) |
| Center Element | White hexagon "S" shape |
| Shadow | `0 4px 16px rgba(0,161,219,0.3)` |

**Usage Locations:**
| Location | Size | Border Radius |
|----------|------|---------------|
| Nav bar | 40×40px | 10px |
| Header | 56×56px | 14px |
| Footer | 40×40px | 10px |
| Favicon | Browser default | N/A |

---

## Page Variants (Niche Mapping)

| Niche | File | Headline | Tagline | Audience |
|-------|------|----------|---------|----------|
| **Generic / Services** | `index.html` | "Stop Losing Customers to Phone Tag" | "Automated Booking & Payment Systems for Any Business" | All service businesses |
| **Food / Restaurants** | `niches/food/index.html` | "Stop Losing Orders to Chaos" | "Business Systems, Automated" | Delis, food trucks, restaurants |
| **Template** | `templates/template-landing.html` | `{{HEADLINE}}` | `{{TAGLINE}}` | Custom |

---

## Template Variables (templates/template-landing.html)

| Variable | Description | Example |
|----------|-------------|---------|
| `{{SITE_TITLE}}` | Browser title | "SyStack.net" |
| `{{META_DESCRIPTION}}` | SEO description | "Automated booking..." |
| `{{OG_TITLE}}` | Social share title | "SyStack.net — Automated Booking" |
| `{{OG_URL}}` | Canonical URL | "https://systack.net" |
| `{{PHONE_E164}}` | Tel link format | "+15012746231" |
| `{{PHONE_DISPLAY}}` | Human readable | "(501) 274-6231" |
| `{{TAGLINE}}` | Full tagline | "Automated Booking & Payment Systems..." |
| `{{HEADLINE_LINE1}}` | H1 first line | "Stop Losing Customers" |
| `{{HEADLINE_HIGHLIGHT}}` | H1 highlighted word | "Phone Tag" |
| `{{HERO_SUBTITLE}}` | Hero paragraph 1 | "Your customers want to book..." |
| `{{HERO_DESCRIPTION}}` | Hero paragraph 2 | "Turn your services into..." |
| `{{TIER_1_NAME}}` | Pricing tier 1 | "Solo Operator" |
| `{{TIER_1_PRICE}}` | Monthly price | "149" |
| `{{TIER_1_SETUP}}` | Setup fee | "1,500" |
| `{{TIER_1_AUDIENCE}}` | Who it's for | "Less than 20 bookings/week..." |
| `{{TESTIMONIAL_QUOTE}}` | Customer quote | "During lunch rush we were..." |
| `{{TESTIMONIAL_BUSINESS}}` | Business name | "Utopia Deli" |
| `{{TESTIMONIAL_LOCATION}}` | City, State | "Little Rock, AR" |
| `{{CTA_HEADLINE}}` | Final CTA headline | "Stop Losing Orders" |
| `{{CTA_KEYWORD}}` | Text keyword | "ORDER SYSTEM" / "BOOKING" |
| `{{NICHE_LIST}}` | 16 business types | 💇 Salon, 🚗 Auto Shop, etc. |

---

## Responsive Breakpoints

| Breakpoint | CSS Rule | Changes |
|------------|----------|---------|
| Mobile | `max-width: 768px` | Single column, reduced padding, smaller fonts |
| Tablet | `768px - 1024px` | 2-column grids, medium padding |
| Desktop | `min-width: 1024px` | Full layout, max-width: 960px container |

---

## Deployment Specs

| Property | Value |
|----------|-------|
| Source | GitHub (`Phillip-Lowe/systack-site`) |
| Branch | `main` |
| Build | Static (no build step) |
| DNS | Cloudflare (nameservers) |
| SSL | GitHub Pages + Cloudflare (Full/Strict) |
| Cache | GitHub Pages CDN (max-age: 600) |
| Custom Domain | `systack.net` (CNAME file required) |

---

## Verification Checklist

After any change, verify:

- [ ] `https://systack.net` resolves (not `phillip-lowe.github.io`)
- [ ] `https://systack.net/brand/logo.svg` loads (HTTP 200)
- [ ] All `tel:` links use `+15012746231` format
- [ ] All pages have `<meta name="description">`
- [ ] All pages have OG tags
- [ ] Pricing tiers match current offering
- [ ] Footer logo renders correctly (not squished)
- [ ] Nav logo renders correctly (40×40px)
- [ ] Header brand-mark renders correctly (56×56px)
- [ ] Mobile view: no horizontal scroll, touch targets ≥44px
- [ ] All internal links (`#pricing`, `#has-dd`, etc.) work

---

## Changelog

| Date | Version | Change |
|------|---------|--------|
| 2026-05-09 | v1.0 | Schema created, logo added, Cloudflare migration |

---

**Canonical Source:** `~/.openclaw/workspaces/sol/systack-site/SITE_SCHEMA.md`
**Last Updated:** 2026-05-09
**Owner:** Phillip Lowe / Green
