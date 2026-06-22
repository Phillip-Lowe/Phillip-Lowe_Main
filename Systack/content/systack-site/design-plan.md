# Systack.net Visual Overhaul Plan

## Current Issues

| Issue | Where | Fix |
|-------|-------|-----|
| No actual logo image | Nav + hero header | Add SVG logo (designed, ready) |
| Nav logo too small / no image | `.nav-logo` is text-only | Add logo image, scale nav |
| Hero brand header has `.brand-mark` with no image | `header` section | Add logo, fix proportions |
| Inconsistent spacing | CSS variables | Audit + tighten |
| No favicon | Browser tab | Add favicon link |
| No meta description | SEO | Add `<meta name="description">` |
| No Open Graph tags | Social sharing | Add OG meta tags |
| "Stop Losing Customers to Phone Tag" vs site name mismatch | Hero h1 | Verify content matches brand |

## Changes

### 1. Add Brand Logo SVG
- File: `brand/logo.svg` (created)
- Add to nav: `img` inside `.nav-logo`
- Add to header: `img` inside `.brand-mark`
- Scale: 40px nav, 56px header
- Ensure `object-fit: cover` so SVG renders crisp

### 2. Fix Nav Layout
- `.nav-logo` currently has no image, just text
- Add: `.nav-logo-img { width: 40px; height: 40px; }` with SVG
- `.nav-logo-text` stays at 24px

### 3. Fix Header Layout
- `.brand-mark` currently empty div, no image
- Add: `.brand-mark img { width: 56px; height: 56px; }` with SVG
- `.brand-name` stays at 36px, gap 16px

### 4. Favicon
- Add `<link rel="icon" type="image/svg+xml" href="brand/logo.svg">`
- Fallback: `<link rel="icon" type="image/png" href="brand/logo.png">` (future)

### 5. Meta Tags
```html
<meta name="description" content="Automated booking and payment systems for service businesses. Turn missed calls into confirmed bookings in 60 seconds.">
<meta property="og:title" content="Systack.net — Automated Booking & Payment Systems">
<meta property="og:description" content="Stop losing customers to phone tag. Your customers want to book and pay online — in under 60 seconds.">
<meta property="og:url" content="https://systack.net">
<meta property="og:type" content="website">
```

### 6. Consistency Pass
- Verify `{{PHONE_E164}}` and `{{PHONE_DISPLAY}}` are consistent
- Verify brand name capitalization (SyStack vs Systack) everywhere
- Hero line-height: `1.15` should be `1.2` for better readability
- CTA button padding: ensure minimum 44px touch target (mobile)

## File Targets
| File | Action |
|------|--------|
| `index.html` | Add logo, favicon, meta tags, fix CSS proportions |
| `templates/template-landing.html` | Same changes |
| `niches/services/index.html` | Same changes |
| `niches/food/index.html` | Same changes |
| `brand/logo.svg` | ✅ Already created |

## Estimated Time
- 15 min to edit all HTML files
- 5 min to test deploy
- 20 min total
