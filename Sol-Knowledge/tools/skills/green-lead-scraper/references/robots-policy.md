# Robots.txt Policy

## Rules

1. **Always check robots.txt** before scraping a domain
2. **Respect `Disallow` directives** for pages marked off-limits
3. **Respect `Crawl-delay`** if present (use max of directive vs config delay)
4. **No scraping behind login walls** without explicit permission

## Checking robots.txt

```python
import urllib.robotparser

rp = urllib.robotparser.RobotFileParser()
rp.set_url(f"https://{domain}/robots.txt")
rp.read()

if not rp.can_fetch("GreenBot/1.0", url):
    print(f"Skipping {url} — disallowed by robots.txt")
    return None
```

## Implementation

The scraper checks `robots.txt` automatically for each new domain. You can disable this with:

```json
{"checkRobots": false}
```

## Notes

- Some sites block all bots: `User-agent: *\nDisallow: /`
- Some allow specific sections: `Allow: /public`
- Always err on the side of caution
