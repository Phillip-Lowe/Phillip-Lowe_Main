#!/usr/bin/env python3
"""Test Stripe API key and list products"""

import json
import urllib.request
import os

# Read API key from file
key_path = os.path.expanduser("~/.openclaw/workspaces/sol/.stripe_api_key")
with open(key_path, 'r') as f:
    api_key = f.read().strip()

print(f"API Key length: {len(api_key)}")
print(f"API Key starts with: {api_key[:20]}")
print(f"API Key ends with: {api_key[-20:]}")

# Test API
req = urllib.request.Request(
    "https://api.stripe.com/v1/products?limit=5",
    headers={
        "Authorization": f"Bearer {api_key}"
    }
)

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
        print(f"\nProducts found: {len(data.get('data', []))}")
        for p in data.get('data', []):
            print(f"  - {p.get('name')} ({p.get('id')})")
except Exception as e:
    print(f"\nError: {e}")
    # Try to read error body
    import sys
    print(f"Status: Check error")
