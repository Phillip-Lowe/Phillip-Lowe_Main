# PDF Update Required — 2026-06-20 Session Changes

## Legacy PDFs Archived
**Location:** `docs/archive/2026-06-20-legacy/`

| PDF | Status | New Version Needed |
|-----|--------|-------------------|
| utopia-deli-client-service-manual.pdf | Archived | ✅ Yes |
| utopia-deli-confirmation-client-service-manual.pdf | Archived | ✅ Yes |
| utopia-deli-internal-implementation-guide.pdf | Archived | ✅ Yes |
| utopia-deli-troubleshooting-guide.pdf | Archived | ✅ Yes |
| utopia-deli-meal-prep-client-service-manual.pdf | Archived | ✅ Yes |
| utopia-deli-meal-prep-internal-implementation-guide.pdf | Archived | ✅ Yes |
| utopia-deli-catering-client-service-manual.pdf | Archived | ✅ Yes |

## What Changed (Requires Doc Updates)

### Order System (pickup-order)
1. **Field Order:** Name → Phone → Email (consent) → Instructions → Submit
2. **Removed:** Pickup time dropdown
3. **Added:** Consent text under email field
4. **Added:** Footer links clickable (Maps, Phone, Email)
5. **Changed:** Juice price $10 → $5 (10oz only)

### Meal Prep System (catering)
1. **Field Order:** Name → Phone → Email (consent) → Instructions → Pickup Info → Submit
2. **Changed:** "Pick your weekly sets" → "Get your weekly sets"
3. **Added:** Consent text under email field
4. **Added:** Google Maps link for address
5. **Changed:** Pickup info moved after notes

### Both Pages
1. **Logo:** Clickable, links to homepage
2. **Privacy page:** New consent/terms page
3. **Footer slogan:** "It's just good food."

### Database/System
1. **New script:** `scripts/deli_square_data_pg.py`
2. **Sync:** 5,000 Square customers → Postgres
3. **Cleanup:** 356 usable contacts, 233 with both email+phone

## Commands to Regenerate

```bash
# Install dependencies
pip3 install pyppeteer
brew install pandoc  # if not installed

# Regenerate all updated docs
cd /Users/philliplowe/utopia-deli-order

# Order system client docs
python3 ~/.openclaw/skills/branded-pdf-generator/scripts/generate_pdf.py \
  docs/automations/order-system/client/utopia-deli-client-service-manual.md \
  docs/automations/order-system/client/utopia-deli-client-service-manual.pdf \
  --title "Utopia Deli — Online Ordering System — Client Service Manual" \
  --brand utopia-deli

# Order system internal docs
python3 ~/.openclaw/skills/branded-pdf-generator/scripts/generate_pdf.py \
  docs/automations/order-system/internal/utopia-deli-internal-implementation-guide.md \
  docs/automations/order-system/internal/utopia-deli-internal-implementation-guide.pdf \
  --title "Utopia Deli — Internal Implementation Guide" \
  --brand utopia-deli

python3 ~/.openclaw/skills/branded-pdf-generator/scripts/generate_pdf.py \
  docs/automations/order-system/internal/utopia-deli-troubleshooting-guide.md \
  docs/automations/order-system/internal/utopia-deli-troubleshooting-guide.pdf \
  --title "Utopia Deli — Troubleshooting Guide" \
  --brand utopia-deli

# Meal prep docs
python3 ~/.openclaw/skills/branded-pdf-generator/scripts/generate_pdf.py \
  docs/automations/meal-prep/client/utopia-deli-meal-prep-client-service-manual.md \
  docs/automations/meal-prep/client/utopia-deli-meal-prep-client-service-manual.pdf \
  --title "Utopia Deli — Meal Prep System — Client Service Manual" \
  --brand utopia-deli

python3 ~/.openclaw/skills/branded-pdf-generator/scripts/generate_pdf.py \
  docs/automations/meal-prep/internal/utopia-deli-meal-prep-internal-implementation-guide.md \
  docs/automations/meal-prep/internal/utopia-deli-meal-prep-internal-implementation-guide.pdf \
  --title "Utopia Deli — Meal Prep — Internal Implementation Guide" \
  --brand utopia-deli

# Catering docs
python3 ~/.openclaw/skills/branded-pdf-generator/scripts/generate_pdf.py \
  docs/automations/catering-lead/client/utopia-deli-catering-client-service-manual.md \
  docs/automations/catering-lead/client/utopia-deli-catering-client-service-manual.pdf \
  --title "Utopia Deli — Catering System — Client Service Manual" \
  --brand utopia-deli
```

## Note
The Markdown source files (`.md`) need to be updated with the new field orders, consent text, and feature changes BEFORE regenerating PDFs. Otherwise the PDFs will contain stale information.

**Suggested approach:**
1. Update `.md` files with new content
2. Run generate commands above
3. Commit new PDFs

## Skill Location
`/Users/philliplowe/.openclaw/skills/branded-pdf-generator/`

## Last Updated
2026-06-20 03:35 CDT
