# Pre-built Selectors for Popular Directories

## Yelp
```json
{
  "name": "h1",
  "phone": "[data-testid='phone-text']",
  "address": "[data-testid='address-text']",
  "rating": "[aria-label*='star rating']",
  "review_count": "[class*='reviewCount']"
}
```

## Google Maps (via Place API)
Use Places API instead of scraping for reliable data.

## Yellow Pages
```json
{
  "name": ".business-name",
  "phone": ".phone",
  "address": ".street-address",
  "rating": ".rating",
  "review_count": ".count"
}
```

## BBB (Better Business Bureau)
```json
{
  "name": "h1.bbb-business-name",
  "phone": ".phone-number",
  "address": ".business-address",
  "rating": ".bbb-rating"
}
```

## Adding Custom Selectors

Add to `scripts/config.json`:
```json
{
  "selectors": {
    "name": "h1, .business-name",
    "phone": "a[href^='tel:']",
    "email": "a[href^='mailto:']",
    "address": ".address",
    "services": ".services li",
    "rating": ".rating",
    "review_count": ".review-count"
  }
}
```
