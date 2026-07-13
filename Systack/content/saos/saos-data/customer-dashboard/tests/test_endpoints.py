#!/usr/bin/env python3
"""
SAOS API Endpoint Test Suite
Tests every endpoint in the Customer Portal API for correct responses.
Run: python3 tests/test_endpoints.py
"""

import requests
import json
import sys
import time

BASE = "http://localhost:8768"
INTERNAL_KEY = "9236a071a332cb740af9518c9fdccb7d1a5d3097285b99b75a72875cc96c4f5c"
results = {"pass": 0, "fail": 0, "skip": 0}
errors = []

def test(name, condition, detail=""):
    if condition:
        results["pass"] += 1
        print(f"  ✅ {name}")
    else:
        results["fail"] += 1
        errors.append(f"{name}: {detail}")
        print(f"  ❌ {name} — {detail}")

def skip(name, reason=""):
    results["skip"] += 1
    print(f"  ⏭️  {name} (skipped: {reason})")

print("=" * 60)
print("SAOS API Endpoint Test Suite")
print(f"Target: {BASE}")
print("=" * 60)

# ── HEALTH ENDPOINTS ──────────────────────────────────
print("\n── Health Endpoints ──")
try:
    r = requests.get(f"{BASE}/api/portal/health", timeout=5)
    test("GET /api/portal/health", r.status_code == 200, f"Got {r.status_code}")
    data = r.json()
    test("Health returns ok status", data.get("status") == "ok", f"Got {data.get('status')}")
except Exception as e:
    test("GET /api/portal/health", False, str(e))

# ── PUBLIC ENDPOINTS ──────────────────────────────────
print("\n── Public Endpoints ──")
try:
    r = requests.get(f"{BASE}/api/portal/agents", timeout=5)
    test("GET /api/portal/agents (no auth)", r.status_code == 200, f"Got {r.status_code}")
except Exception as e:
    test("GET /api/portal/agents", False, str(e))

# ── TRUST CENTER (Public) ─────────────────────────────
print("\n── Trust Center (Public) ──")
try:
    r = requests.get(f"{BASE}/api/compliance/trust-center", timeout=5)
    test("GET /api/compliance/trust-center", r.status_code == 200, f"Got {r.status_code}")
    data = r.json()
    test("Trust center has company", "company" in data, "Missing 'company' field")
    test("Trust center has policies", len(data.get("compliance_policies", [])) > 0, "No policies")
    test("Trust center has backup status", "last_backup" in data, "Missing backup status")
    test("Trust center has security events", "security_events_30d" in data, "Missing security events")
except Exception as e:
    test("Trust Center", False, str(e))

# ── AUTH ENDPOINTS ─────────────────────────────────────
print("\n── Auth Endpoints ──")

# Login without credentials
try:
    r = requests.post(f"{BASE}/api/auth/login", json={}, timeout=5)
    test("POST /api/auth/login (empty)", r.status_code == 400, f"Got {r.status_code}")
except Exception as e:
    test("POST /api/auth/login (empty)", False, str(e))

# Login with bad credentials
try:
    r = requests.post(f"{BASE}/api/auth/login", json={"client_id": 99999, "pin": "0000"}, timeout=5)
    test("POST /api/auth/login (bad)", r.status_code == 404, f"Got {r.status_code}")
except Exception as e:
    test("POST /api/auth/login (bad)", False, str(e))

# Login with correct credentials
TOKEN = None
try:
    r = requests.post(f"{BASE}/api/auth/login", json={"client_id": 1, "pin": "1234"}, timeout=5)
    if r.status_code == 200:
        data = r.json()
        if "token" in data:
            TOKEN = data["token"]
            test("POST /api/auth/login (valid)", True)
            test("Login returns token", bool(TOKEN), "No token in response")
            test("Login returns client info", "client" in data, "Missing client info")
        else:
            test("POST /api/auth/login (valid)", False, "No token returned")
    elif r.status_code == 200 and r.json().get("mfa_required"):
        skip("POST /api/auth/login (valid)", "MFA required — using MFA flow")
    else:
        test("POST /api/auth/login (valid)", False, f"Got {r.status_code}: {r.text[:100]}")
except Exception as e:
    test("POST /api/auth/login (valid)", False, str(e))

# If no token, skip authed tests
if not TOKEN:
    print("\n⚠️  No auth token — skipping authenticated tests")
    # Try to get a token with client 2
    try:
        r = requests.post(f"{BASE}/api/auth/login", json={"client_id": 2, "pin": "1234"}, timeout=5)
        if r.status_code == 200 and "token" in r.json():
            TOKEN = r.json()["token"]
            print(f"  ✅ Got token from client 2")
    except:
        pass

if not TOKEN:
    # Create a test token directly via DB
    print("\n⚠️  Still no token — creating test session via DB")
    import subprocess
    import hashlib
    import secrets
    test_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(test_token.encode()).hexdigest()
    from datetime import datetime, timedelta
    expires = (datetime.now() + timedelta(days=30)).isoformat()
    try:
        result = subprocess.run([
            'psql', '-h', 'localhost', '-U', 'philliplowe', '-d', 'systack_memory', '-c',
            f"INSERT INTO client_auth_tokens (client_id, token_hash, expires_at) VALUES (1, '{token_hash}', '{expires}')"
        ], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            TOKEN = test_token
            print(f"  ✅ Created test token")
        else:
            print(f"  ❌ Could not create token: {result.stderr}")
    except Exception as e:
        print(f"  ❌ DB token creation failed: {e}")

AUTH_HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

# ── AUTHED ENDPOINTS ───────────────────────────────────
if TOKEN:
    print("\n── Authed Endpoints ──")
    
    endpoints_get = [
        "/api/portal/status",
        "/api/portal/tasks",
        "/api/portal/client",
        "/api/portal/services",
        "/api/portal/activity",
        "/api/portal/deliverables",
        "/api/portal/integrations",
        "/api/auth/me",
        "/api/auth/mfa/status",
        "/api/auth/permissions",
    ]
    
    for ep in endpoints_get:
        try:
            r = requests.get(f"{BASE}{ep}", headers=AUTH_HEADERS, timeout=5)
            test(f"GET {ep}", r.status_code == 200, f"Got {r.status_code}")
        except Exception as e:
            test(f"GET {ep}", False, str(e))
    
    # Chat endpoints
    print("\n── Chat Endpoints ──")
    try:
        r = requests.get(f"{BASE}/api/chat/conversations", headers=AUTH_HEADERS, timeout=5)
        test("GET /api/chat/conversations", r.status_code == 200, f"Got {r.status_code}")
        convs = r.json() if r.status_code == 200 else []
        test("Conversations is list", isinstance(convs, list), "Not a list")
    except Exception as e:
        test("GET /api/chat/conversations", False, str(e))
    
    # Poll endpoint
    try:
        r = requests.get(f"{BASE}/api/chat/poll", headers=AUTH_HEADERS, timeout=5)
        test("GET /api/chat/poll", r.status_code == 200, f"Got {r.status_code}")
    except Exception as e:
        test("GET /api/chat/poll", False, str(e))

# ── ADMIN ENDPOINTS (P2-P5) ────────────────────────────
print("\n── P2-P5 Admin Endpoints ──")

# These require admin role — try with our token
if TOKEN:
    admin_endpoints = [
        ("GET", "/api/admin/backup-log"),
        ("GET", "/api/admin/backup/rpo-rto"),
        ("GET", "/api/admin/security-events"),
        ("GET", "/api/admin/security-events/stats"),
        ("GET", "/api/admin/audit-log"),
        ("GET", "/api/compliance/policies"),
        ("GET", "/api/compliance/incidents"),
    ]
    
    for method, ep in admin_endpoints:
        try:
            if method == "GET":
                r = requests.get(f"{BASE}{ep}", headers=AUTH_HEADERS, timeout=5)
            test(f"{method} {ep}", r.status_code in (200, 403), f"Got {r.status_code}")
            if r.status_code == 403:
                print(f"    (403 expected if not admin role)")
        except Exception as e:
            test(f"{method} {ep}", False, str(e))

# ── INTERNAL ENDPOINTS ─────────────────────────────────
print("\n── Internal Endpoints ──")
INTERNAL_HEADERS = {"X-Internal-Api-Key": INTERNAL_KEY}

internal_get = [
    "/api/internal/pending-tasks",
    "/api/internal/notifications/pending",
]

for ep in internal_get:
    try:
        r = requests.get(f"{BASE}{ep}", headers=INTERNAL_HEADERS, timeout=5)
        test(f"GET {ep}", r.status_code == 200, f"Got {r.status_code}")
    except Exception as e:
        test(f"GET {ep}", False, str(e))

# Internal without key
try:
    r = requests.get(f"{BASE}/api/internal/pending-tasks", timeout=5)
    test("GET /api/internal/pending-tasks (no key)", r.status_code == 401, f"Got {r.status_code}")
except Exception as e:
    test("Internal no-key test", False, str(e))

# ── PDF DOWNLOAD ROUTES ────────────────────────────────
print("\n── PDF Download Routes ──")
pdf_routes = [
    "/download/quickstart-v7",
    "/download/user-guide-v6",
    "/download/manual-v7",
    "/download/architecture-v5",
    "/download/mobile-guide-v4",
    "/download/enterprise-guide",
    "/download/technical-spec",
    "/download/ios-cert-plan",
    "/download/changelog",
    "/download/changelog-jul5",
    "/download/readme",
    "/download/security-arch",
    "/download/trust-center",
    "/download/backup-recovery",
]

for route in pdf_routes:
    try:
        r = requests.get(f"{BASE}{route}", timeout=5)
        test(f"GET {route}", r.status_code == 200, f"Got {r.status_code}")
        if r.status_code == 200:
            ct = r.headers.get("Content-Type", "")
            if "pdf" not in ct and "application/octet-stream" not in ct:
                test(f"  {route} content-type", False, f"Got {ct}")
    except Exception as e:
        test(f"GET {route}", False, str(e))

# ── COMMAND CENTER ENDPOINTS ───────────────────────────
print("\n── Command Center (port 8770) ──")
CC_BASE = "http://localhost:8770"
CC_HEADERS = {"X-Admin-PIN": "46097565"}

cc_endpoints = [
    "/api/health",
    "/api/fleet/status",
    "/api/fleet/clients",
    "/api/fleet/agents",
    "/api/fleet/infrastructure",
    "/api/fleet/workflows",
    "/api/fleet/usage",
    "/api/fleet/security-events",
    "/api/fleet/backup-status",
    "/api/fleet/compliance",
    "/api/fleet/audit-trail",
    "/api/fleet/services-health",
    "/api/fleet/alerts",
]

for ep in cc_endpoints:
    try:
        r = requests.get(f"{CC_BASE}{ep}", headers=CC_HEADERS, timeout=5)
        test(f"GET {ep}", r.status_code == 200, f"Got {r.status_code}")
    except Exception as e:
        test(f"GET {ep}", False, str(e))

# Client detail
try:
    r = requests.get(f"{CC_BASE}/api/fleet/clients/1", headers=CC_HEADERS, timeout=5)
    test("GET /api/fleet/clients/1", r.status_code == 200, f"Got {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        test("Client detail has enterprise_readiness", "enterprise_readiness" in data, "Missing")
except Exception as e:
    test("GET /api/fleet/clients/1", False, str(e))

# ── SUMMARY ────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"RESULTS: {results['pass']} passed, {results['fail']} failed, {results['skip']} skipped")
if errors:
    print(f"\nFailures:")
    for e in errors:
        print(f"  ❌ {e}")
print("=" * 60)
sys.exit(0 if results["fail"] == 0 else 1)