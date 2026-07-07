# Trust Center Link Fix — 2026-07-07 01:20 CDT

## Problem
Trust Center PDF links on systack.net pointed to `command.systack.net/download/trust-center` which returned 404.

## Root Cause
The Trust Center PDF is served from the Customer Portal (port 8768), not the Command Center (port 8770). The correct URL is `portal.systack.net/download/trust-center`.

## Files Fixed
- `Systack/content/systack-site/index.html` — Changed `/trust` → `https://portal.systack.net/download/trust-center`
- `Systack/content/systack-site/services.html` — Changed `command.systack.net` → `portal.systack.net`
- `Systack/content/systack-site/pricing.html` — Changed `command.systack.net` → `portal.systack.net`

## Verified Working
- `work/index.html` — Already had correct URL ✅
- `saos/index.html` — No Trust Center link (correct) ✅

## Deploy
- Ran `scripts/sync-site.sh` → pushed to `Phillip-Lowe/systack` repo
- GitHub Pages deployed within ~2 minutes
- All 4 pages verified live with correct URL

## Site Audit (All Good)
- All demo links: 200 (booking, ordering, invoice, SAOS, portal, command center)
- All services listed: Booking, Ordering, Workflow, SAOS Fleet, Invoice, Lead, Support, Reports, Document Classification, Knowledge Base
- All plans: Business Fleet ($299), Enterprise Fleet ($799), Accelerate ($249), Private ($799)
- No Personal tier anywhere
- Stripe subscription buttons on all plan cards
- Case studies with real metrics on work page
- CSS loading correctly (3086 bytes, 200)
