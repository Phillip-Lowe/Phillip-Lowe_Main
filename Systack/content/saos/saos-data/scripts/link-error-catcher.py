#!/usr/bin/env python3
"""Link Error Catcher to critical production workflows."""
import json, subprocess, sys

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwNmNiN2I4Zi02OThiLTQxYzYtOWE5NC1iM2YzNTA0MzNjZmEiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiNDQ4MDE4YzAtNTA3NC00YzM0LWEwZjAtMDE4YzY5NzExOTllIiwiaWF0IjoxNzc4OTc1MzE1fQ.8m4SjmpFAr0y9LkIexYBSzt8jEKjkzUWzxjnUtBu80Y"
ERROR_CATCHER_ID = "AdAM0770d3pJTrWt"

CRITICAL = [
    ("JuqVmfK58ydfiLrC", "Utopia Deli — Full Checkout"),
    ("752408b1-01ac-42cc-a7ba-a934e8ffee66", "Utopia Deli — HTML Webhook Checkout v2 (BROKEN)"),
    ("61c97348-a41f-41e8-8f2c-b360b3b27f00", "Utopia Deli — HTML Checkout v3"),
    ("zFYCzAQh9HlNHGpS", "Systack Lead Scraper — SQLite CRM"),
    ("gdQQYtAzX14iQz1m", "Green Systems — Outreach Sequencer"),
]

base_url = "http://localhost:5678/api/v1/workflows"
headers = ["-H", f"X-N8N-API-KEY: {API_KEY}", "-H", "Content-Type: application/json"]

for wf_id, wf_name in CRITICAL:
    # GET
    result = subprocess.run(
        ["curl", "-s", f"{base_url}/{wf_id}"] + headers,
        capture_output=True, text=True
    )
    try:
        wf = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"❌ {wf_name}: JSON parse error - {e}")
        continue
    
    # Set errorWorkflow
    wf.setdefault('settings', {})['errorWorkflow'] = ERROR_CATCHER_ID
    
    # PUT back
    result2 = subprocess.run(
        ["curl", "-s", "-X", "PUT", f"{base_url}/{wf_id}"] + headers,
        input=json.dumps(wf), capture_output=True, text=True
    )
    try:
        updated = json.loads(result2.stdout)
        err_wf = updated.get('settings', {}).get('errorWorkflow', 'NOT SET')
        print(f"✅ {wf_name} → errorWorkflow={'SET' if err_wf == ERROR_CATCHER_ID else err_wf}")
    except json.JSONDecodeError:
        print(f"⚠️  {wf_name}: PUT response not valid JSON - {result2.stdout[:200]}")
