#!/usr/bin/env python3
"""Test if payment links are accessible and active"""

import urllib.request
import json

# Test all payment links
links = {
    "Personal+ Monthly": "https://buy.stripe.com/7sYcMYfZLagn9wQ7MG87K03",
    "Personal+ Annual": "https://buy.stripe.com/bJecMYdRD88f8sM5Ey87K04",
    "Business Monthly": "https://buy.stripe.com/dRm9AMcNzgELdN6d7087K0a",
    "Business Annual": "https://buy.stripe.com/14A6oA28V88f6kE8QK87K0c",
    "Enterprise Monthly": "https://buy.stripe.com/cNi8wI9Bnbkr5gAc2W87K0b",
    "Enterprise Annual": "https://buy.stripe.com/6oUfZaaFr0FNfVed7087K0d",
}

print("=== Testing Payment Links ===\n")

for name, url in links.items():
    try:
        req = urllib.request.Request(url, method='GET')
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"{name}:")
            print(f"  Status: {resp.status}")
            print(f"  URL: {url}")
            
            # Check if it's actually a checkout page
            content = resp.read(500).decode('utf-8', errors='ignore')
            if 'stripe' in content.lower() or 'checkout' in content.lower():
                print(f"  ✅ Working - Stripe checkout page")
            else:
                print(f"  ⚠️ Unexpected content")
            print()
    except Exception as e:
        print(f"{name}:")
        print(f"  ❌ Error: {e}")
        print()

print("=== Done ===")
