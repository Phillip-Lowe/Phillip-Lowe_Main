#!/usr/bin/env python3
"""Create missing Stripe payment links for SAOS Business Fleet Annual and SAOS Enterprise Fleet Annual"""

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

# List all products
print("=== Finding Products ===")
products = stripe_request("https://api.stripe.com/v1/products?limit=30")
if products and 'data' in products:
    for p in products['data']:
        print(f"{p['id']}: {p.get('name', 'N/A')}")
    
    business_prod = None
    enterprise_prod = None
    
    for p in products['data']:
        name = p.get('name', '')
        if 'Business Fleet' in name and 'Monthly' in name:
            business_prod = p['id']
            print(f"\n✓ Found Business Fleet Monthly: {p['id']}")
        elif 'Enterprise Fleet' in name and 'Monthly' in name:
            enterprise_prod = p['id']
            print(f"\n✓ Found Enterprise Fleet Monthly: {p['id']}")
    
    if not business_prod:
        print("\n✗ Business Fleet Monthly not found, creating product...")
        prod_data = {
            'name': 'SAOS Business Fleet — Monthly',
            'description': 'Multi-agent team for your business. 16GB VPS, team Slack, invoice processing, lead qualification.'
        }
        prod = stripe_request("https://api.stripe.com/v1/products", "POST",
                             "&".join([f"{k}={urllib.parse.quote(v)}" for k,v in prod_data.items()]))
        if prod:
            business_prod = prod['id']
            print(f"Created: {business_prod}")
    
    if not enterprise_prod:
        print("\n✗ Enterprise Fleet Monthly not found, creating product...")
        prod_data = {
            'name': 'SAOS Enterprise Fleet — Monthly',
            'description': 'Full private automation suite. On-premise, HIPAA-grade, dedicated hardware.'
        }
        prod = stripe_request("https://api.stripe.com/v1/products", "POST",
                             "&".join([f"{k}={urllib.parse.quote(v)}" for k,v in prod_data.items()]))
        if prod:
            enterprise_prod = prod['id']
            print(f"Created: {enterprise_prod}")
    
    # Create annual prices
    if business_prod:
        print(f"\n=== Creating Business Fleet Annual ===")
        # Check if annual price already exists
        prices = stripe_request(f"https://api.stripe.com/v1/prices?product={business_prod}&limit=10")
        annual_exists = False
        if prices and 'data' in prices:
            for pr in prices['data']:
                if pr.get('recurring', {}).get('interval') == 'year':
                    annual_exists = True
                    print(f"Annual price already exists: {pr['id']}")
                    
        if not annual_exists:
            price_data = {
                'product': business_prod,
                'unit_amount': '358800',  # $3,588.00 in cents (299 * 12)
                'currency': 'usd',
                'recurring[interval]': 'year',
                'nickname': 'Business Fleet Annual'
            }
            price = stripe_request("https://api.stripe.com/v1/prices", "POST",
                                    "&".join([f"{k}={v}" for k,v in price_data.items()]))
            if price:
                print(f"Price created: {price.get('id')}")
                
                # Create payment link
                link_data = {
                    'line_items[0][price]': price['id'],
                    'line_items[0][quantity]': '1',
                    'mode': 'subscription',
                    'metadata[name]': 'SAOS Business Fleet Annual'
                }
                link = stripe_request("https://api.stripe.com/v1/payment_links", "POST",
                                     "&".join([f"{k}={v}" for k,v in link_data.items()]))
                if link:
                    print(f"Payment Link: {link.get('url')}")
                    print(f"Link ID: {link.get('id')}")
                    print(f"Buy Button ID: buy_btn_{link.get('id').replace('plink_', '')}")
    
    if enterprise_prod:
        print(f"\n=== Creating Enterprise Fleet Annual ===")
        # Check if annual price already exists
        prices = stripe_request(f"https://api.stripe.com/v1/prices?product={enterprise_prod}&limit=10")
        annual_exists = False
        if prices and 'data' in prices:
            for pr in prices['data']:
                if pr.get('recurring', {}).get('interval') == 'year':
                    annual_exists = True
                    print(f"Annual price already exists: {pr['id']}")
                    
        if not annual_exists:
            price_data = {
                'product': enterprise_prod,
                'unit_amount': '958800',  # $9,588.00 in cents (799 * 12)
                'currency': 'usd',
                'recurring[interval]': 'year',
                'nickname': 'Enterprise Fleet Annual'
            }
            price = stripe_request("https://api.stripe.com/v1/prices", "POST",
                                    "&".join([f"{k}={v}" for k,v in price_data.items()]))
            if price:
                print(f"Price created: {price.get('id')}")
                
                # Create payment link
                link_data = {
                    'line_items[0][price]': price['id'],
                    'line_items[0][quantity]': '1',
                    'mode': 'subscription',
                    'metadata[name]': 'SAOS Enterprise Fleet Annual'
                }
                link = stripe_request("https://api.stripe.com/v1/payment_links", "POST",
                                     "&".join([f"{k}={v}" for k,v in link_data.items()]))
                if link:
                    print(f"Payment Link: {link.get('url')}")
                    print(f"Link ID: {link.get('id')}")
                    print(f"Buy Button ID: buy_btn_{link.get('id').replace('plink_', '')}")

print("\n=== Done ===")
