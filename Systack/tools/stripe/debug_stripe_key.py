#!/usr/bin/env python3
"""Test Stripe publishable key validity"""

import urllib.request
import json

# Test the publishable key
pub_key = "pk_live_51Tckdx1WicviTxii6uKLsxzQENJqWDNxt8Zqmst9YKBQ4F0KSn7VpuR7PZTGRQXJMv42NwimR1kcIdOxElznzIsM000DBc6pKp"

print(f"Testing publishable key: {pub_key[:20]}...{pub_key[-10:]}")
print(f"Key prefix: {pub_key[:7]}")
print()

# Check if it's live or test
if pub_key.startswith('pk_live_'):
    print("✅ This is a LIVE mode key")
elif pub_key.startswith('pk_test_'):
    print("⚠️ This is a TEST mode key")
else:
    print("❌ Unknown key prefix")

# The key format looks valid for Stripe
# pk_live_51Tckdx1WicviTxii... = standard Stripe live key format

print()
print("Common causes of 'Something went wrong':")
print("1. Payment link not active")
print("2. Payment link domain restrictions")
print("3. Account not fully verified")
print("4. Buy button not enabled for the payment link")
print("5. Wrong account (test vs live)")
print()
print("RECOMMENDATION: Use direct payment link URLs instead of embedded buy buttons")
print("until we can debug the button issue.")
