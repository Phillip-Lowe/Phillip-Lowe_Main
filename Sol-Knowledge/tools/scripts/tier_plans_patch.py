#!/usr/bin/env python3
"""
SAOS VPS Provisioning Script (UPDATED)
8-core business tier, 8-core enterprise with 32GB RAM
"""

import os
import sys
import json
import time
import base64
import argparse
import requests
from datetime import datetime

UBUNTU_22_04_OS_ID = 2076

TIER_PLANS = {
    "business": {
        "plan": "vhp-8c-16gb",  # 8 vCPU, 16GB RAM
        "region": "ord",
        "os_id": UBUNTU_22_04_OS_ID,
        "description": "Business Fleet - 8 vCPU, 16GB RAM"
    },
    "enterprise": {
        "plan": "vhf-8c-32gb",  # 8 vCPU, 32GB RAM
        "region": "ord",
        "os_id": UBUNTU_22_04_OS_ID,
        "description": "Enterprise Fleet - 8 vCPU, 32GB RAM + Dedicated Support"
    },
    "test": {
        "plan": "vc2-1c-1gb",
        "region": "ord",
        "os_id": UBUNTU_22_04_OS_ID,
        "description": "Test - 1 vCPU, 1GB RAM"
    }
}

print("Updated TIER_PLANS:")
for tier, config in TIER_PLANS.items():
    print(f"  {tier}: {config['plan']} - {config['description']}")