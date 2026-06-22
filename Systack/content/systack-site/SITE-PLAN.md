# Systack Site Overhaul Plan

## User's Requirements

1. **Real homepage** — Not just a booking page, something that introduces the business
2. **Personal AI Agent service** — For regular people who want their own agent but don't want technical setup
3. **No technical complexity for clients** — They shouldn't have to deal with setup
4. **Case studies** — Use Utopia Deli and other real work we've done
5. **Demo strategy** — Generic demo (not exposing specific client data), but can show real case studies
6. **No fake testimonials** — Only real ones, or none for now

## What "Becoming Serious" Means Here

The user wants to avoid looking like a "vibe coder" selling toy apps. The site needs to signal:
- Real business with real systems
- Professional delivery (not "built in a weekend")
- Actual client work (Utopia Deli)
- Services for both businesses AND individuals

## Site Structure Plan

### Homepage
- Hero: What we do (systems + agents)
- Two clear paths: "Business Systems" | "Personal Agent"
- Brief credibility: years, clients served, systems running
- Call to action: consultation booking

### Business Systems Page
- What: booking systems, payment flows, automation
- Proof: Utopia Deli case study (real metrics)
- Demo: generic booking form (not client data)
- Pricing: clear tiers

### Personal Agent Page (NEW)
- What: your own AI agent that handles tasks
- Who: busy professionals, creators, anyone who needs help
- How: we set it up, you use it, no technical knowledge needed
- Pricing: monthly service

### Case Studies / Work Page
- Utopia Deli: order system, payment processing, notifications
- Metrics: orders processed, time saved, etc.
- Screenshots (with permission or anonymized)

### Contact / Consultation
- Real booking form (not just mailto)
- Calendar integration
- Discovery call scheduling

## What to Fix Now

1. **Homepage rewrite** — separate from booking demo
2. **Add Personal Agent service page** — completely new
3. **Case study page for Utopia Deli** — real project, real outcomes
4. **Generic demo** — simple booking form for show
5. **Remove fake testimonials** — add real ones when we have them
6. **Contact form** — actual form, not just email link

## Technical Notes

- Keep existing CSS framework (systack.css)
- Reuse components where possible
- Mobile responsive throughout
- Fast load, clean code

## Files to Create/Edit

- `index.html` — major rewrite
- `personal-agent/index.html` — new service page
- `work/index.html` — case studies (Utopia Deli)
- `demo/booking.html` — generic demo form
- `contact.html` — real contact form
- Update navigation across all pages
