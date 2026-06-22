# Utopia Deli Meal Prep — Master Documentation

## Weekly Update Process (Standardized)

Trigger phrase: *"Save this everywhere and end session"*

When new meal prep photos arrive:

### 1. Receive Photos
- Get images from Jacqueline (owner)
- Usually arrives via iCloud/Photos or shared folder
- Folder: `utopia-deli-revamp/images/Meal Prep/`

### 2. Identify & Match
- Use image analysis to identify each meal
- Match names to current menu in `catering/catering-form.js`
- Handle renames when dishes change (e.g., "Korean BBQ" → "Peanut Ginger")

### 3. File Management
- Rename descriptively: `meal-{dish-name}.jpg` or `dessert-{name}.jpg`
- Copy to: `catering/images/`
- Remove old placeholder images

### 4. Code Updates
- Update `MEALS` or `DESSERTS` array with new `photo` paths
- Prices remain constant unless explicitly changed
- Tax rate aligned with n8n backend (currently 9.52%)

### 5. Deploy
```bash
git add catering/
git commit -m "feat(menu): Week of [DATE] — new meal prep photos"
git push origin main
```
GitHub Pages auto-deploys — no SSH needed.

## Menu Structure (As of 2026-06-11)

### Meals ($12 each)
| ID | Name | Calories | Photo |
|---|---|---|---|
| buffalo-chickpea | Buffalo Chickpea Ranch Bowl | 490 | meal-buffalo-chickpea.jpg |
| teriyaki-tofu | Teriyaki Tofu Bowl | 480 | meal-teriyaki-tofu.jpg |
| red-lentil-masala | Red Lentil Coconut Masala | 510 | meal-red-lentil-masala.jpg |
| peanut-ginger | Peanut Ginger Bowl | 500 | meal-peanut-ginger.jpg |
| cajun-northern-beans | Cajun Northern Beans & Rice | 470 | meal-cajun-northern-beans.jpg |
| rainbow-bbq-tofu | Rainbow BBQ Tofu Wild Rice | 520 | meal-rainbow-bbq-tofu.jpg |

### Desserts ($6 each)
| ID | Name | Calories | Photo |
|---|---|---|---|
| raspberry-mousse | Raspberry Dark Chocolate Mousse | 340 | dessert-raspberry-mousse.jpg |

## CSS Rules
- `.meal-grid`: 2 columns desktop, 1 column mobile
- `.dessert-grid`: 2 columns desktop, 1 column mobile, **always centered**
- `.meal-card img`: 180px height, object-fit cover
- `.dessert-card img`: 160px height, object-fit cover

## Important Decisions
- **Dessert section:** Separate CTA "Add a Sweet Treat" with pink accent (#AF3D4B)
- **Tax rate:** 9.52% — frontend JS must match n8n backend
- **Labor fee:** $50 flat per order (not per meal)
- **Images:** Lazy-loaded `<img>` tags, not placeholders
- **Deploy method:** GitHub Pages (no SSH to server needed)

## Files
- `catering/index.html` — Main page structure
- `catering/catering-form.js` — Meal data, cart logic, checkout
- `catering/images/` — All food photos
- `.github/workflows/pages.yml` — Auto-deploy config

## Source
Updated: 2026-06-11
Session: Meal prep image upload + dessert section + tax alignment
