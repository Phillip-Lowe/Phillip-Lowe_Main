---
name: site-deployer
description: "Deploy static HTML/CSS/JS sites to Netlify with custom domain, SSL, and branded styling. Handles build, upload, DNS, and verification."
---

# Site Deployer

Deploy static HTML/CSS/JS sites to Netlify with custom domains. Zero-config hosting with automatic SSL, CDN, and instant deploys.

## When to Use
- Client needs a landing page, booking form, or information site
- Demos and proof-of-concepts
- Internal tools and dashboards
- Any static HTML site that needs a public URL

## Quick Deploy

```bash
# Install netlify-cli if needed
npm install -g netlify-cli

# Login (one-time)
netlify login

# Deploy current directory
netlify deploy --prod --dir .

# With custom domain
netlify deploy --prod --dir . --site=my-site-slug
```

## Branded Site Structure

```
site/
├── index.html              # Landing page
├── about.html              # About section
├── services.html           # Services grid
├── contact.html            # Contact form
├── privacy.html            # Privacy policy
├── assets/
│   ├── css/
│   │   └── systack.css     # Brand stylesheet
│   ├── js/
│   │   └── main.js         # Shared scripts
│   └── images/
│       └── logo.png        # Brand assets
└── _redirects              # URL redirects
```

## SyStack Brand CSS

Include in all pages:
```html
<link rel="stylesheet" href="assets/css/systack.css?v=14">
```

Cache-bust with version param when updating:
```bash
# Increment version in all HTML files
sed -i '' 's/v=13/v=14/g' *.html
```

## Netlify Config

`_redirects` file:
```
# Clean URLs
/catering/    /catering/index.html    200
/pickup-order/ /pickup-order/index.html 200

# SPA fallback (if using JS routing)
/*    /index.html   200
```

`netlify.toml` (optional):
```toml
[build]
  publish = "."

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
```

## Custom Domain

1. **Add domain in Netlify dashboard**:
   - Site settings → Domain management → Add custom domain
   - Enter: `client.systack.net`

2. **DNS Configuration**:
   - Netlify DNS: Point NS records to Netlify
   - External DNS: Add CNAME `client` → `site-name.netlify.app`

3. **SSL**:
   - Netlify provisions Let's Encrypt automatically
   - Force HTTPS in site settings

## Domain Strategy

| Client Type | Domain Pattern |
|-------------|---------------|
| Main business | `systack.net` |
| Demo/landing | `demo.systack.net` |
| Client site | `client-name.systack.net` |
| Order form | `order.client-domain.com` |
| Agent portal | `agent.systack.net` |

## Deployment Checklist

- [ ] All pages link correctly (relative paths)
- [ ] Images/assets load on all pages
- [ ] Mobile responsive (test with browser dev tools)
- [ ] Forms submit to correct webhook URL
- [ ] Privacy policy linked in footer
- [ ] Custom domain configured
- [ ] SSL certificate active
- [ ] 404 page exists
- [ ] Favicon set
- [ ] Meta tags for SEO (title, description, OG tags)

## Navigation Consistency

All pages must have identical nav and footer:

```html
<nav class="main-nav">
  <a href="index.html">Home</a>
  <a href="services.html">Services</a>
  <a href="pricing.html">Pricing</a>
  <a href="contact.html">Contact</a>
</nav>

<footer>
  <p>© 2026 SyStack. Built for your business.</p>
  <a href="privacy.html">Privacy Policy</a>
</footer>
```

## Linking Between Sites

```html
<!-- From systack.net to order form -->
<a href="https://order.theutopiadeli.com/pickup-order/" target="_blank">
  Try Live Demo →
</a>

<!-- From order form back to main site -->
<a href="https://systack.net">Powered by SyStack</a>
```

## Verification

After deploy:
1. Visit site on custom domain
2. Check SSL lock icon
3. Test all navigation links
4. Submit test form
5. Verify mobile view
6. Run Lighthouse audit (target: 90+)

## Common Issues

| Issue | Fix |
|-------|-----|
| CSS not loading | Check cache-bust version matches uploaded file |
| Images 404 | Ensure relative paths correct for subdirectory pages |
| Form submission failing | Verify webhook URL is HTTPS |
| Old version showing | Clear browser cache, check Netlify deploy |
| Custom domain not resolving | Wait 24-48h for DNS propagation |

## Reference

- SyStack site: `systack-site/`
- Utopia Deli order form: `pickup-order/`
- Catering form: `catering/`
- Brand CSS: `systack-site/assets/css/systack.css`
