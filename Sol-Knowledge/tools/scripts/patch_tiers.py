#!/usr/bin/env python3
"""
Patch provision_vps.py with correct tier plans
"""

import re

with open('/tmp/systack-saas-init/scripts/provision_vps.py', 'r') as f:
    content = f.read()

# Find and replace TIER_PLANS
old_block = '''TIER_PLANS = {
    "business": {
        "plan": "vhp-4c-16gb",
        "region": "ord",  # Chicago (closest to Little Rock)
        "os_id": UBUNTU_22_04_OS_ID,
        "description": "Business Fleet - 4 vCPU, 16GB RAM"
    },
    "enterprise": {
        "plan": "vhp-4c-16gb",
        "region": "ord",
        "os_id": UBUNTU_22_04_OS_ID,
        "description": "Enterprise Fleet - 4 vCPU, 16GB RAM + Dedicated Support"
    },
    # Test tier for development (cheapest)
    "test": {
        "plan": "vc2-1c-1gb",
        "region": "ord",
        "os_id": UBUNTU_22_04_OS_ID,
        "description": "Test - 1 vCPU, 1GB RAM (development only)"
    }
}'''

new_block = '''TIER_PLANS = {
    "business": {
        "plan": "vhp-8c-16gb",  # 8 vCPU, 16GB RAM - both tiers use 8 cores
        "region": "ord",
        "os_id": UBUNTU_22_04_OS_ID,
        "description": "Business Fleet - 8 vCPU, 16GB RAM"
    },
    "enterprise": {
        "plan": "vhf-8c-32gb",  # 8 vCPU, 32GB RAM - more RAM for enterprise
        "region": "ord",
        "os_id": UBUNTU_22_04_OS_ID,
        "description": "Enterprise Fleet - 8 vCPU, 32GB RAM + Dedicated Support"
    },
    # Test tier for development (cheapest)
    "test": {
        "plan": "vc2-1c-1gb",
        "region": "ord",
        "os_id": UBUNTU_22_04_OS_ID,
        "description": "Test - 1 vCPU, 1GB RAM (development only)"
    }
}'''

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('/tmp/systack-saas-init/scripts/provision_vps.py', 'w') as f:
        f.write(content)
    print("✅ Updated TIER_PLANS successfully")
else:
    print("❌ Could not find old TIER_PLANS block")
    print("Searching for it...")
    # Try finding with regex
    match = re.search(r'TIER_PLANS = \{.*?\n\}', content, re.DOTALL)
    if match:
        print(f"Found at line {content[:match.start()].count(chr(10)) + 1}")
    else:
        print("Not found with regex either")