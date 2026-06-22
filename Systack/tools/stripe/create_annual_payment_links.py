#!/usr/bin/env python3
"""Create payment links for annual subscriptions"""

import json
import urllib.request
import os

key_path = os.path.expanduser("~/.openclaw/workspaces/sol/.stripe_api_key")
with open(key_path, 'r') as f:
    api_key = f.read().strip()

def stripe_request(url, method="GET", data=None):
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        method=method
    )
    if data:
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        req.data = data.encode()
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error {e.code}: {error_body}")
        return None

# Create payment links for annual prices (no mode parameter needed)
print("=== Creating Payment Links ===")

# Business Fleet Annual
print("\n1. Business Fleet Annual")
business_price = "price_1TfWCN1WicviTxiiVYHg0xjC"
link_data = {
    'line_items[0][price]': business_price,
    'line_items[0][quantity]': '1',
}
link = stripe_request("https://api.stripe.com/v1/payment_links", "POST",
                     "&".join([f"{k}={v}" for k,v in link_data.items()]))
if link:
    print(f"✓ Payment Link: {link.get('url')}")
    print(f"  Link ID: {link.get('id')}")
    print(f"  Button ID: buy_btn_{link.get('id').replace('plink_', '')}")

# Enterprise Fleet Annual
print("\n2. Enterprise Fleet Annual")
enterprise_price = "price_1TfWCN1WicviTxiiLw06pYxR"
link_data = {
    'line_items[0][price]': enterprise_price,
    'line_items[0][quantity]': '1',
}
link = stripe_request("https://api.stripe.com/v1/payment_links", "POST",
                     "&".join([f"{k}={v}" for k,v in link_data.items()]))
if link:
    print(f"✓ Payment Link: {link.get('url')}")
    print(f"  Link ID: {link.get('id')}")
    print(f"  Button ID: buy_btn_{link.get('id').replace('plink_', '')}")

print("\n=== Done ===")
