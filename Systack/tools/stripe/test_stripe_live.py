#!/usr/bin/env python3
"""Test opening Stripe payment links to verify they work"""

import urllib.request

links = {
    "Personal+ Monthly": "https://buy.stripe.com/7sYcMYfZLagn9wQ7MG87K03",
    "Personal+ Annual": "https://buy.stripe.com/bJecMYdRD88f8sM5Ey87K04",
    "Business Monthly": "https://buy.stripe.com/dRm9AMcNzgELdN6d7087K0a",
    "Business Annual": "https://buy.stripe.com/14A6oA28V88f6kE8QK87K0c",
    "Enterprise Monthly": "https://buy.stripe.com/cNi8wI9Bnbkr5gAc2W87K0b",
    "Enterprise Annual": "https://buy.stripe.com/6oUfZaaFr0FNfVed7087K0d",
}

print("=== Testing Stripe Links (browser simulation) ===\n")

for name, url in links.items():
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read(1000).decode('utf-8', errors='ignore')
            
            # Check for actual checkout form vs error
            if 'data-testid' in content or 'checkout' in content.lower() or 'payment' in content.lower():
                print(f"✅ {name}: Working checkout page")
            elif 'error' in content.lower() and 'not found' in content.lower():
                print(f"❌ {name}: Page not found")
            elif resp.status == 200:
                print(f"⚠️ {name}: Returns 200 but may need browser")
            else:
                print(f"❌ {name}: Status {resp.status}")
    except Exception as e:
        print(f"❌ {name}: Error - {e}")

print("\n=== Done ===")
