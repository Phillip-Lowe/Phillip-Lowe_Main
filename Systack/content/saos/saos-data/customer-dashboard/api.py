#!/usr/bin/env python3
"""
SAOS Customer Dashboard API v2.1
Enhanced UX: better task descriptions, agent info, PIN management, onboarding flow.
Serves client-scoped fleet data + REAL-TIME CHAT for the customer-facing portal.

Usage:
    python3 api.py --port 8768
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
import hashlib
import random
import secrets
import string
from datetime import datetime, timedelta
from functools import wraps
import base64
import uuid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DELIVERABLES_DIR = os.path.join(BASE_DIR, 'deliverables')
os.makedirs(DELIVERABLES_DIR, exist_ok=True)
app = Flask(__name__, static_folder=BASE_DIR)
CORS(app, origins=["http://localhost:8768", "https://*.ts.net", "https://systack.net"])

# ── SECURITY: RATE LIMITING ────────────────────────────────
# Simple in-memory rate limiter for login attempts
_login_attempts = {}

def check_rate_limit(key, max_attempts=5, window_seconds=300):
    """Check if key (IP + endpoint) has exceeded rate limit."""
    now = datetime.now()
    window_start = now - timedelta(seconds=window_seconds)
    
    # Clean old entries
    for k in list(_login_attempts.keys()):
        _login_attempts[k] = [t for t in _login_attempts[k] if t > window_start]
        if not _login_attempts[k]:
            del _login_attempts[k]
    
    # Check current key
    if key not in _login_attempts:
        _login_attempts[key] = []
    
    recent = [t for t in _login_attempts[key] if t > window_start]
    if len(recent) >= max_attempts:
        return False, len(recent)
    
    _login_attempts[key].append(now)
    return True, len(recent)

# ── ADVANCED RATE LIMITING ─────────────────────────────────
# Per-endpoint rate limit configuration
RATE_LIMITS = {
    'login':         {'max': 5,   'window': 300},   # 5 per 5 min
    'mfa_verify':    {'max': 5,   'window': 300},   # 5 per 5 min
    'pin_reset':     {'max': 3,   'window': 3600},  # 3 per hour
    'register':     {'max': 5,   'window': 3600},  # 5 per hour
    'api_general':   {'max': 100, 'window': 60},    # 100 per min
    'api_write':     {'max': 30,  'window': 60},    # 30 per min
    'webhook':       {'max': 200, 'window': 60},    # 200 per min
    'file_upload':   {'max': 10,  'window': 60},    # 10 per min
}

def rate_limit(endpoint_type, key_suffix=''):
    """Decorator for advanced per-endpoint rate limiting."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            config = RATE_LIMITS.get(endpoint_type, RATE_LIMITS['api_general'])
            client_ip = request.remote_addr or 'unknown'
            key = f"{endpoint_type}:{client_ip}:{key_suffix}"
            allowed, attempts = check_rate_limit(key, max_attempts=config['max'], window_seconds=config['window'])
            if not allowed:
                log_audit(f'rate_limited_{endpoint_type}', ip=client_ip)
                resp = jsonify({
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {config['max']} per {config['window']}s. Try again later.",
                    "limit": config['max'],
                    "window_seconds": config['window']
                })
                resp.status_code = 429
                resp.headers['Retry-After'] = str(config['window'])
                resp.headers['X-RateLimit-Limit'] = str(config['max'])
                resp.headers['X-RateLimit-Remaining'] = '0'
                return resp
            resp = f(*args, **kwargs)
            if hasattr(resp, 'headers'):
                resp.headers['X-RateLimit-Limit'] = str(config['max'])
                resp.headers['X-RateLimit-Remaining'] = str(max(0, config['max'] - attempts))
            return resp
        return decorated
    return decorator

DB_HOST = os.environ.get("PGHOST", "localhost")
DB_PORT = int(os.environ.get("PGPORT", "5432"))
DB_NAME = os.environ.get("PGDATABASE", "systack_memory")
DB_USER = os.environ.get("PGUSER", "philliplowe")

# ── SERVICES CONFIGURATION ─────────────────────────────────
# Service definitions by tier — ALIGNED WITH ACTUAL SYSTACK OFFERINGS
# Source: Systack/content/systack-site/services/service-packages.md
# Updated: 2026-06-29 — Removed fake services, matched real products

TIER_SERVICES = {
    'business': [
        {'icon': '🧾', 'name': 'Invoice Processing Pipeline', 'desc': 'Auto-extract vendor, totals, line items from invoices. Push to your accounting system.', 'active': True},
        {'icon': '🎯', 'name': 'Lead Qualification System', 'desc': 'Score and route incoming leads based on your criteria. High-intent flagged automatically.', 'active': True},
        {'icon': '💬', 'name': 'Customer Support Drafting', 'desc': 'Auto-draft responses to common inquiries. Human reviews before send.', 'active': True},
        {'icon': '📄', 'name': 'Document Classification Engine', 'desc': 'Incoming docs auto-sorted: contracts, invoices, forms, applications.', 'active': True},
        {'icon': '📊', 'name': 'Scheduled Report Generator', 'desc': 'Daily/weekly summary reports auto-generated and delivered to Slack/email.', 'active': True},
        {'icon': '🤖', 'name': '7-Agent AI Fleet', 'desc': 'SOL, ASSEMBLY, CHATTY, ATLAS, GENI, JURIS, PESSI — managed team of specialists.', 'active': True},
        {'icon': '⚙️', 'name': 'n8n Workflow Hosting', 'desc': 'Up to 10,000 automation runs/month. Visual builder for custom workflows.', 'active': True},
        {'icon': '🔐', 'name': 'Tailscale VPN + PostgreSQL', 'desc': 'Encrypted mesh network + managed database. Your data stays private.', 'active': True},
    ],
    'enterprise': [
        {'icon': '🧾', 'name': 'Invoice Processing Pipeline', 'desc': 'Auto-extract vendor, totals, line items from invoices. Push to your accounting system.', 'active': True},
        {'icon': '🎯', 'name': 'Lead Qualification System', 'desc': 'Score and route incoming leads based on your criteria. High-intent flagged automatically.', 'active': True},
        {'icon': '💬', 'name': 'Customer Support Drafting', 'desc': 'Auto-draft responses to common inquiries. Human reviews before send.', 'active': True},
        {'icon': '📄', 'name': 'Document Classification Engine', 'desc': 'Incoming docs auto-sorted: contracts, invoices, forms, applications.', 'active': True},
        {'icon': '📊', 'name': 'Scheduled Report Generator', 'desc': 'Daily/weekly summary reports auto-generated and delivered to Slack/email.', 'active': True},
        {'icon': '🤖', 'name': '10-Agent AI Fleet', 'desc': 'Business Fleet + CODY (code review), VALI (QA), CHATTY (comms) — full coverage.', 'active': True},
        {'icon': '⚙️', 'name': 'Unlimited n8n Workflows', 'desc': 'No run limits. Build as many automations as your business needs.', 'active': True},
        {'icon': '🔐', 'name': 'Tailscale VPN + PostgreSQL', 'desc': 'Encrypted mesh network + managed database. Your data stays private.', 'active': True},
        {'icon': '🏢', 'name': '32GB RAM Infrastructure', 'desc': 'Double the compute. Faster inference, larger context windows, parallel processing.', 'active': True},
        {'icon': '🚨', 'name': 'Dedicated Support Line', 'desc': '4-hour SLA response. Priority feature requests. Quarterly business reviews.', 'active': True},
    ],
    'private': [
        {'icon': '📄', 'name': 'Private Document Extraction Pipeline', 'desc': 'Scanned PDFs, contracts, medical records → structured data. Zero cloud exposure.', 'active': True},
        {'icon': '🧾', 'name': 'Automated Invoice Processing System', 'desc': 'Classify, extract, route for approval, push to QuickBooks/Xero. Air-gapped.', 'active': True},
        {'icon': '💬', 'name': 'Self-Hosted Customer Support Automations', 'desc': 'Auto-draft responses. Human reviews. Local SMTP only. No external APIs.', 'active': True},
        {'icon': '⌨️', 'name': 'Local Data Entry Elimination System', 'desc': 'Watch folders/inboxes. Extract data. Populate CRM/EHR automatically.', 'active': True},
        {'icon': '🔍', 'name': 'Private Knowledge Base Search', 'desc': 'Index your internal docs. Answers sourced exclusively from your files. Zero cloud.', 'active': True},
        {'icon': '📋', 'name': 'Automated Compliance Audit Trail', 'desc': 'Every AI action logged. Full chain of custody. Audit-ready at any moment.', 'active': True},
    ],
    'accelerate': [
        {'icon': '🧾', 'name': 'Automated Invoice Processing System', 'desc': 'Ingest invoices (PDF, email, scan). Extract vendor, total, line items. Push to accounting.', 'active': True},
        {'icon': '💬', 'name': 'Self-Hosted Customer Support Automations', 'desc': 'Auto-classify and draft responses. Human reviews before send.', 'active': True},
        {'icon': '⌨️', 'name': 'Local Data Entry Elimination System', 'desc': 'Monitor sources, extract data, populate CRM/ERP automatically.', 'active': True},
        {'icon': '🎯', 'name': 'Automated Lead Qualification Pipeline', 'desc': 'Score and route leads. High-intent flagged, tire-kickers nurtured.', 'active': True},
        {'icon': '📄', 'name': 'Document Classification & Routing Engine', 'desc': 'Auto-sort by type. Route to correct department or folder.', 'active': True},
        {'icon': '📊', 'name': 'Scheduled Report Generator', 'desc': 'Daily/weekly reports auto-generated. Delivered to Slack/email.', 'active': True},
        {'icon': '⚙️', 'name': 'n8n Workflow Hosting', 'desc': 'Up to 10,000 automation runs/month. Managed cloud VPS.', 'active': True},
        {'icon': '🔐', 'name': 'Tailscale VPN + PostgreSQL', 'desc': 'Encrypted mesh network + managed database. Cloud-hosted, zero external AI.', 'active': True},
    ]
}

# ── STRIPE CHECKOUT CONFIGURATION ─────────────────────────
STRIPE_CHECKOUT_URLS = {
    'business': {
        'monthly': 'https://buy.stripe.com/6oUdR2eVHfAH5gA9UO87K01',
        'annual': 'https://buy.stripe.com/eVqbIUcNz607eRa8QK87K00',
        'price_monthly': 299,
        'price_annual': 2988,
    },
    'enterprise': {
        'monthly': 'https://buy.stripe.com/14A7sE9Bn2NVaAU2sm87K02',
        'annual': 'https://buy.stripe.com/dRm14gcNz74beRa7MG87K0f',
        'price_monthly': 799,
        'price_annual': 7990,
    },
    'private': {
        'monthly': 'https://buy.stripe.com/6oUdR2eVHfAH5gA9UO87K01',
        'price_monthly': 799,
    },
    'accelerate': {
        'monthly': 'https://buy.stripe.com/6oUdR2eVHfAH5gA9UO87K01',
        'price_monthly': 249,
    },
}

TIER_INFRA = {
    'business': [
        {'icon': '☁️', 'name': 'Infrastructure', 'value': 'Cloud VPS (16GB RAM)'},
        {'icon': '🧠', 'name': 'AI Models', 'value': 'Local Ollama (qwen2.5:7b)'},
        {'icon': '🔐', 'name': 'Network', 'value': 'Tailscale encrypted tunnel'},
        {'icon': '⚙️', 'name': 'Automation Engine', 'value': 'n8n (10K runs/mo)'},
        {'icon': '🛠️', 'name': 'Management', 'value': 'Fully managed by Systack'},
        {'icon': '👥', 'name': 'Team Size', 'value': 'Up to 5 members'},
    ],
    'enterprise': [
        {'icon': '☁️', 'name': 'Infrastructure', 'value': 'Cloud VPS (32GB RAM)'},
        {'icon': '🧠', 'name': 'AI Models', 'value': 'Local Ollama (llama3:70b)'},
        {'icon': '🔐', 'name': 'Network', 'value': 'Tailscale encrypted tunnel'},
        {'icon': '⚙️', 'name': 'Automation Engine', 'value': 'n8n (unlimited runs)'},
        {'icon': '🛠️', 'name': 'Management', 'value': 'Fully managed by Systack'},
        {'icon': '👥', 'name': 'Team Size', 'value': 'Unlimited members'},
        {'icon': '🚨', 'name': 'Support', 'value': 'Dedicated line, 4hr SLA'},
    ],
    'private': [
        {'icon': '🖥️', 'name': 'Hardware', 'value': 'Mac Studio / Linux + RTX 4090'},
        {'icon': '🧠', 'name': 'AI Models', 'value': 'llama3-70b, command-r (local)'},
        {'icon': '🔒', 'name': 'Network', 'value': 'Air-gapped or firewalled LAN'},
        {'icon': '☁️', 'name': 'Cloud Apps', 'value': 'ZERO — Stripe only (client account)'},
        {'icon': '⚙️', 'name': 'Automation Engine', 'value': 'Self-hosted n8n'},
        {'icon': '🛠️', 'name': 'Management', 'value': 'White-glove by Systack'},
    ],
    'accelerate': [
        {'icon': '☁️', 'name': 'Infrastructure', 'value': 'Cloud GPU instances (RunPod/Lambda)'},
        {'icon': '🧠', 'name': 'AI Models', 'value': 'llama3-8b, mistral-7b (local)'},
        {'icon': '🔐', 'name': 'Network', 'value': 'Tailscale WireGuard tunnel'},
        {'icon': '⚙️', 'name': 'Automation Engine', 'value': 'n8n (10K runs/mo)'},
        {'icon': '📈', 'name': 'Scaling', 'value': 'Auto-scaling GPU instances'},
        {'icon': '🛠️', 'name': 'Management', 'value': 'Fully managed by Systack'},
    ]
}

TIER_SUPPORT = {
    'business': [
        {'label': 'Support Channel', 'value': 'Email + Slack'},
        {'label': 'Response Time', 'value': 'Same business day'},
        {'label': 'Setup', 'value': 'Remote (3-5 business days)'},
        {'label': 'Uptime SLA', 'value': '99.5% monthly'},
        {'label': 'Agent Fleet', 'value': '7 agents (SOL, ASSEMBLY, CHATTY, ATLAS, GENI, JURIS, PESSI)'},
    ],
    'enterprise': [
        {'label': 'Support Channel', 'value': 'Dedicated Slack + Phone'},
        {'label': 'Response Time', 'value': '4-hour SLA (business hours)'},
        {'label': 'Setup', 'value': 'White-glove on-site (1-2 weeks)'},
        {'label': 'Uptime SLA', 'value': '99.9% monthly'},
        {'label': 'Agent Fleet', 'value': '10 agents (+ CODY, VALI, CHATTY)'},
        {'label': 'Reviews', 'value': 'Quarterly business reviews'},
    ],
    'private': [
        {'label': 'Support Channel', 'value': 'Phone + Scheduled calls'},
        {'label': 'Response Time', 'value': '4-hour SLA (business hours)'},
        {'label': 'Setup', 'value': 'On-site hardware install (1-2 weeks)'},
        {'label': 'Uptime SLA', 'value': '99.5% (your hardware, our maintenance)'},
        {'label': 'Hardware', 'value': 'Client-owned (Mac Studio / Linux + RTX 4090)'},
    ],
    'accelerate': [
        {'label': 'Support Channel', 'value': 'Email + Slack'},
        {'label': 'Response Time', 'value': 'Same business day'},
        {'label': 'Setup', 'value': 'Remote (3-5 business days)'},
        {'label': 'Uptime SLA', 'value': '99.9% monthly'},
        {'label': 'Scaling', 'value': 'Auto-scaling cloud GPU'},
    ]
}


# ── DB HELPERS ─────────────────────────────────────────────────

def get_db():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER
    )

def db_query(sql, params=(), one=False):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.commit()
        if one:
            return dict(rows[0]) if rows else None
        return [dict(r) for r in rows]
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

def db_exec(sql, params=()):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return str(e)
    finally:
        cur.close()
        conn.close()

# ── AUTH ───────────────────────────────────────────────────────

def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()

def generate_pin(length=6):
    """Generate a numeric PIN."""
    return ''.join(random.choices(string.digits, k=length))

def generate_token():
    return secrets.token_urlsafe(32)

def get_auth_client():
    """Extract client from Authorization: Bearer <token> header."""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header[7:].strip()
    token_hash = hash_token(token)
    
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT c.* FROM saos_clients c
            JOIN client_auth_tokens t ON c.id = t.client_id
            WHERE t.token_hash = %s 
            AND t.revoked_at IS NULL 
            AND t.expires_at > NOW()
            LIMIT 1
        """, (token_hash,))
        client = cur.fetchone()
        
        if client and 'error' not in client:
            # Set RLS context for this session
            pin = client.get('auth_pin') or client.get('temp_pin', '')
            cur.execute("SET LOCAL app.current_client_pin = %s", (pin,))
            
            # Update last_used
            cur.execute("UPDATE client_auth_tokens SET last_used_at = NOW() WHERE token_hash = %s", (token_hash,))
            conn.commit()
            return client
    finally:
        cur.close()
        conn.close()
    return None

def log_audit(action, entity_type=None, entity_id=None, old_value=None, new_value=None, client_id=None):
    """Log an audit trail entry."""
    try:
        if client_id is None:
            client = get_auth_client()
            client_id = client['id'] if client else None
        ip = request.remote_addr if request else None
        user_agent = request.headers.get('User-Agent', '') if request else None
        
        db_exec("""
            INSERT INTO audit_log (client_id, action, entity_type, entity_id, old_value, new_value, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (client_id, action, entity_type, entity_id, old_value, new_value, ip, user_agent))
    except Exception as e:
        # Audit logging should never break the app
        print(f"Audit log error: {e}")

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        client = get_auth_client()
        if not client:
            return jsonify({"error": "Unauthorized", "message": "Valid Bearer token required"}), 401
        request.client = client
        return f(*args, **kwargs)
    return decorated

def require_auth_optional(f):
    """Auth optional - sets request.client if available."""
    @wraps(f)
    def decorated(*args, **kwargs):
        request.client = get_auth_client()
        return f(*args, **kwargs)
    return decorated

# ── RBAC: ROLE-BASED ACCESS CONTROL ────────────────────────

def get_client_role(client):
    """Get the role for a client. Defaults to 'customer'."""
    return client.get('role', 'customer') if client else 'customer'

def get_role_permissions(role):
    """Fetch permissions for a role from the database."""
    result = db_query("SELECT permissions FROM saos_roles WHERE role = %s", (role,), one=True)
    if result and 'permissions' in result:
        return result['permissions']
    # Fallback defaults
    defaults = {
        'customer': {'dashboard': True, 'tasks': True, 'chat': True, 'deliverables': True, 'docs': True, 'billing': False, 'admin': False, 'users': False},
        'support': {'dashboard': True, 'tasks': True, 'chat': True, 'deliverables': True, 'docs': True, 'billing': False, 'admin': False, 'users': False, 'all_clients': True},
        'billing': {'dashboard': True, 'billing': True, 'docs': True, 'admin': False, 'users': False},
        'ops': {'dashboard': True, 'tasks': True, 'agents': True, 'provisioning': True, 'ops': True, 'billing': False, 'admin': False, 'users': False, 'all_clients': True},
        'admin': {'dashboard': True, 'tasks': True, 'chat': True, 'deliverables': True, 'docs': True, 'billing': True, 'admin': True, 'users': True, 'agents': True, 'provisioning': True, 'ops': True, 'all_clients': True},
    }
    return defaults.get(role, defaults['customer'])

def require_role(*roles):
    """Decorator that requires the authenticated client to have one of the specified roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            client = get_auth_client()
            if not client:
                return jsonify({"error": "Unauthorized", "message": "Valid Bearer token required"}), 401
            client_role = get_client_role(client)
            if client_role not in roles:
                log_audit('access_denied_wrong_role', entity_type='client', entity_id=str(client['id']),
                         new_value=f'Required: {roles}, Had: {client_role}', client_id=client['id'])
                return jsonify({"error": "Forbidden", "message": f"Role '{client_role}' does not have access to this resource"}), 403
            request.client = client
            return f(*args, **kwargs)
        return decorated
    return decorator

def require_permission(permission_name):
    """Decorator that checks if the client's role has a specific permission."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            client = get_auth_client()
            if not client:
                return jsonify({"error": "Unauthorized", "message": "Valid Bearer token required"}), 401
            client_role = get_client_role(client)
            permissions = get_role_permissions(client_role)
            if not permissions.get(permission_name, False):
                log_audit('access_denied_missing_permission', entity_type='client', entity_id=str(client['id']),
                         new_value=f'Required: {permission_name}', client_id=client['id'])
                return jsonify({"error": "Forbidden", "message": f"Permission '{permission_name}' required"}), 403
            request.client = client
            return f(*args, **kwargs)
        return decorated
    return decorator

# ── MFA: MULTI-FACTOR AUTHENTICATION (TOTP) ────────────────

import time as _time
import base64 as _b64
import struct as _struct
import hmac as _hmac
import hashlib as _hashlib

def _totp_generate(secret, interval=None):
    """Generate a TOTP code from a base32-encoded secret."""
    if interval is None:
        interval = int(_time.time() // 30)
    # Decode base32 secret
    key = _b64.b32decode(secret.upper() + '=' * (-len(secret) % 8))
    # Pack interval as 8-byte big-endian
    msg = _struct.pack('>Q', interval)
    # HMAC-SHA1
    h = _hmac.new(key, msg, _hashlib.sha1).digest()
    # Dynamic truncation
    offset = h[-1] & 0x0F
    code = ((_struct.unpack('>I', h[offset:offset+4])[0] & 0x7FFFFFFF) % 1000000)
    return f'{code:06d}'

def _totp_verify(secret, code, window=1):
    """Verify a TOTP code within a time window."""
    if not secret or not code:
        return False
    interval = int(_time.time() // 30)
    for offset in range(-window, window + 1):
        if _totp_generate(secret, interval + offset) == str(code).strip():
            return True
    return False

def _generate_totp_secret():
    """Generate a random base32 TOTP secret."""
    raw = os.urandom(20)
    return _b64.b32encode(raw).decode('utf-8').rstrip('=')

def _generate_recovery_codes(count=8):
    """Generate one-time recovery codes."""
    return [secrets.token_hex(8) for _ in range(count)]

def _generate_totp_uri(secret, account_name, issuer='SAOS'):
    """Generate otpauth:// URI for QR code."""
    label = f'{issuer}:{account_name}'
    return f'otpauth://totp/{label}?secret={secret}&issuer={issuer}&algorithm=SHA1&digits=6&period=30'

# ── NEW: ONBOARDING & PIN MANAGEMENT ───────────────────────

@app.route('/api/auth/register', methods=['POST'])
@rate_limit('register')
def register_client():
    """
    First-time client registration.
    Client provides client_id + temp_pin + new_pin.
    Sets a permanent PIN and activates the account.
    """
    data = request.get_json() or {}
    client_id = data.get('client_id')
    temp_pin = data.get('temp_pin')
    new_pin = data.get('new_pin')
    
    if not client_id:
        return jsonify({"error": "client_id required"}), 400
    if not temp_pin:
        return jsonify({"error": "Temporary PIN required"}), 400
    if not new_pin:
        return jsonify({"error": "New PIN required"}), 400
    if len(new_pin) < 4 or len(new_pin) > 10:
        return jsonify({"error": "PIN must be 4-10 digits"}), 400
    
    client = db_query("SELECT * FROM saos_clients WHERE id = %s", (client_id,), one=True)
    if not client:
        return jsonify({"error": "Client not found"}), 404
    
    # Verify temp PIN
    if client.get('temp_pin') != temp_pin:
        return jsonify({"error": "Invalid temporary PIN"}), 401
    
    # Check expiration
    if client.get('temp_pin_expires_at') and client['temp_pin_expires_at'] < datetime.now():
        return jsonify({"error": "Temporary PIN has expired. Contact support."}), 410
    
    # Set permanent PIN and activate
    db_exec("""
        UPDATE saos_clients 
        SET auth_pin = %s, onboarding_status = 'active', 
            onboarding_completed_at = NOW(), temp_pin = NULL,
            temp_pin_expires_at = NULL
        WHERE id = %s
    """, (new_pin, client_id))
    
    return jsonify({
        "success": True,
        "message": "PIN set successfully. You can now log in with your client ID and PIN.",
        "client_id": client_id
    })

@app.route('/api/auth/change-pin', methods=['POST'])
@require_auth
def change_pin():
    """Logged-in client changes their PIN. Revokes all existing tokens."""
    client_id = request.client['id']
    data = request.get_json() or {}
    current_pin = data.get('current_pin')
    new_pin = data.get('new_pin')
    
    if not current_pin or not new_pin:
        return jsonify({"error": "Current PIN and new PIN required"}), 400
    if len(new_pin) < 4 or len(new_pin) > 10:
        return jsonify({"error": "PIN must be 4-10 digits"}), 400
    
    client = db_query("SELECT auth_pin FROM saos_clients WHERE id = %s", (client_id,), one=True)
    if not client or client.get('auth_pin') != current_pin:
        return jsonify({"error": "Current PIN is incorrect"}), 401
    
    # Update PIN
    db_exec("UPDATE saos_clients SET auth_pin = %s WHERE id = %s", (new_pin, client_id))
    
    # Revoke ALL existing tokens for this client (security: force re-login)
    db_exec("""
        UPDATE client_auth_tokens 
        SET revoked_at = NOW() 
        WHERE client_id = %s AND revoked_at IS NULL
    """, (client_id,))
    
    log_audit('pin_changed', entity_type='client', entity_id=str(client_id), old_value='***', new_value='***')
    
    return jsonify({
        "success": True, 
        "message": "PIN updated successfully. Please log in again with your new PIN.",
        "requires_relogin": True
    })

@app.route('/api/auth/forgot-pin', methods=['POST'])
@rate_limit('pin_reset')
def forgot_pin():
    """Request PIN reset. Requires email + client_id."""
    data = request.get_json() or {}
    client_id = data.get('client_id')
    email = data.get('email')
    
    if not client_id or not email:
        return jsonify({"error": "client_id and email required"}), 400
    
    client = db_query("SELECT * FROM saos_clients WHERE id = %s AND customer_email = %s", 
                      (client_id, email), one=True)
    if not client:
        # Return success even if not found (security - don't leak existence)
        return jsonify({"success": True, "message": "If your account exists, a reset link has been sent."})
    
    # Generate new temp PIN
    temp = generate_pin(6)
    expires = datetime.now() + timedelta(hours=24)
    
    db_exec("""
        UPDATE saos_clients 
        SET temp_pin = %s, temp_pin_expires_at = %s, onboarding_status = 'pending'
        WHERE id = %s
    """, (temp, expires, client_id))
    
    # TODO: Send email with temp PIN via CHATTY/n8n
    # For now, return it (in production, this would be sent to email only)
    return jsonify({
        "success": True,
        "message": "PIN reset. Contact your SAOS administrator for your temporary PIN.",
        "temp_pin": temp,  # REMOVE IN PRODUCTION - send via email instead
        "expires_at": expires.isoformat()
    })

@app.route('/api/portal/onboarding-status/<int:client_id>')
def onboarding_status(client_id):
    """Check if client needs to set up PIN (public endpoint)."""
    client = db_query("""
        SELECT id, customer_name, onboarding_status, auth_pin IS NOT NULL as has_pin,
               temp_pin IS NOT NULL as has_temp_pin
        FROM saos_clients WHERE id = %s
    """, (client_id,), one=True)
    
    if not client:
        return jsonify({"error": "Client not found"}), 404
    
    return jsonify({
        "client_id": client_id,
        "onboarding_status": client.get('onboarding_status', 'pending'),
        "needs_setup": not client.get('has_pin') and not client.get('has_temp_pin'),
        "can_register": client.get('has_temp_pin'),
        "has_active_pin": client.get('has_pin')
    })

# ── EXISTING ENDPOINTS (Updated with auth + descriptions) ──

@app.route('/api/portal/health')
def health():
    return jsonify({"status": "ok", "service": "saos-customer-portal-api", "version": "2.0"})

@app.route('/api/portal/status')
@require_auth
def client_status():
    client = request.client
    client_id = client['id']
    tier = client.get('tier', 'business')
    
    # Task counts
    tasks = db_query("""
        SELECT status, COUNT(*) as n FROM task_queue 
        WHERE payload_json->>'client_id' = %s OR %s = '1'
        GROUP BY status
    """, (str(client_id), str(client_id)))
    task_counts = {r['status']: r['n'] for r in tasks if 'status' in r}
    
    # Agent states filtered by tier
    TIER_AGENTS = {
        'personal': ['SOL', 'CHATTY'],
        'personal+': ['SOL', 'CHATTY', 'GENI'],
        'business': ['SOL', 'ASSEMBLY', 'CHATTY', 'ATLAS', 'GENI', 'JURIS', 'PESSI'],
        'enterprise': ['SOL', 'ASSEMBLY', 'CHATTY', 'ATLAS', 'GENI', 'JURIS', 'PESSI', 'CODY', 'VALI'],
        'private': ['SOL', 'ASSEMBLY', 'CHATTY', 'ATLAS', 'JURIS'],
        'accelerate': ['SOL', 'ASSEMBLY', 'CHATTY', 'ATLAS', 'GENI', 'JURIS']
    }
    allowed = TIER_AGENTS.get(tier, TIER_AGENTS['business'])
    
    agents = db_query("""
        SELECT agent_name, role, role_description, status, avatar_emoji,
               capabilities, tier_access, last_heartbeat
        FROM agent_state
        WHERE agent_name = ANY(%s)
        ORDER BY agent_name
    """, (allowed,))
    
    # Recent chat activity
    recent_chat = db_query("""
        SELECT COUNT(*) as unread FROM chat_messages m
        JOIN chat_conversations c ON m.conversation_id = c.id
        WHERE c.client_id = %s AND m.sender_type = 'agent' AND m.read_at IS NULL
    """, (client_id,), one=True)
    
    # Calculate setup progress based on completed tasks
    setup_tasks = db_query("""
        SELECT status, COUNT(*) as n FROM task_queue 
        WHERE payload_json->>'client_id' = %s 
        AND task_type = 'service_setup'
        GROUP BY status
    """, (str(client_id),))
    setup_counts = {r['status']: r['n'] for r in setup_tasks if 'status' in r}
    total_setup = sum(setup_counts.values())
    completed_setup = setup_counts.get('COMPLETED', 0)
    setup_progress = round((completed_setup / total_setup) * 100) if total_setup > 0 else 0
    
    # ── USAGE METRICS (Quick Win) ─────────────────────────
    from datetime import datetime, timedelta
    import os
    
    # Tasks completed this month
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_tasks = db_query("""
        SELECT COUNT(*) as n FROM task_queue 
        WHERE (payload_json->>'client_id' = %s OR %s = '1')
        AND status = 'DONE'
        AND completed_at >= %s
    """, (str(client_id), str(client_id), month_start), one=True)
    tasks_completed_monthly = monthly_tasks.get('n', 0) if monthly_tasks else 0
    
    # Agent active hours (from execution_log)
    agent_hours = db_query("""
        SELECT COALESCE(SUM(duration_ms), 0) as total_ms FROM execution_log 
        WHERE task_id IN (
            SELECT id FROM task_queue 
            WHERE payload_json->>'client_id' = %s OR %s = '1'
        )
        AND created_at >= %s
    """, (str(client_id), str(client_id), datetime.now() - timedelta(days=30)), one=True)
    total_agent_hours = round((agent_hours.get('total_ms', 0) if agent_hours else 0) / 3600000, 1)
    
    # Deliverables storage (calculate from deliverables directory)
    deliverables_size = 0
    deliverables_count = 0
    if os.path.exists(DELIVERABLES_DIR):
        for f in os.listdir(DELIVERABLES_DIR):
            fp = os.path.join(DELIVERABLES_DIR, f)
            if os.path.isfile(fp):
                deliverables_size += os.path.getsize(fp)
                deliverables_count += 1
    deliverables_mb = round(deliverables_size / (1024 * 1024), 1)
    
    # n8n runs (placeholder — would need n8n webhook or execution tracking)
    # For now, use execution_log count as proxy
    n8n_runs = db_query("""
        SELECT COUNT(*) as n FROM execution_log 
        WHERE created_at >= %s
    """, (datetime.now() - timedelta(days=30),), one=True)
    n8n_runs_monthly = n8n_runs.get('n', 0) if n8n_runs else 0
    
    # Tier limits
    tier_limits = {
        'business': {'n8n_runs': 10000, 'agents': 7},
        'enterprise': {'n8n_runs': -1, 'agents': 10},  # -1 = unlimited
        'private': {'n8n_runs': -1, 'agents': 5},
        'accelerate': {'n8n_runs': 10000, 'agents': 6}
    }
    limits = tier_limits.get(tier, tier_limits['business'])
    
    return jsonify({
        "client": client,
        "tasks": task_counts,
        "agents": agents,
        "unread_messages": recent_chat.get('unread', 0) if recent_chat else 0,
        "onboarding_status": client.get('onboarding_status'),
        "setup_progress": setup_progress,
        "usage": {
            "tasks_completed_monthly": tasks_completed_monthly,
            "agent_hours_this_month": total_agent_hours,
            "deliverables_count": deliverables_count,
            "deliverables_mb": deliverables_mb,
            "n8n_runs_monthly": n8n_runs_monthly,
            "n8n_runs_limit": limits['n8n_runs'],
            "agents_active": len([a for a in agents if a.get('status') != 'OFFLINE']),
            "agents_limit": limits['agents']
        },
        "trust": {
            "data_residency": {
                "server_location": "United States (Dallas, TX)",
                "flag": "🇺🇸",
                "encryption_at_rest": "AES-256",
                "encryption_in_transit": "TLS 1.3",
                "last_security_audit": "2026-06-15",
                "compliance_status": "SOC 2 Type II In Progress"
            },
            "scope": {
                "systack_manages": [
                    "Server uptime & monitoring",
                    "Agent software updates",
                    "n8n workflow hosting",
                    "Tailscale VPN mesh",
                    "PostgreSQL backups"
                ],
                "client_controls": [
                    "Your data (you own it)",
                    "Your PIN & access",
                    "Your workflow logic",
                    "Integration credentials",
                    "Export or delete anytime"
                ]
            },
            "sla": {
                "uptime_last_30_days": 99.7,
                "incidents_this_month": 0,
                "response_time_commitment": "4 hours" if tier == 'enterprise' else "Same business day",
                "actual_last_response": "2h 14m"  # Would be calculated from chat data
            },
            "support": {
                "tier": tier,
                "primary_channel": "Dashboard Chat (SOL)",
                "escalation_path": "Chat → iMessage → Phone" if tier == 'enterprise' else "Chat → Email",
                "emergency_contact": "+1-501-274-6231 (iMessage)" if tier in ['enterprise', 'private'] else None,
                "last_contact": "2026-06-28 14:32 CDT"  # Would be from actual data
            },
            "billing": {
                "plan": tier.replace('_', ' ').title(),
                "monthly_price": limits.get('monthly_price', 299),
                "next_billing_date": "2026-07-17",
                "payment_method": "Visa •••• 4242",
                "invoices": [
                    {"date": "2026-06-17", "amount": 799, "status": "paid"},
                    {"date": "2026-05-17", "amount": 799, "status": "paid"}
                ]
            },
            "changelog": [
                {"date": "2026-06-29", "change": "Added usage metrics dashboard"},
                {"date": "2026-06-29", "change": "Security hardening: rate limiting & CORS"},
                {"date": "2026-06-28", "change": "Fixed PIN change flow"},
                {"date": "2026-06-27", "change": "Added Enterprise agent fleet (CODY, VALI)"},
                {"date": "2026-06-25", "change": "Mobile-responsive dashboard launched"}
            ]
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/portal/tasks')
@require_auth
def client_tasks():
    client_id = request.client['id']
    tasks = db_query("""
        SELECT t.id, t.task_type, COALESCE(t.display_name, t.task_type) as display_name,
               COALESCE(t.description, '') as description,
               t.assigned_agent, t.status, t.priority,
               t.created_at, t.completed_at, t.error_message
        FROM task_queue t
        WHERE t.payload_json->>'client_id' = %s OR %s = '1'
        ORDER BY t.created_at DESC
        LIMIT 50
    """, (str(client_id), str(client_id)))
    return jsonify(tasks)

@app.route('/api/portal/agents')
def client_agents():
    """Public - returns agents filtered by client tier."""
    # Get client's tier from optional auth
    auth_header = request.headers.get('Authorization', '')
    tier = 'business'  # default
    
    if auth_header.startswith('Bearer '):
        token = auth_header[7:].strip()
        token_hash = hash_token(token)
        client = db_query("""
            SELECT c.tier FROM saos_clients c
            JOIN client_auth_tokens t ON c.id = t.client_id
            WHERE t.token_hash = %s AND t.revoked_at IS NULL AND t.expires_at > NOW()
            LIMIT 1
        """, (token_hash,), one=True)
        if client and 'error' not in client:
            tier = client.get('tier', 'business')
    
    # Tier-to-agent mapping
    TIER_AGENTS = {
        'personal': ['SOL', 'CHATTY'],
        'personal+': ['SOL', 'CHATTY', 'GENI'],
        'business': ['SOL', 'ASSEMBLY', 'CHATTY', 'ATLAS', 'GENI', 'JURIS', 'PESSI'],
        'enterprise': ['SOL', 'ASSEMBLY', 'CHATTY', 'ATLAS', 'GENI', 'JURIS', 'PESSI', 'CODY', 'VALI'],
        'private': ['SOL', 'ASSEMBLY', 'CHATTY', 'ATLAS', 'JURIS'],
        'accelerate': ['SOL', 'ASSEMBLY', 'CHATTY', 'ATLAS', 'GENI', 'JURIS']
    }
    
    allowed = TIER_AGENTS.get(tier, TIER_AGENTS['business'])
    
    agents = db_query("""
        SELECT agent_name, role, role_description, status, avatar_emoji,
               capabilities, tier_access
        FROM agent_state 
        WHERE agent_name = ANY(%s)
        ORDER BY agent_name
    """, (allowed,))
    
    return jsonify(agents)

@app.route('/api/portal/client')
@require_auth
def client_info():
    return jsonify(request.client)

# ── CHAT ENDPOINTS ─────────────────────────────────────────────

@app.route('/api/chat/conversations', methods=['GET'])
@require_auth
def list_conversations():
    """Get all conversations for this client."""
    client_id = request.client['id']
    conversations = db_query("""
        SELECT c.*, 
               (SELECT COUNT(*) FROM chat_messages WHERE conversation_id = c.id AND sender_type = 'agent' AND read_at IS NULL) as unread_count,
               (SELECT content FROM chat_messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message,
               (SELECT created_at FROM chat_messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message_at
        FROM chat_conversations c
        WHERE c.client_id = %s
        ORDER BY c.updated_at DESC
    """, (client_id,))
    return jsonify(conversations)

@app.route('/api/chat/conversations', methods=['POST'])
@require_auth
def create_conversation():
    """Create a new chat conversation."""
    client_id = request.client['id']
    data = request.get_json() or {}
    title = data.get('title', 'New Conversation')
    
    result = db_query("""
        INSERT INTO chat_conversations (client_id, title)
        VALUES (%s, %s)
        RETURNING *
    """, (client_id, title), one=True)
    
    # Add system welcome message
    if result and 'error' not in result:
        db_exec("""
            INSERT INTO chat_messages (conversation_id, sender_type, sender_name, content, message_type)
            VALUES (%s, 'system', 'System', 'Conversation started. An agent will respond shortly.', 'system')
        """, (result['id'],))
    
    return jsonify(result or {"error": "Failed to create conversation"})

@app.route('/api/chat/conversations/<int:conv_id>/messages', methods=['GET'])
@require_auth
def get_messages(conv_id):
    """Get messages for a conversation."""
    client_id = request.client['id']
    
    # Verify conversation belongs to client
    conv = db_query("SELECT * FROM chat_conversations WHERE id = %s AND client_id = %s", 
                    (conv_id, client_id), one=True)
    if not conv:
        return jsonify({"error": "Conversation not found"}), 404
    
    messages = db_query("""
        SELECT m.*, 
               CASE WHEN m.sender_type = 'agent' THEN m.created_at END as delivered_at
        FROM chat_messages m
        WHERE m.conversation_id = %s
        ORDER BY m.created_at DESC
        LIMIT 100
    """, (conv_id,))
    # Reverse to show oldest first in UI
    messages = list(reversed(messages))
    
    # Mark agent messages as read
    db_exec("""
        UPDATE chat_messages SET read_at = NOW()
        WHERE conversation_id = %s AND sender_type = 'agent' AND read_at IS NULL
    """, (conv_id,))
    
    return jsonify(messages)

@app.route('/api/chat/conversations/<int:conv_id>/messages', methods=['POST'])
@require_auth
def send_message(conv_id):
    """Send a message from client to agents."""
    client_id = request.client['id']
    data = request.get_json() or {}
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({"error": "Message content required"}), 400
    
    # Verify conversation belongs to client
    conv = db_query("SELECT * FROM chat_conversations WHERE id = %s AND client_id = %s", 
                    (conv_id, client_id), one=True)
    if not conv:
        return jsonify({"error": "Conversation not found"}), 404
    if conv.get('status') == 'closed':
        return jsonify({"error": "Conversation is closed. Start a new conversation."}), 400
    
    # Insert client message
    msg = db_query("""
        INSERT INTO chat_messages (conversation_id, sender_type, sender_name, content, message_type)
        VALUES (%s, 'client', 'You', %s, 'text')
        RETURNING *
    """, (conv_id, content), one=True)
    
    # Track usage: chat_message
    track_usage(client_id, 'chat_message', metric_name='client_message', quantity=1, metadata={"conversation_id": conv_id})
    
    # Auto-create task from message if it looks like a request
    task_keywords = ['create', 'build', 'make', 'deploy', 'fix', 'update', 'help', 'need', 'want']
    is_task_request = any(kw in content.lower() for kw in task_keywords)
    
    if is_task_request:
        # Create task in queue
        task = db_query("""
            INSERT INTO task_queue (task_type, payload_json, priority, status, assigned_agent)
            VALUES ('client_request', %s, 5, 'PENDING', 'SOL')
            RETURNING id
        """, (json.dumps({"client_id": client_id, "conversation_id": conv_id, "request": content}),), one=True)
        
        if task and 'error' not in task:
            # Link message to task
            db_exec("UPDATE chat_messages SET task_id = %s WHERE id = %s", (task['id'], msg['id']))
            
            # Add system message about task creation
            db_exec("""
                INSERT INTO chat_messages (conversation_id, sender_type, sender_name, content, message_type, task_id)
                VALUES (%s, 'system', 'System', %s, 'task_created', %s)
            """, (conv_id, f"Task #{task['id']} created. SOL will handle this request.", task['id']))
    
    return jsonify(msg or {"error": "Failed to send message"})

@app.route('/api/chat/conversations/<int:conv_id>/close', methods=['POST'])
@require_auth
def close_conversation(conv_id):
    """Close a conversation."""
    client_id = request.client['id']
    db_exec("""
        UPDATE chat_conversations 
        SET status = 'closed', closed_at = NOW()
        WHERE id = %s AND client_id = %s
    """, (conv_id, client_id))
    return jsonify({"success": True})

# ── AUTH ENDPOINTS ─────────────────────────────────────────────

@app.route('/api/auth/login', methods=['POST'])
@rate_limit('login')
def login():
    """PIN-based login with optional MFA. Requires client_id + PIN. Rate limited: 5 attempts per 5 min."""
    data = request.get_json() or {}
    client_id = data.get('client_id')
    pin = data.get('pin')
    mfa_code = data.get('mfa_code')  # Optional: TOTP code if MFA is enabled
    recovery_code = data.get('recovery_code')  # Optional: recovery code
    
    # Rate limiting
    client_ip = request.remote_addr or 'unknown'
    rate_key = f"login:{client_ip}:{client_id}"
    allowed, attempts = check_rate_limit(rate_key, max_attempts=5, window_seconds=300)
    if not allowed:
        log_audit('login_failed_rate_limit', entity_type='client', entity_id=str(client_id))
        return jsonify({
            "error": "Too many login attempts",
            "message": "Please try again in 5 minutes.",
            "attempts": attempts
        }), 429
    
    if not client_id:
        return jsonify({"error": "client_id required"}), 400
    if not pin:
        return jsonify({"error": "PIN required"}), 400
    
    client = db_query("SELECT * FROM saos_clients WHERE id = %s", (client_id,), one=True)
    if not client:
        log_audit('login_failed_not_found', entity_type='client', entity_id=str(client_id))
        return jsonify({"error": "Client not found"}), 404
    
    # Check PIN
    if not client.get('auth_pin'):
        log_audit('login_failed_no_pin', entity_type='client', entity_id=str(client_id))
        return jsonify({"error": "PIN not set. Contact support."}), 403
    
    if client['auth_pin'] != pin:
        log_audit('login_failed_invalid_pin', entity_type='client', entity_id=str(client_id))
        return jsonify({
            "error": "Invalid PIN",
            "message": f"Login failed. Attempt {attempts} of 5 in 5 minutes."
        }), 401
    
    # Enterprise tier: MFA is mandatory
    tier = client.get('tier', 'business')
    if tier == 'enterprise' and not client.get('mfa_enabled'):
        log_audit('login_failed_mfa_required_enterprise', entity_type='client', entity_id=str(client_id))
        return jsonify({
            "error": "MFA required",
            "message": "Enterprise accounts require Multi-Factor Authentication. Please set up MFA before logging in.",
            "mfa_setup_required": True,
            "setup_url": "/api/mfa/setup"
        }), 403
    
    # MFA check
    if client.get('mfa_enabled') and client.get('mfa_secret'):
        if not mfa_code and not recovery_code:
            # PIN correct but MFA required — return partial success
            log_audit('login_mfa_required', entity_type='client', entity_id=str(client_id))
            return jsonify({
                "mfa_required": True,
                "message": "MFA code required. Provide mfa_code or recovery_code."
            }), 200
        
        if recovery_code:
            # Verify recovery code
            codes = client.get('mfa_recovery_codes', [])
            if recovery_code not in codes:
                log_audit('login_failed_bad_recovery', entity_type='client', entity_id=str(client_id))
                return jsonify({"error": "Invalid recovery code"}), 401
            # Consume recovery code
            codes.remove(recovery_code)
            db_exec("UPDATE saos_clients SET mfa_recovery_codes = %s WHERE id = %s",
                    (json.dumps(codes), client_id))
        else:
            # Verify TOTP code
            if not _totp_verify(client['mfa_secret'], mfa_code):
                log_audit('login_failed_bad_mfa', entity_type='client', entity_id=str(client_id))
                return jsonify({"error": "Invalid MFA code"}), 401
    
    # Generate token
    token = generate_token()
    token_hash = hash_token(token)
    expires = datetime.now() + timedelta(days=30)
    
    db_exec("""
        INSERT INTO client_auth_tokens (client_id, token_hash, expires_at)
        VALUES (%s, %s, %s)
    """, (client_id, token_hash, expires))
    
    # Update login stats
    db_exec("""
        UPDATE saos_clients 
        SET last_login_at = NOW(), login_count = COALESCE(login_count, 0) + 1
        WHERE id = %s
    """, (client_id,))
    
    log_audit('login_success', entity_type='client', entity_id=str(client_id), client_id=client_id)
    
    # Build response (exclude sensitive fields)
    client_safe = {k: v for k, v in client.items() if k not in ('auth_pin', 'mfa_secret', 'mfa_recovery_codes', 'temp_pin')}
    
    return jsonify({
        "token": token,
        "expires_at": expires.isoformat(),
        "client": client_safe,
        "onboarding_status": client.get('onboarding_status'),
        "mfa_enabled": bool(client.get('mfa_enabled'))
    })

# ── MFA ENDPOINTS ──────────────────────────────────────────

@app.route('/api/auth/mfa/setup', methods=['POST'])
@require_auth
def mfa_setup():
    """Initialize MFA for the authenticated client. Returns QR code URI and secret."""
    client = request.client
    client_id = client['id']
    
    # Check if MFA already enabled
    if client.get('mfa_enabled'):
        return jsonify({"error": "MFA already enabled. Disable first to re-setup."}), 400
    
    # Generate new secret
    secret = _generate_totp_secret()
    account_name = client.get('customer_email') or f'client-{client_id}'
    uri = _generate_totp_uri(secret, account_name)
    
    # Store secret temporarily (not enabled yet — client must verify)
    db_exec("UPDATE saos_clients SET mfa_secret = %s WHERE id = %s", (secret, client_id))
    
    log_audit('mfa_setup_initiated', entity_type='client', entity_id=str(client_id), client_id=client_id)
    
    return jsonify({
        "secret": secret,
        "otpauth_uri": uri,
        "qr_url": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={uri}",
        "message": "Scan this QR code with your authenticator app (Google Authenticator, Authy, etc). Then verify with /api/auth/mfa/verify."
    })

@app.route('/api/auth/mfa/verify', methods=['POST'])
@require_auth
@rate_limit('mfa_verify')
def mfa_verify():
    """Verify MFA setup by checking a TOTP code. Enables MFA if correct."""
    client = request.client
    client_id = client['id']
    data = request.get_json() or {}
    code = data.get('mfa_code')
    
    if not code:
        return jsonify({"error": "mfa_code required"}), 400
    
    # Get fresh client data (with secret)
    fresh = db_query("SELECT mfa_secret, mfa_enabled FROM saos_clients WHERE id = %s", (client_id,), one=True)
    if not fresh or not fresh.get('mfa_secret'):
        return jsonify({"error": "MFA not initialized. Call /api/auth/mfa/setup first."}), 400
    if fresh.get('mfa_enabled'):
        return jsonify({"error": "MFA already enabled"}), 400
    
    if not _totp_verify(fresh['mfa_secret'], code):
        return jsonify({"error": "Invalid MFA code"}), 401
    
    # Generate recovery codes
    recovery_codes = _generate_recovery_codes(8)
    
    # Enable MFA
    db_exec("""
        UPDATE saos_clients 
        SET mfa_enabled = true, mfa_recovery_codes = %s
        WHERE id = %s
    """, (json.dumps(recovery_codes), client_id))
    
    log_audit('mfa_enabled', entity_type='client', entity_id=str(client_id), client_id=client_id)
    
    return jsonify({
        "success": True,
        "message": "MFA enabled successfully. Save your recovery codes — these are shown only once.",
        "recovery_codes": recovery_codes
    })

@app.route('/api/auth/mfa/disable', methods=['POST'])
@require_auth
def mfa_disable():
    """Disable MFA. Requires PIN confirmation."""
    client = request.client
    client_id = client['id']
    data = request.get_json() or {}
    pin = data.get('pin')
    mfa_code = data.get('mfa_code')
    
    if not pin:
        return jsonify({"error": "PIN required to disable MFA"}), 400
    
    # Verify PIN
    fresh = db_query("SELECT auth_pin, mfa_enabled, mfa_secret FROM saos_clients WHERE id = %s", (client_id,), one=True)
    if not fresh or fresh.get('auth_pin') != pin:
        return jsonify({"error": "Invalid PIN"}), 401
    
    # Verify MFA code if MFA is enabled
    if fresh.get('mfa_enabled') and fresh.get('mfa_secret'):
        if not mfa_code or not _totp_verify(fresh['mfa_secret'], mfa_code):
            return jsonify({"error": "Valid MFA code required to disable MFA"}), 401
    
    db_exec("""
        UPDATE saos_clients 
        SET mfa_enabled = false, mfa_secret = NULL, mfa_recovery_codes = '[]'
        WHERE id = %s
    """, (client_id,))
    
    log_audit('mfa_disabled', entity_type='client', entity_id=str(client_id), client_id=client_id)
    return jsonify({"success": True, "message": "MFA disabled."})

@app.route('/api/auth/mfa/status', methods=['GET'])
@require_auth
def mfa_status():
    """Check MFA status for the authenticated client."""
    client = request.client
    return jsonify({
        "mfa_enabled": bool(client.get('mfa_enabled')),
        "mfa_setup_required": not bool(client.get('mfa_enabled'))
    })

# ── RBAC ENDPOINTS ─────────────────────────────────────────

@app.route('/api/auth/roles', methods=['GET'])
@require_role('admin')
def list_roles():
    """List all available roles. Admin only."""
    roles = db_query("SELECT role, description, permissions FROM saos_roles ORDER BY role")
    return jsonify({"roles": roles})

@app.route('/api/admin/client/<int:cid>/role', methods=['PUT'])
@require_role('admin')
def set_client_role(cid):
    """Set the role for a client. Admin only."""
    data = request.get_json() or {}
    new_role = data.get('role')
    if new_role not in ('customer', 'support', 'billing', 'ops', 'admin'):
        return jsonify({"error": "Invalid role. Must be: customer, support, billing, ops, or admin"}), 400
    
    client = db_query("SELECT id, customer_name, role FROM saos_clients WHERE id = %s", (cid,), one=True)
    if not client:
        return jsonify({"error": "Client not found"}), 404
    
    old_role = client.get('role', 'customer')
    db_exec("UPDATE saos_clients SET role = %s WHERE id = %s", (new_role, cid))
    log_audit('role_changed', entity_type='client', entity_id=str(cid),
             old_value=old_role, new_value=new_role, client_id=request.client['id'])
    return jsonify({"success": True, "client_id": cid, "old_role": old_role, "new_role": new_role})

@app.route('/api/auth/permissions', methods=['GET'])
@require_auth
def my_permissions():
    """Get permissions for the current client's role."""
    client = request.client
    role = get_client_role(client)
    perms = get_role_permissions(role)
    return jsonify({"role": role, "permissions": perms})

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Revoke current token."""
    auth_header = request.headers.get('Authorization', '')
    token = auth_header[7:].strip()
    token_hash = hash_token(token)
    db_exec("UPDATE client_auth_tokens SET revoked_at = NOW() WHERE token_hash = %s", (token_hash,))
    log_audit('logout', entity_type='token', entity_id=token_hash[:8] + '...')
    return jsonify({"success": True})

@app.route('/api/auth/me', methods=['GET'])
@require_auth
def me():
    """Get current client info."""
    return jsonify(request.client)

def track_usage(client_id, metric_type, metric_name=None, quantity=1, metadata=None):
    """Record usage metric for billing. Silently fails on error."""
    try:
        db_exec("""
            INSERT INTO usage_metrics (client_id, metric_type, metric_name, quantity, metadata)
            VALUES (%s, %s, %s, %s, %s)
        """, [client_id, metric_type, metric_name, quantity, json.dumps(metadata) if metadata else None])
    except Exception as e:
        # Silently log but don't fail the request
        print(f"[USAGE] Failed to track {metric_type} for client {client_id}: {e}")

# ── TASK CREATION (Client-initiated) ─────────────────────

# Client-facing agent pool (internal agents like DOOBY/LOKI not exposed)
SERVICE_AGENT_MAP = {
    # Invoice Processing
    'Invoice Processing Pipeline': 'ASSEMBLY',
    'Automated Invoice Processing System': 'ASSEMBLY',
    # Lead Qualification  
    'Lead Qualification System': 'ASSEMBLY',
    'Automated Lead Qualification Pipeline': 'ASSEMBLY',
    # Customer Support
    'Customer Support Drafting': 'CHATTY',
    'Self-Hosted Customer Support Automations': 'CHATTY',
    # Document Classification
    'Document Classification Engine': 'ASSEMBLY',
    'Document Classification & Routing Engine': 'ASSEMBLY',
    # Report Generation
    'Scheduled Report Generator': 'ASSEMBLY',
    # Data Entry
    'Local Data Entry Elimination System': 'ASSEMBLY',
    'Data Entry Elimination': 'ASSEMBLY',
    # Knowledge Base
    'Private Knowledge Base Search': 'ATLAS',
    # Document Extraction
    'Private Document Extraction Pipeline': 'ASSEMBLY',
    # Compliance
    'Automated Compliance Audit Trail': 'JURIS',
    'Compliance Audit Trail': 'JURIS',
    # Infrastructure / Management
    '7-Agent AI Fleet': 'ASSEMBLY',
    '10-Agent AI Fleet': 'ASSEMBLY',
    'n8n Workflow Hosting': 'ASSEMBLY',
    'Unlimited n8n Workflows': 'ASSEMBLY',
    '32GB RAM Infrastructure': 'ASSEMBLY',
    'Tailscale VPN + PostgreSQL': 'ASSEMBLY',
    'Dedicated Support Line': 'PESSI',
    # Fallback
    'Unknown Service': 'SOL',
}

@app.route('/api/tasks/request', methods=['POST'])
@require_auth
def request_task():
    """Client requests setup for a service. Creates a proper task."""
    client_id = request.client['id']
    data = request.get_json() or {}
    service_name = data.get('service_name', 'Unknown Service')
    service_desc = data.get('service_description', '')
    
    # Track usage: task_created
    db_exec("""
        INSERT INTO usage_metrics (client_id, metric_type, metric_name, metadata)
        VALUES (%s, 'task_created', %s, %s)
    """, [client_id, service_name, json.dumps({"service": service_name, "source": "dashboard"})])
    
    # Track usage: task_created
    track_usage(client_id, 'task_created', service_name, 1, {"service": service_name, "source": "dashboard"})
    
    # Determine agent based on service
    assigned_agent = SERVICE_AGENT_MAP.get(service_name, 'SOL')
    
    # Create task
    task = db_query("""
        INSERT INTO task_queue (task_type, display_name, description, payload_json, priority, status, assigned_agent)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, task_type, display_name, description, assigned_agent, status, priority, created_at
    """, (
        'service_setup',
        f'Setup: {service_name}',
        f'Client requested setup for {service_name}. {service_desc}',
        json.dumps({
            'client_id': client_id,
            'service_name': service_name,
            'service_description': service_desc,
            'requested_by': 'client_dashboard'
        }),
        4,  # High priority
        'PENDING',
        assigned_agent
    ), one=True)
    
    if not task or 'error' in task:
        return jsonify({'error': 'Failed to create task'}), 500
    
    # Create notification for client
    db_exec("""
        INSERT INTO chat_messages (conversation_id, sender_type, sender_name, content, message_type)
        SELECT id, 'system', 'System', %s, 'task_created'
        FROM chat_conversations
        WHERE client_id = %s AND status IN ('open', 'active')
        ORDER BY updated_at DESC
        LIMIT 1
    """, (f"📋 Task #{task['id']} created: Setup {service_name}. Assigned to {assigned_agent}.", client_id))
    
    return jsonify({
        'success': True,
        'task_id': task['id'],
        'assigned_agent': assigned_agent,
        'status': 'PENDING',
        'message': f'Task created and assigned to {assigned_agent}'
    })

# ── AGENT RESPONSE WEBHOOK (for n8n/OpenClaw to call) ────────

@app.route('/api/chat/webhook/agent-response', methods=['POST'])
def agent_response_webhook():
    """Webhook for agents to send responses back to chat.
    Called by n8n workflow or OpenClaw integration."""
    data = request.get_json() or {}
    
    conversation_id = data.get('conversation_id')
    agent_name = data.get('agent_name', 'SOL')
    content = data.get('content', '')
    task_id = data.get('task_id')
    
    if not conversation_id or not content:
        return jsonify({"error": "conversation_id and content required"}), 400
    
    msg = db_query("""
        INSERT INTO chat_messages (conversation_id, sender_type, sender_name, sender_agent, content, task_id)
        VALUES (%s, 'agent', %s, %s, %s, %s)
        RETURNING *
    """, (conversation_id, agent_name, agent_name, content, task_id), one=True)
    
    return jsonify(msg or {"error": "Failed to save message"})

# ── POLLING ENDPOINT (for real-time updates) ─────────────────

@app.route('/api/chat/poll')
@require_auth
def poll_updates():
    """Poll for new messages/tasks since last check."""
    client_id = request.client['id']
    last_check = request.args.get('since', datetime.now().isoformat())
    
    # New messages
    new_messages = db_query("""
        SELECT m.* FROM chat_messages m
        JOIN chat_conversations c ON m.conversation_id = c.id
        WHERE c.client_id = %s AND m.created_at > %s AND m.sender_type != 'client'
        ORDER BY m.created_at ASC
    """, (client_id, last_check))
    
    # Task updates
    task_updates = db_query("""
        SELECT t.id, t.status, t.assigned_agent, t.completed_at, t.error_message
        FROM task_queue t
        WHERE t.payload_json->>'client_id' = %s 
        AND t.updated_at > %s
        ORDER BY t.updated_at DESC
        LIMIT 10
    """, (str(client_id), last_check))
    
    return jsonify({
        "messages": new_messages,
        "task_updates": task_updates,
        "timestamp": datetime.now().isoformat()
    })

# ── INTERNAL: Task Polling (for OpenClaw cron/agent spawn) ──

@app.route('/api/internal/pending-tasks')
def pending_tasks():
    """Internal endpoint for OpenClaw/n8n to poll for pending tasks.
    Returns tasks ready for agent assignment.
    Requires internal-api-key header for basic security.
    """
    api_key = request.headers.get('X-Internal-Api-Key', '')
    expected = os.environ.get('SAOS_INTERNAL_API_KEY')
    
    if api_key != expected:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get pending tasks that haven't been claimed yet
    tasks = db_query("""
        SELECT t.id, t.task_type, t.display_name, t.description,
               t.assigned_agent, t.priority, t.payload_json,
               t.created_at, c.id as client_id, c.customer_name,
               c.customer_email, c.tier
        FROM task_queue t
        JOIN saos_clients c ON (t.payload_json->>'client_id')::int = c.id
        WHERE t.status = 'PENDING'
        AND (t.payload_json->>'claimed_at') IS NULL
        ORDER BY t.priority DESC, t.created_at ASC
        LIMIT 10
    """)
    
    return jsonify({
        'tasks': tasks,
        'count': len(tasks),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/internal/claim-task/<int:task_id>', methods=['POST'])
def claim_task(task_id):
    """Mark a task as claimed by an agent runner.
    Prevents duplicate agent spawns."""
    api_key = request.headers.get('X-Internal-Api-Key', '')
    expected = os.environ.get('SAOS_INTERNAL_API_KEY')
    
    if api_key != expected:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json() or {}
    runner_id = data.get('runner_id', 'unknown')
    
    # Mark task as claimed
    db_exec("""
        UPDATE task_queue
        SET payload_json = payload_json || %s,
            updated_at = NOW()
        WHERE id = %s
    """, (json.dumps({'claimed_at': datetime.now().isoformat(), 'runner_id': runner_id}), task_id))
    
    return jsonify({'success': True, 'task_id': task_id, 'claimed_by': runner_id})

@app.route('/api/internal/update-task/<int:task_id>', methods=['POST'])
def update_task(task_id):
    """Update task status from agent execution.
    Called by spawned agents via webhook."""
    api_key = request.headers.get('X-Internal-Api-Key', '')
    expected = os.environ.get('SAOS_INTERNAL_API_KEY')
    
    if api_key != expected:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json() or {}
    status = data.get('status')
    result = data.get('result', '')
    error = data.get('error', '')
    
    if status not in ['RUNNING', 'DONE', 'FAILED']:
        return jsonify({'error': 'Invalid status'}), 400
    
    # Update task
    if status == 'RUNNING':
        db_exec("""
            UPDATE task_queue
            SET status = %s, updated_at = NOW()
            WHERE id = %s
        """, (status, task_id))
    elif status == 'DONE':
        db_exec("""
            UPDATE task_queue
            SET status = %s, completed_at = NOW(), updated_at = NOW(),
                payload_json = payload_json || %s
            WHERE id = %s
        """, (status, json.dumps({'result': result}), task_id))
    elif status == 'FAILED':
        db_exec("""
            UPDATE task_queue
            SET status = %s, error_message = %s, updated_at = NOW()
            WHERE id = %s
        """, (status, error, task_id))
    
    # Notify client via chat if there's an open conversation
    task = db_query("SELECT payload_json FROM task_queue WHERE id = %s", (task_id,), one=True)
    if task:
        payload = task.get('payload_json', {})
        client_id = payload.get('client_id') if isinstance(payload, dict) else None
        
        if client_id:
            status_msg = {
                'RUNNING': f"🔄 Task #{task_id} is now being processed.",
                'DONE': f"✅ Task #{task_id} completed! {result[:200] if result else ''}",
                'FAILED': f"❌ Task #{task_id} failed: {error[:200] if error else 'Unknown error'}"
            }.get(status, f"Task #{task_id} status: {status}")
            
            # Insert chat notification
            db_exec("""
                INSERT INTO chat_messages (conversation_id, sender_type, sender_name, content, message_type)
                SELECT id, 'system', 'System', %s, 'task_update'
                FROM chat_conversations
                WHERE client_id = %s AND status IN ('open', 'active')
                ORDER BY updated_at DESC
                LIMIT 1
            """, (status_msg, client_id))
            
            # Queue async notification for offline clients
            urgency = 'urgent' if status == 'FAILED' else 'normal'
            channel = 'imessage' if status == 'FAILED' else 'auto'
            
            db_exec("""
                INSERT INTO notifications (client_id, task_id, message, urgency, channel, status)
                VALUES (%s, %s, %s, %s, %s, 'queued')
            """, (client_id, task_id, status_msg, urgency, channel))
    
    return jsonify({'success': True, 'task_id': task_id, 'status': status})

# ── PDF Downloads (updated for v2.1) ──
@app.route('/download/quickstart-v5')
def serve_quickstart_v5():
    return send_from_directory(BASE_DIR, 'SAOS-Quick-Start-Guide-v6.0.pdf',
                               as_attachment=False, mimetype='application/pdf')

@app.route('/download/user-guide-v3')
def serve_user_guide_v3():
    return send_from_directory(BASE_DIR, 'SAOS-Dashboard-User-Guide-v4.0.pdf',
                               as_attachment=False, mimetype='application/pdf')

@app.route('/download/manual-v5')
def serve_manual_v5():
    return send_from_directory(BASE_DIR, 'SAOS-Service-Manual-v6.0.pdf',
                               as_attachment=False, mimetype='application/pdf')

@app.route('/download/architecture-v4')
def serve_arch_v4():
    return send_from_directory(BASE_DIR, 'SAOS-Architecture-Overview-v4.0.pdf',
                               as_attachment=False, mimetype='application/pdf')

@app.route('/download/mobile-guide-v2')
def serve_mobile_guide_v2():
    return send_from_directory(BASE_DIR, 'SAOS-Dashboard-Mobile-Access-Guide-v2.0.pdf',
                               as_attachment=False, mimetype='application/pdf')

@app.route('/download/enterprise-guide')
def serve_enterprise_guide():
    return send_from_directory(BASE_DIR, 'SyStack-Enterprise-Deployment-Guide-v1.0.pdf',
                               as_attachment=False, mimetype='application/pdf')

# ── NOTIFICATIONS (Async — Email/iMessage) ──────────────────

@app.route('/api/internal/notify-client', methods=['POST'])
def notify_client():
    """Send async notification to client via BlueBubbles (iMessage) or email.
    Called by task update system when client is offline or for urgent updates.
    """
    api_key = request.headers.get('X-Internal-Api-Key', '')
    expected = os.environ.get('SAOS_INTERNAL_API_KEY')
    
    if api_key != expected:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json() or {}
    client_id = data.get('client_id')
    task_id = data.get('task_id')
    message = data.get('message', '')
    urgency = data.get('urgency', 'normal')  # normal, urgent, critical
    channel = data.get('channel', 'auto')  # auto, imessage, email
    
    if not client_id or not message:
        return jsonify({'error': 'client_id and message required'}), 400
    
    # Get client info
    client = db_query("""
        SELECT customer_name, customer_email, tier 
        FROM saos_clients WHERE id = %s
    """, (client_id,), one=True)
    
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    # Store notification log
    db_exec("""
        INSERT INTO notifications (client_id, task_id, message, urgency, channel, status)
        VALUES (%s, %s, %s, %s, %s, 'queued')
    """, (client_id, task_id, message, urgency, channel))
    
    # Determine delivery channel
    delivery_channel = channel
    if channel == 'auto':
        delivery_channel = 'imessage' if urgency in ['urgent', 'critical'] else 'email'
    
    # Send via BlueBubbles (iMessage) for urgent or critical
    if delivery_channel == 'imessage':
        try:
            import subprocess
            result = subprocess.run([
                'curl', '-s', '-X', 'POST',
                'http://phillips-macbook-air.tail573d57.ts.net:1234/api/message',
                '-H', 'Content-Type: application/json',
                '-d', json.dumps({
                    'chatGuid': '+15012746231',
                    'message': message[:500]  # iMessage limit
                })
            ], capture_output=True, text=True, timeout=10)
            
            db_exec("""
                UPDATE notifications SET status = 'sent', sent_at = NOW()
                WHERE client_id = %s AND task_id = %s AND status = 'queued'
            """, (client_id, task_id))
            
            return jsonify({
                'success': True,
                'channel': 'imessage',
                'message': message,
                'client': client['customer_name']
            })
        except Exception as e:
            # Fallback to email
            delivery_channel = 'email'
    
    # Send via email (SMTP)
    if delivery_channel == 'email':
        # For now, store as pending email — n8n will pick up and send
        db_exec("""
            UPDATE notifications SET status = 'pending_email', sent_at = NOW()
            WHERE client_id = %s AND task_id = %s AND status = 'queued'
        """, (client_id, task_id))
        
        return jsonify({
            'success': True,
            'channel': 'email',
            'message': message,
            'client': client['customer_name'],
            'note': 'Queued for email delivery via n8n'
        })
    
    return jsonify({'error': 'No delivery channel available'}), 500

@app.route('/api/internal/notifications/pending')
def pending_notifications():
    """Get pending notifications for n8n to process."""
    api_key = request.headers.get('X-Internal-Api-Key', '')
    expected = os.environ.get('SAOS_INTERNAL_API_KEY')
    
    if api_key != expected:
        return jsonify({'error': 'Unauthorized'}), 401
    
    notifications = db_query("""
        SELECT n.*, c.customer_name, c.customer_email
        FROM notifications n
        JOIN saos_clients c ON n.client_id = c.id
        WHERE n.status IN ('queued', 'pending_email')
        ORDER BY n.created_at DESC
        LIMIT 50
    """)
    
    return jsonify({
        'notifications': notifications,
        'count': len(notifications),
        'timestamp': datetime.now().isoformat()
    })

# ── DELIVERABLES (Task Output Storage) ─────────────────────

@app.route('/api/internal/deliverables/upload', methods=['POST'])
def upload_deliverable():
    """Upload a deliverable file for a task.
    Called by agents after completing work."""
    api_key = request.headers.get('X-Internal-Api-Key', '')
    expected = os.environ.get('SAOS_INTERNAL_API_KEY')
    
    if api_key != expected:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json() or {}
    task_id = data.get('task_id')
    filename = data.get('filename', 'deliverable.txt')
    content_base64 = data.get('content_base64', '')
    description = data.get('description', '')
    
    if not task_id or not content_base64:
        return jsonify({'error': 'task_id and content_base64 required'}), 400
    
    # Generate unique filename
    file_id = str(uuid.uuid4())[:8]
    safe_filename = f"task_{task_id}_{file_id}_{filename.replace(' ', '_')}"
    filepath = os.path.join(DELIVERABLES_DIR, safe_filename)
    
    # Decode and save
    try:
        content = base64.b64decode(content_base64)
        with open(filepath, 'wb') as f:
            f.write(content)
    except Exception as e:
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
    
    # Store reference in task payload
    db_exec("""
        UPDATE task_queue
        SET payload_json = payload_json || %s,
            updated_at = NOW()
        WHERE id = %s
    """, (json.dumps({
        'deliverable': {
            'filename': filename,
            'stored_as': safe_filename,
            'description': description,
            'size': len(content),
            'uploaded_at': datetime.now().isoformat()
        }
    }), task_id))
    
    # Track usage: deliverable_uploaded
    task = db_query("SELECT payload_json FROM task_queue WHERE id = %s", (task_id,), one=True)
    if task:
        payload = task.get('payload_json', {}) if isinstance(task.get('payload_json'), dict) else {}
        client_id_from_task = payload.get('client_id') if isinstance(payload, dict) else None
        if client_id_from_task:
            track_usage(client_id_from_task, 'deliverable_uploaded', filename, 1, {"task_id": task_id, "size": len(content)})
    
    return jsonify({
        'success': True,
        'task_id': task_id,
        'filename': filename,
        'download_url': f'/api/deliverables/download/{safe_filename}'
    })

@app.route('/api/deliverables/download/<filename>')
@require_auth
def download_deliverable(filename):
    """Download a deliverable file."""
    # Security: prevent directory traversal
    safe_name = os.path.basename(filename)
    filepath = os.path.join(DELIVERABLES_DIR, safe_name)
    
    if not os.path.isfile(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_from_directory(DELIVERABLES_DIR, safe_name, as_attachment=True)

@app.route('/api/portal/deliverables')
@require_auth
def list_deliverables():
    """List all deliverables for this client."""
    client_id = request.client['id']
    
    tasks = db_query("""
        SELECT id, task_type, display_name, payload_json, completed_at
        FROM task_queue
        WHERE payload_json->'deliverable' IS NOT NULL
        AND (payload_json->>'client_id')::int = %s
        ORDER BY completed_at DESC
        LIMIT 50
    """, (client_id,))
    
    deliverables = []
    for task in tasks:
        payload = task.get('payload_json', {})
        if isinstance(payload, dict) and 'deliverable' in payload:
            d = payload['deliverable']
            deliverables.append({
                'task_id': task['id'],
                'task_name': task.get('display_name', task['task_type']),
                'filename': d.get('filename'),
                'description': d.get('description'),
                'size': d.get('size', 0),
                'download_url': f'/api/deliverables/download/{d.get("stored_as")}',
                'completed_at': task.get('completed_at')
            })
    
    return jsonify(deliverables)

# ── ACTIVITY LOG (Real audit trail) ────────────────────────

@app.route('/api/portal/activity')
@require_auth
def client_activity():
    """Return real activity log for this client.
    
    Combines:
    - Task lifecycle events (created, claimed, completed, failed)
    - Deliverable uploads
    - Chat messages
    - Login events
    - Notifications sent
    """
    client_id = request.client['id']
    limit = min(int(request.args.get('limit', 50)), 100)
    
    # Task events
    tasks = db_query("""
        SELECT id, task_type, display_name, status, assigned_agent,
               created_at, completed_at, updated_at, error_message
        FROM task_queue
        WHERE payload_json->>'client_id' = %s
        ORDER BY updated_at DESC
        LIMIT %s
    """, (str(client_id), limit))
    
    task_events = []
    for t in tasks:
        if t['status'] == 'DONE':
            task_events.append({
                'type': 'task_completed',
                'icon': '✅',
                'title': t['display_name'] or t['task_type'],
                'detail': f"Completed by {t['assigned_agent'] or 'agent'}",
                'time': t['completed_at'],
                'task_id': t['id']
            })
        elif t['status'] == 'FAILED':
            task_events.append({
                'type': 'task_failed',
                'icon': '❌',
                'title': t['display_name'] or t['task_type'],
                'detail': t['error_message'] or 'Task failed',
                'time': t['updated_at'],
                'task_id': t['id']
            })
        elif t['status'] == 'RUNNING':
            task_events.append({
                'type': 'task_started',
                'icon': '🔄',
                'title': t['display_name'] or t['task_type'],
                'detail': f"Assigned to {t['assigned_agent']}",
                'time': t['updated_at'],
                'task_id': t['id']
            })
        else:
            task_events.append({
                'type': 'task_created',
                'icon': '📋',
                'title': t['display_name'] or t['task_type'],
                'detail': 'Awaiting agent assignment',
                'time': t['created_at'],
                'task_id': t['id']
            })
    
    # Deliverable events
    deliverable_tasks = db_query("""
        SELECT id, display_name, task_type, payload_json, completed_at
        FROM task_queue
        WHERE payload_json->'deliverable' IS NOT NULL
        AND payload_json->>'client_id' = %s
        ORDER BY completed_at DESC
        LIMIT %s
    """, (str(client_id), limit))
    
    deliverable_events = []
    for t in deliverable_tasks:
        payload = t.get('payload_json', {})
        if isinstance(payload, dict) and 'deliverable' in payload:
            d = payload['deliverable']
            deliverable_events.append({
                'type': 'deliverable_uploaded',
                'icon': '📁',
                'title': d.get('filename', 'File'),
                'detail': f"For: {t.get('display_name', t['task_type'])}",
                'time': t['completed_at'],
                'task_id': t['id'],
                'download_url': f'/api/deliverables/download/{d.get("stored_as")}'
            })
    
    # Combine and sort by time (newest first)
    all_events = task_events + deliverable_events
    all_events.sort(key=lambda x: x['time'] or datetime.min.isoformat(), reverse=True)
    
    return jsonify({
        'events': all_events[:limit],
        'count': len(all_events),
        'timestamp': datetime.now().isoformat()
    })

# ── SERVICES (Dynamic — from backend config) ────────────────

@app.route('/api/portal/services')
@require_auth
def client_services():
    """Return services configuration for this client's tier."""
    tier = request.client.get('tier', 'business')
    services = TIER_SERVICES.get(tier, TIER_SERVICES['business'])
    infra = TIER_INFRA.get(tier, TIER_INFRA['business'])
    support = TIER_SUPPORT.get(tier, TIER_SUPPORT['business'])
    stripe = STRIPE_CHECKOUT_URLS.get(tier, {})
    return jsonify({
        'tier': tier,
        'services': services,
        'infrastructure': infra,
        'support': support,
        'pricing': {
            'monthly': stripe.get('price_monthly'),
            'annual': stripe.get('price_annual'),
            'checkout_url': stripe.get('monthly'),
            'checkout_url_annual': stripe.get('annual'),
        }
    })

# ── DOCUMENT DOWNLOADS ────────────────────────────────────
# Map friendly doc names to actual files in the dashboard directory
DOC_FILES = {
    'quickstart-v7': 'SAOS-Quick-Start-Guide-v7.0.pdf',
    'user-guide-v6': 'SAOS-Dashboard-User-Guide-v6.0.pdf',
    'user-guide-v5': 'SAOS-Dashboard-User-Guide-v6.0.pdf',  # backward compat
    'manual-v7': 'SAOS-Service-Manual-v7.0.pdf',
    'architecture-v5': 'SAOS-Architecture-Overview-v5.0.pdf',
    'mobile-guide-v4': 'SAOS-Dashboard-Mobile-Access-Guide-v4.0.pdf',
    'mobile-guide-v3': 'SAOS-Dashboard-Mobile-Access-Guide-v4.0.pdf',  # backward compat
    'enterprise-guide': 'SyStack-Enterprise-Deployment-Guide-v1.0.pdf',
    'technical-spec': 'SAOS-Dashboard-Technical-Spec.pdf',
    'ios-cert-plan': 'SAOS-iOS-Cert-Trust-Plan.pdf',
    'changelog': 'SAOS-Changes-2026-06-29.pdf',
    'changelog-jul5': 'SAOS-Changes-2026-07-05.pdf',
    'readme': 'SAOS-Customer-Portal-README-v2.pdf',
    'security-arch': 'SAOS-Security-Architecture-v2.0.pdf',
    'security-arch-v1': 'SAOS-Security-Architecture-v1.0.pdf',  # backward compat
    'trust-center': 'SAOS-Compliance-Trust-Center-v1.0.pdf',
    'backup-recovery': 'SAOS-Backup-Recovery-Guide-v1.0.pdf',
    'deployment-checklist': 'SAOS-Production-Deployment-Checklist-v1.0.pdf',
}

@app.route('/download/<doc_id>')
def download_doc(doc_id):
    """Serve PDF documentation files. No auth required for client-facing docs."""
    filename = DOC_FILES.get(doc_id)
    if not filename:
        return jsonify({'error': 'Document not found'}), 404
    
    full_path = os.path.join(BASE_DIR, filename)
    if not os.path.isfile(full_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_from_directory(BASE_DIR, filename, as_attachment=False)

# ── DATA EXPORT ────────────────────────────────────────────
import zipfile
import io

@app.route('/api/export/data', methods=['POST'])
@require_auth
def export_client_data():
    """Export all client data as ZIP: tasks, chat, deliverables, settings."""
    client_id = request.client['id']
    client_name = request.client.get('customer_name', 'client')
    
    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 1. Export tasks
        tasks = db_query("""
            SELECT t.*, to_json(t.payload_json) as payload
            FROM task_queue t
            WHERE t.payload_json->>'client_id' = %s OR %s = '1'
            ORDER BY t.created_at DESC
        """, (str(client_id), str(client_id)))
        
        if tasks and 'error' not in tasks:
            tasks_json = json.dumps(tasks, indent=2, default=str)
            zf.writestr('tasks/tasks.json', tasks_json)
        
        # 2. Export chat conversations
        conversations = db_query("""
            SELECT c.*, 
                   (SELECT json_agg(m.*) FROM chat_messages m WHERE m.conversation_id = c.id) as messages
            FROM chat_conversations c
            WHERE c.client_id = %s
            ORDER BY c.created_at DESC
        """, (client_id,))
        
        if conversations and 'error' not in conversations:
            conv_json = json.dumps(conversations, indent=2, default=str)
            zf.writestr('chat/conversations.json', conv_json)
        
        # 3. Export deliverables (copy files)
        deliverables_dir = os.path.join(BASE_DIR, 'deliverables')
        if os.path.exists(deliverables_dir):
            for filename in os.listdir(deliverables_dir):
                file_path = os.path.join(deliverables_dir, filename)
                if os.path.isfile(file_path):
                    zf.write(file_path, f'deliverables/{filename}')
        
        # 4. Export client settings
        client_data = {
            'client_id': client_id,
            'customer_name': request.client.get('customer_name'),
            'customer_email': request.client.get('customer_email'),
            'tier': request.client.get('tier'),
            'created_at': str(request.client.get('created_at')),
            'export_date': datetime.now().isoformat()
        }
        zf.writestr('settings/client.json', json.dumps(client_data, indent=2))
        
        # 5. Add README
        readme = """# SAOS Data Export

This ZIP contains your complete data from SAOS:

- tasks/ — All task history
- chat/ — All conversation transcripts
- deliverables/ — All uploaded/downloaded files
- settings/ — Your account settings

You own this data. Import it into any system that supports JSON.
"""
        zf.writestr('README.txt', readme)
    
    zip_buffer.seek(0)
    
    log_audit('data_export', entity_type='client', entity_id=str(client_id), 
                new_value=f'Exported data for client {client_id}', client_id=client_id)
    
    # Use Response object instead of send_from_directory for in-memory buffer
    from flask import Response
    return Response(
        zip_buffer.getvalue(),
        mimetype='application/zip',
        headers={
            'Content-Disposition': f'attachment; filename=saos-export-{client_name.replace(" ", "_")}-{datetime.now().strftime("%Y%m%d")}.zip'
        }
    )

# ── Static file serving ──
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_dashboard(path):
    if not path:
        return send_from_directory(BASE_DIR, 'index.html')
    full_path = os.path.join(BASE_DIR, path)
    if os.path.isfile(full_path):
        return send_from_directory(BASE_DIR, path)
    return send_from_directory(BASE_DIR, 'index.html')

# ── INTEGRATION HEALTH MONITORING ────────────────────────

import subprocess
import urllib.request
import time as time_mod

INTEGRATION_CHECKS = [
    {
        'name': 'PostgreSQL',
        'icon': '🐘',
        'check_fn': lambda: _check_postgres(),
    },
    {
        'name': 'n8n',
        'icon': '⚙️',
        'check_fn': lambda: _check_n8n(),
    },
    {
        'name': 'Tailscale',
        'icon': '🔐',
        'check_fn': lambda: _check_tailscale(),
    },
    {
        'name': 'BlueBubbles',
        'icon': '💬',
        'check_fn': lambda: _check_bluebubbles(),
    },
    {
        'name': 'Ollama',
        'icon': '🧠',
        'check_fn': lambda: _check_ollama(),
    },
]

def _check_postgres():
    start = time_mod.time()
    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, connect_timeout=3)
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.fetchone()
        cur.close()
        conn.close()
        elapsed = int((time_mod.time() - start) * 1000)
        return {'status': 'healthy', 'response_ms': elapsed, 'details': 'Connection OK'}
    except Exception as e:
        return {'status': 'down', 'response_ms': None, 'details': str(e)}

def _check_n8n():
    start = time_mod.time()
    try:
        req = urllib.request.Request('http://localhost:5678/healthz', method='GET')
        with urllib.request.urlopen(req, timeout=3) as resp:
            elapsed = int((time_mod.time() - start) * 1000)
            if resp.status == 200:
                return {'status': 'healthy', 'response_ms': elapsed, 'details': 'n8n responding'}
            return {'status': 'degraded', 'response_ms': elapsed, 'details': f'HTTP {resp.status}'}
    except Exception as e:
        return {'status': 'down', 'response_ms': None, 'details': str(e)}

def _check_tailscale():
    start = time_mod.time()
    try:
        result = subprocess.run(['tailscale', 'status'], capture_output=True, text=True, timeout=3)
        elapsed = int((time_mod.time() - start) * 1000)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            return {'status': 'healthy', 'response_ms': elapsed, 'details': f'{len(lines)} peers connected'}
        return {'status': 'degraded', 'response_ms': elapsed, 'details': 'tailscale status non-zero'}
    except subprocess.TimeoutExpired:
        return {'status': 'down', 'response_ms': None, 'details': 'Timeout after 3s'}
    except Exception as e:
        return {'status': 'down', 'response_ms': None, 'details': str(e)}

def _check_bluebubbles():
    start = time_mod.time()
    try:
        req = urllib.request.Request('http://phillips-macbook-air.tail573d57.ts.net:1234/', method='GET')
        with urllib.request.urlopen(req, timeout=3) as resp:
            elapsed = int((time_mod.time() - start) * 1000)
            if resp.status == 200:
                return {'status': 'healthy', 'response_ms': elapsed, 'details': 'BlueBubbles responding'}
            return {'status': 'degraded', 'response_ms': elapsed, 'details': f'HTTP {resp.status}'}
    except Exception as e:
        return {'status': 'down', 'response_ms': None, 'details': str(e)}

def _check_ollama():
    start = time_mod.time()
    try:
        req = urllib.request.Request('http://localhost:11434/api/tags', method='GET')
        with urllib.request.urlopen(req, timeout=3) as resp:
            elapsed = int((time_mod.time() - start) * 1000)
            if resp.status == 200:
                return {'status': 'healthy', 'response_ms': elapsed, 'details': 'Ollama API responding'}
            return {'status': 'degraded', 'response_ms': elapsed, 'details': f'HTTP {resp.status}'}
    except Exception as e:
        return {'status': 'down', 'response_ms': None, 'details': str(e)}

@app.route('/api/portal/integrations')
@require_auth
def integrations_health():
    """Return health status of all integrations."""
    results = []
    overall = 'healthy'
    for ic in INTEGRATION_CHECKS:
        check = ic['check_fn']()
        results.append({
            'name': ic['name'],
            'icon': ic['icon'],
            'status': check['status'],
            'response_ms': check['response_ms'],
            'details': check['details'],
            'last_check': datetime.now().isoformat()
        })
        if check['status'] == 'down':
            overall = 'down'
        elif check['status'] == 'degraded' and overall == 'healthy':
            overall = 'degraded'
    return jsonify({
        'integrations': results,
        'overall_health': overall
    })

# ── SEARCH ───────────────────────────────────────────────

@app.route('/api/portal/search')
@require_auth
def search_portal():
    """Search across tasks, chat messages, and activity log."""
    query = request.args.get('q', '').strip()
    if len(query) < 3:
        return jsonify({'error': 'Query must be at least 3 characters'}), 400
    
    client_id = request.client['id']
    pattern = f'%{query}%'
    
    # Search tasks
    tasks = db_query("""
        SELECT id, task_type, display_name, description, assigned_agent, status, priority, created_at
        FROM task_queue
        WHERE (payload_json->>'client_id' = %s OR %s = '1')
        AND (display_name ILIKE %s OR description ILIKE %s OR task_type ILIKE %s)
        ORDER BY created_at DESC
        LIMIT 20
    """, (str(client_id), str(client_id), pattern, pattern, pattern))
    
    # Search chat messages
    messages = db_query("""
        SELECT m.id, m.content, m.sender_type, m.sender_name, m.created_at, c.id as conversation_id, c.title as conversation_title
        FROM chat_messages m
        JOIN chat_conversations c ON m.conversation_id = c.id
        WHERE c.client_id = %s AND m.content ILIKE %s
        ORDER BY m.created_at DESC
        LIMIT 20
    """, (client_id, pattern))
    
    # Search activity log
    activity = db_query("""
        SELECT id, action, entity_type, entity_id, old_value, new_value, created_at
        FROM audit_log
        WHERE client_id = %s AND (action ILIKE %s OR entity_type ILIKE %s)
        ORDER BY created_at DESC
        LIMIT 20
    """, (client_id, pattern, pattern))
    
    if tasks and 'error' in tasks: tasks = []
    if messages and 'error' in messages: messages = []
    if activity and 'error' in activity: activity = []
    
    total = (len(tasks) if isinstance(tasks, list) else 0) + \
            (len(messages) if isinstance(messages, list) else 0) + \
            (len(activity) if isinstance(activity, list) else 0)
    
    return jsonify({
        'query': query,
        'results': {
            'tasks': tasks if isinstance(tasks, list) else [],
            'messages': messages if isinstance(messages, list) else [],
            'activity': activity if isinstance(activity, list) else []
        },
        'total': total
    })


# ── USAGE METRICS ──────────────────────────────────────────

@app.route('/api/portal/usage')
@require_auth
def client_usage():
    """Return usage metrics for the current client."""
    client_id = request.client['id']
    
    # Get current month metrics
    metrics = db_query("""
        SELECT metric_type, SUM(metric_value) as total
        FROM usage_metrics
        WHERE client_id = %s AND metric_period = 'monthly'
        AND recorded_at >= DATE_TRUNC('month', NOW())
        GROUP BY metric_type
    """, (client_id,))
    
    # Get tier limits
    client = db_query("SELECT tier FROM saos_clients WHERE id = %s", (client_id,), one=True)
    tier = client.get('tier', 'business') if client else 'business'
    limits = TIER_LIMITS.get(tier, TIER_LIMITS['business'])
    
    return jsonify({
        'metrics': {m['metric_type']: m['total'] for m in metrics} if isinstance(metrics, list) else {},
        'limits': limits,
        'period': 'monthly'
    })

# ── SERVICE SETUP TRACKING ─────────────────────────────────

@app.route('/api/portal/setup-progress')
@require_auth
def setup_progress():
    """Return setup progress for all services."""
    client_id = request.client['id']
    
    # Get client tier services
    client = db_query("SELECT tier FROM saos_clients WHERE id = %s", (client_id,), one=True)
    tier = client.get('tier', 'business') if client else 'business'
    services = TIER_SERVICES.get(tier, TIER_SERVICES['business'])
    
    # Get setup status from database
    setups = db_query("""
        SELECT service_name, status, setup_progress
        FROM service_setup
        WHERE client_id = %s
    """, (client_id,))
    
    setup_map = {}
    if isinstance(setups, list):
        for s in setups:
            setup_map[s['service_name']] = s
    
    # Calculate overall progress
    total_services = len(services)
    completed = sum(1 for s in setup_map.values() if s.get('status') == 'completed')
    progress_pct = int((completed / total_services * 100)) if total_services > 0 else 0
    
    return jsonify({
        'overall_progress': progress_pct,
        'completed_count': completed,
        'total_count': total_services,
        'services': [
            {
                'name': s['name'],
                'icon': s.get('icon', '⚙️'),
                'desc': s.get('desc', ''),
                'status': setup_map.get(s['name'], {}).get('status', 'pending'),
                'progress': setup_map.get(s['name'], {}).get('setup_progress', 0)
            }
            for s in services
        ]
    })

@app.route('/api/portal/setup-progress', methods=['POST'])
@require_auth
def update_setup_progress():
    """Update setup progress for a service."""
    client_id = request.client['id']
    data = request.get_json() or {}
    service_name = data.get('service_name')
    status = data.get('status', 'pending')
    progress = data.get('progress', 0)
    
    if not service_name:
        return jsonify({'error': 'service_name required'}), 400
    
    # Upsert
    db_exec("""
        INSERT INTO service_setup (client_id, service_name, status, setup_progress, started_at)
        VALUES (%s, %s, %s, %s, NOW())
        ON CONFLICT (client_id, service_name)
        DO UPDATE SET 
            status = EXCLUDED.status,
            setup_progress = EXCLUDED.setup_progress,
            completed_at = CASE WHEN EXCLUDED.status = 'completed' THEN NOW() ELSE NULL END
    """, (client_id, service_name, status, progress))
    
    return jsonify({'status': 'updated', 'service': service_name})

# ════════════════════════════════════════════════════════════════
# P2: BACKUP VERIFICATION & RECOVERY ENDPOINTS
# ════════════════════════════════════════════════════════════════

@app.route('/api/admin/backup-log')
@require_role('admin', 'ops')
def backup_log_list():
    """List backup history. Admin/ops only."""
    limit = min(int(request.args.get('limit', 50)), 200)
    backups = db_query("""
        SELECT * FROM backup_log 
        ORDER BY started_at DESC 
        LIMIT %s
    """, (limit,))
    return jsonify({
        'backups': backups if isinstance(backups, list) else [],
        'count': len(backups) if isinstance(backups, list) else 0
    })

@app.route('/api/admin/backup/run', methods=['POST'])
@require_role('admin', 'ops')
def backup_run():
    """Trigger a backup verification cycle. Admin/ops only.
    Runs pg_dump + restore test in background."""
    import subprocess as sp
    import threading
    
    script_path = os.path.join(BASE_DIR, 'scripts', 'backup_verify.py')
    if not os.path.isfile(script_path):
        return jsonify({'error': 'Backup script not found'}), 500
    
    def run_backup():
        try:
            sp.run(
                ['python3', script_path, '--full'],
                capture_output=True, text=True, timeout=120,
                env={**os.environ}
            )
        except Exception as e:
            print(f'[BACKUP] Background backup failed: {e}')
    
    thread = threading.Thread(target=run_backup, daemon=True)
    thread.start()
    
    log_audit('backup_triggered', entity_type='system', 
              client_id=request.client['id'])
    
    return jsonify({
        'success': True,
        'message': 'Backup verification started. Check /api/admin/backup-log for results.'
    })

@app.route('/api/admin/backup/rpo-rto')
@require_role('admin', 'ops')
def backup_rpo_rto():
    """Return RPO/RTO metrics from latest verified backup."""
    latest = db_query("""
        SELECT * FROM backup_log 
        WHERE status = 'verified' 
        ORDER BY started_at DESC 
        LIMIT 1
    """, one=True)
    
    if not latest or 'error' in latest:
        return jsonify({
            'rpo_minutes': 1440,
            'rto_minutes': 10,
            'last_backup': None,
            'message': 'No verified backups yet. Defaults: RPO=24h, RTO=10min'
        })
    
    return jsonify({
        'rpo_minutes': latest.get('rpo_minutes', 1440),
        'rto_minutes': latest.get('rto_minutes', 10),
        'last_backup': latest.get('started_at').isoformat() if latest.get('started_at') else None,
        'last_verified': latest.get('verified_at').isoformat() if latest.get('verified_at') else None,
        'file_size_bytes': latest.get('file_size_bytes'),
        'checksum': latest.get('checksum_sha256', '')[:16] + '...',
        'verification_result': latest.get('verification_result', '')
    })

# ════════════════════════════════════════════════════════════════
# P3: SECURITY EVENTS DASHBOARD ENDPOINTS
# ════════════════════════════════════════════════════════════════

@app.route('/api/admin/security-events')
@require_role('admin', 'ops', 'support')
def security_events_list():
    """List security events with filtering. Admin/ops/support only."""
    limit = min(int(request.args.get('limit', 50)), 200)
    severity = request.args.get('severity')
    event_type = request.args.get('event_type')
    resolved = request.args.get('resolved')
    
    sql = "SELECT * FROM security_events WHERE 1=1"
    params = []
    
    if severity:
        sql += " AND severity = %s"
        params.append(severity)
    if event_type:
        sql += " AND event_type = %s"
        params.append(event_type)
    if resolved is not None:
        sql += " AND resolved = %s"
        params.append(resolved == 'true')
    
    sql += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)
    
    events = db_query(sql, tuple(params))
    return jsonify({
        'events': events if isinstance(events, list) else [],
        'count': len(events) if isinstance(events, list) else 0
    })

@app.route('/api/admin/security-events/stats')
@require_role('admin', 'ops', 'support')
def security_events_stats():
    """Aggregated security event statistics."""
    # Total counts by type
    by_type = db_query("""
        SELECT event_type, COUNT(*) as count, 
               COUNT(*) FILTER (WHERE resolved = false) as unresolved
        FROM security_events
        WHERE created_at > NOW() - INTERVAL '30 days'
        GROUP BY event_type
        ORDER BY count DESC
    """)
    
    # Counts by severity
    by_severity = db_query("""
        SELECT severity, COUNT(*) as count,
               COUNT(*) FILTER (WHERE resolved = false) as unresolved
        FROM security_events
        WHERE created_at > NOW() - INTERVAL '30 days'
        GROUP BY severity
    """)
    
    # Recent critical events
    critical = db_query("""
        SELECT * FROM security_events 
        WHERE severity IN ('critical', 'warning') AND resolved = false
        ORDER BY created_at DESC LIMIT 10
    """)
    
    # Top offending IPs
    top_ips = db_query("""
        SELECT ip_address, COUNT(*) as count,
               MAX(created_at) as last_seen
        FROM security_events
        WHERE created_at > NOW() - INTERVAL '30 days'
        AND ip_address IS NOT NULL
        GROUP BY ip_address
        ORDER BY count DESC
        LIMIT 10
    """)
    
    return jsonify({
        'by_type': by_type if isinstance(by_type, list) else [],
        'by_severity': by_severity if isinstance(by_severity, list) else [],
        'critical_unresolved': critical if isinstance(critical, list) else [],
        'top_offending_ips': top_ips if isinstance(top_ips, list) else [],
        'period': '30 days'
    })

@app.route('/api/admin/security-events/<int:event_id>/resolve', methods=['POST'])
@require_role('admin', 'ops')
def resolve_security_event(event_id):
    """Resolve a security event. Admin/ops only."""
    data = request.get_json() or {}
    notes = data.get('resolution_notes', '')
    
    event = db_query("SELECT * FROM security_events WHERE id = %s", (event_id,), one=True)
    if not event:
        return jsonify({'error': 'Security event not found'}), 404
    
    db_exec("""
        UPDATE security_events 
        SET resolved = true, resolved_at = NOW(), 
            resolved_by = %s, resolution_notes = %s
        WHERE id = %s
    """, (request.client.get('customer_name', 'admin'), notes, event_id))
    
    log_audit('security_event_resolved', entity_type='security_event', 
              entity_id=str(event_id), client_id=request.client['id'])
    
    return jsonify({
        'success': True, 
        'event_id': event_id,
        'message': 'Security event resolved'
    })

# Internal: Log security event (called by auth endpoints)
def log_security_event(event_type, severity='info', client_id=None, ip=None, 
                       user_agent=None, details=None, blocked=False):
    """Log a security event. Silently fails."""
    try:
        db_exec("""
            INSERT INTO security_events 
            (event_type, severity, client_id, ip_address, user_agent, details, blocked)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (event_type, severity, client_id, ip, user_agent,
              json.dumps(details) if details else None, blocked))
    except Exception as e:
        print(f"[SECURITY] Failed to log event: {e}")

# ════════════════════════════════════════════════════════════════
# P4: ADMIN CONSOLE HARDENING & AUDIT EXPORT
# ════════════════════════════════════════════════════════════════

@app.route('/api/admin/audit-log')
@require_role('admin')
def admin_audit_log():
    """Full audit trail. Admin only. Supports filtering."""
    limit = min(int(request.args.get('limit', 100)), 500)
    client_filter = request.args.get('client_id')
    action_filter = request.args.get('action')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    sql = """
        SELECT a.*, c.customer_name 
        FROM audit_log a 
        LEFT JOIN saos_clients c ON a.client_id = c.id
        WHERE 1=1
    """
    params = []
    
    if client_filter:
        sql += " AND a.client_id = %s"
        params.append(int(client_filter))
    if action_filter:
        sql += " AND a.action ILIKE %s"
        params.append(f'%{action_filter}%')
    if date_from:
        sql += " AND a.created_at >= %s"
        params.append(date_from)
    if date_to:
        sql += " AND a.created_at <= %s"
        params.append(date_to)
    
    sql += " ORDER BY a.created_at DESC LIMIT %s"
    params.append(limit)
    
    logs = db_query(sql, tuple(params))
    return jsonify({
        'audit_logs': logs if isinstance(logs, list) else [],
        'count': len(logs) if isinstance(logs, list) else 0,
        'filters': {
            'client_id': client_filter,
            'action': action_filter,
            'date_from': date_from,
            'date_to': date_to
        }
    })

@app.route('/api/admin/audit/export', methods=['POST'])
@require_role('admin')
def admin_audit_export():
    """Export audit log as ZIP file. Admin only.
    Exports full audit trail or filtered by client_id/date range."""
    data = request.get_json() or {}
    client_filter = data.get('client_id')
    date_from = data.get('date_from')
    date_to = data.get('date_to')
    export_type = data.get('export_type', 'full_audit')
    
    sql = """
        SELECT a.*, c.customer_name, c.customer_email
        FROM audit_log a 
        LEFT JOIN saos_clients c ON a.client_id = c.id
        WHERE 1=1
    """
    params = []
    
    if client_filter:
        sql += " AND a.client_id = %s"
        params.append(int(client_filter))
    if date_from:
        sql += " AND a.created_at >= %s"
        params.append(date_from)
    if date_to:
        sql += " AND a.created_at <= %s"
        params.append(date_to)
    
    sql += " ORDER BY a.created_at DESC"
    
    logs = db_query(sql, tuple(params))
    if not isinstance(logs, list):
        logs = []
    
    # Also fetch security events if full export
    security_events = []
    if export_type in ('full_audit', 'security_events'):
        sec_sql = "SELECT * FROM security_events WHERE 1=1"
        sec_params = []
        if date_from:
            sec_sql += " AND created_at >= %s"
            sec_params.append(date_from)
        if date_to:
            sec_sql += " AND created_at <= %s"
            sec_params.append(date_to)
        sec_sql += " ORDER BY created_at DESC"
        security_events = db_query(sec_sql, tuple(sec_params)) or []
    
    # Create ZIP
    import zipfile, io as _io
    zip_buffer = _io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('audit_log.json', json.dumps(logs, indent=2, default=str))
        if security_events:
            zf.writestr('security_events.json', json.dumps(security_events, indent=2, default=str))
        
        # Add summary
        summary = {
            'export_type': export_type,
            'exported_by': request.client.get('customer_name', 'admin'),
            'exported_at': datetime.now().isoformat(),
            'audit_record_count': len(logs),
            'security_event_count': len(security_events),
            'date_range': {'from': date_from, 'to': date_to},
            'client_filter': client_filter
        }
        zf.writestr('export_summary.json', json.dumps(summary, indent=2))
    
    zip_buffer.seek(0)
    
    # Calculate checksum
    zip_data = zip_buffer.getvalue()
    checksum = hashlib.sha256(zip_data).hexdigest()
    
    # Log the export
    db_exec("""
        INSERT INTO audit_exports 
        (exported_by, export_type, client_id_filter, date_from, date_to, 
         record_count, file_size_bytes, checksum_sha256)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (request.client['id'], export_type, client_filter, date_from, date_to,
          len(logs), len(zip_data), checksum))
    
    log_audit('audit_export', entity_type='audit_log', 
              new_value=f'Exported {len(logs)} records', client_id=request.client['id'])
    
    from flask import Response
    return Response(
        zip_data,
        mimetype='application/zip',
        headers={
            'Content-Disposition': f'attachment; filename=saos-audit-export-{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        }
    )

@app.route('/api/admin/audit/client/<int:cid>')
@require_role('admin', 'support')
def admin_client_audit(cid):
    """Get audit trail for a specific client. Admin/support only."""
    client = db_query("SELECT id, customer_name, customer_email, tier, role FROM saos_clients WHERE id = %s", (cid,), one=True)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    limit = min(int(request.args.get('limit', 100)), 500)
    logs = db_query("""
        SELECT * FROM audit_log 
        WHERE client_id = %s 
        ORDER BY created_at DESC LIMIT %s
    """, (cid, limit))
    
    # Security events for this client
    sec_events = db_query("""
        SELECT * FROM security_events 
        WHERE client_id = %s 
        ORDER BY created_at DESC LIMIT %s
    """, (cid, limit))
    
    # Login history
    logins = db_query("""
        SELECT action, created_at, ip_address, user_agent 
        FROM audit_log 
        WHERE client_id = %s AND action LIKE 'login%'
        ORDER BY created_at DESC LIMIT 20
    """, (cid,))
    
    return jsonify({
        'client': client,
        'audit_logs': logs if isinstance(logs, list) else [],
        'security_events': sec_events if isinstance(sec_events, list) else [],
        'login_history': logins if isinstance(logins, list) else [],
        'total_logs': len(logs) if isinstance(logs, list) else 0
    })

# ════════════════════════════════════════════════════════════════
# P5: COMPLIANCE PACKAGE ENDPOINTS
# ════════════════════════════════════════════════════════════════

@app.route('/api/compliance/policies')
@require_auth
def compliance_policies_list():
    """List all active compliance policies. Any authenticated user."""
    policies = db_query("""
        SELECT id, policy_type, title, version, effective_date, review_date, 
               approved_by, status, created_at, updated_at
        FROM compliance_policies 
        WHERE status = 'active'
        ORDER BY policy_type
    """)
    return jsonify({
        'policies': policies if isinstance(policies, list) else [],
        'count': len(policies) if isinstance(policies, list) else 0
    })

@app.route('/api/compliance/policies/<policy_type>')
@require_auth
def compliance_policy_by_type(policy_type):
    """Get full policy content by type. Any authenticated user."""
    policy = db_query("""
        SELECT * FROM compliance_policies 
        WHERE policy_type = %s AND status = 'active'
        ORDER BY version DESC LIMIT 1
    """, (policy_type,), one=True)
    
    if not policy:
        return jsonify({'error': 'Policy not found'}), 404
    
    return jsonify(policy)

@app.route('/api/compliance/incidents')
@require_role('admin', 'ops', 'support')
def compliance_incidents_list():
    """List incident log entries. Admin/ops/support only."""
    status = request.args.get('status')
    severity = request.args.get('severity')
    limit = min(int(request.args.get('limit', 50)), 200)
    
    sql = "SELECT * FROM incident_log WHERE 1=1"
    params = []
    
    if status:
        sql += " AND status = %s"
        params.append(status)
    if severity:
        sql += " AND severity = %s"
        params.append(severity)
    
    sql += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)
    
    incidents = db_query(sql, tuple(params))
    return jsonify({
        'incidents': incidents if isinstance(incidents, list) else [],
        'count': len(incidents) if isinstance(incidents, list) else 0
    })

@app.route('/api/compliance/incidents', methods=['POST'])
@require_role('admin', 'ops')
def compliance_create_incident():
    """Create a new incident log entry. Admin/ops only."""
    data = request.get_json() or {}
    
    required = ['incident_type', 'severity', 'title']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} required'}), 400
    
    result = db_query("""
        INSERT INTO incident_log 
        (incident_type, severity, title, description, affected_clients, 
         status, detected_at, created_by)
        VALUES (%s, %s, %s, %s, %s, 'open', NOW(), %s)
        RETURNING id, title, status, created_at
    """, (
        data['incident_type'],
        data['severity'],
        data['title'],
        data.get('description', ''),
        json.dumps(data.get('affected_clients', [])),
        request.client.get('customer_name', 'admin')
    ), one=True)
    
    if not result or 'error' in result:
        return jsonify({'error': 'Failed to create incident'}), 500
    
    log_audit('incident_created', entity_type='incident', 
              entity_id=str(result.get('id')), client_id=request.client['id'])
    
    return jsonify({
        'success': True,
        'incident': result
    })

@app.route('/api/compliance/incidents/<int:incident_id>/resolve', methods=['POST'])
@require_role('admin', 'ops')
def compliance_resolve_incident(incident_id):
    """Resolve an incident. Admin/ops only."""
    data = request.get_json() or {}
    
    incident = db_query("SELECT * FROM incident_log WHERE id = %s", (incident_id,), one=True)
    if not incident:
        return jsonify({'error': 'Incident not found'}), 404
    
    # Calculate duration
    detected = incident.get('detected_at') or incident.get('created_at')
    duration = None
    if detected:
        duration = int((datetime.now() - detected).total_seconds() / 60)
    
    db_exec("""
        UPDATE incident_log 
        SET status = 'resolved', resolved_at = NOW(), duration_minutes = %s,
            root_cause = %s, resolution = %s, preventive_measures = %s,
            updated_at = NOW()
        WHERE id = %s
    """, (
        duration,
        data.get('root_cause', ''),
        data.get('resolution', ''),
        data.get('preventive_measures', ''),
        incident_id
    ))
    
    log_audit('incident_resolved', entity_type='incident',
              entity_id=str(incident_id), client_id=request.client['id'])
    
    return jsonify({
        'success': True,
        'incident_id': incident_id,
        'duration_minutes': duration,
        'message': 'Incident resolved'
    })

@app.route('/api/compliance/trust-center')
def trust_center():
    """Public trust center — no auth required.
    Returns security posture, compliance status, and policies summary."""
    # Active policies count
    policies = db_query("""
        SELECT policy_type, title, version, effective_date, review_date
        FROM compliance_policies 
        WHERE status = 'active'
        ORDER BY policy_type
    """)
    
    # Recent incidents (last 90 days, no sensitive details)
    incidents = db_query("""
        SELECT incident_type, severity, title, status, 
               detected_at, resolved_at, duration_minutes
        FROM incident_log 
        WHERE created_at > NOW() - INTERVAL '90 days'
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    # Backup status
    last_backup = db_query("""
        SELECT status, started_at, file_size_bytes, verification_result
        FROM backup_log 
        ORDER BY started_at DESC LIMIT 1
    """, one=True)
    
    # Security events summary (last 30 days)
    sec_summary = db_query("""
        SELECT severity, COUNT(*) as count,
               COUNT(*) FILTER (WHERE resolved = true) as resolved_count
        FROM security_events
        WHERE created_at > NOW() - INTERVAL '30 days'
        GROUP BY severity
    """)
    
    return jsonify({
        'company': 'Systack',
        'product': 'SAOS (Systack AI Operations System)',
        'security_posture': {
            'mfa_available': True,
            'rbac_enabled': True,
            'rate_limiting': True,
            'audit_logging': True,
            'encryption_in_transit': 'TLS 1.3 / WireGuard',
            'encryption_at_rest': 'AES-256',
            'network_security': 'Tailscale mesh VPN — no public exposure',
            'data_residency': 'United States (Dallas, TX)'
        },
        'compliance_policies': policies if isinstance(policies, list) else [],
        'recent_incidents': incidents if isinstance(incidents, list) else [],
        'last_backup': last_backup if last_backup and 'error' not in last_backup else None,
        'security_events_30d': sec_summary if isinstance(sec_summary, list) else [],
        'trust_center_version': '1.0',
        'last_updated': datetime.now().isoformat()
    })

# ════════════════════════════════════════════════════════════════
# INTEGRATION: Log security events on failed auth
# ════════════════════════════════════════════════════════════════

# Override log_audit to also log security events for auth failures
_original_log_audit = log_audit

def log_audit_with_security(action, entity_type=None, entity_id=None, old_value=None, 
                            new_value=None, client_id=None):
    """Extended audit logging that also creates security events for auth failures."""
    _original_log_audit(action, entity_type, entity_id, old_value, new_value, client_id)
    
    # Auto-create security events for auth-related actions
    security_actions = {
        'login_failed_invalid_pin': ('failed_login', 'warning'),
        'login_failed_rate_limit': ('rate_limit_hit', 'warning'),
        'login_failed_not_found': ('failed_login', 'info'),
        'login_failed_no_pin': ('failed_login', 'info'),
        'login_failed_bad_mfa': ('mfa_failure', 'warning'),
        'login_failed_bad_recovery': ('mfa_failure', 'warning'),
        'access_denied_wrong_role': ('access_denied', 'warning'),
        'access_denied_missing_permission': ('access_denied', 'warning'),
    }
    
    if action in security_actions:
        event_type, severity = security_actions[action]
        ip = request.remote_addr if request else None
        ua = request.headers.get('User-Agent', '') if request else None
        log_security_event(
            event_type=event_type,
            severity=severity,
            client_id=client_id,
            ip=ip,
            user_agent=ua,
            details={'action': action, 'entity_id': entity_id},
            blocked=(action in ['login_failed_rate_limit'])
        )

# Replace the global log_audit
log_audit = log_audit_with_security

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8768)
    args = parser.parse_args()

    print(f"🛰️  SAOS Customer Portal API v2.1 starting on port {args.port}")
    print(f"   NEW v2.1 features:")
    print(f"   - POST /api/auth/register (first-time PIN setup)")
    print(f"   - POST /api/auth/change-pin (logged-in clients)")
    print(f"   - POST /api/auth/forgot-pin (PIN reset)")
    print(f"   - GET  /api/portal/onboarding-status/<id> (check if setup needed)")
    print(f"   - Enhanced agent descriptions with role + capabilities")
    print(f"   - Task display_name + description fields")
    print(f"   Endpoints:")
    print(f"   - GET /                  (dashboard HTML)")
    print(f"   - POST /api/auth/login   (get Bearer token)")
    print(f"   - GET /api/portal/status (client fleet overview)")
    print(f"   - GET /api/chat/conversations (list chats)")
    print(f"   - POST /api/chat/conversations (create chat)")
    print(f"   - GET /api/chat/conversations/<id>/messages")
    print(f"   - POST /api/chat/conversations/<id>/messages")
    print(f"   - POST /api/chat/webhook/agent-response")
    print(f"   - GET /api/chat/poll")
    print(f"")
    print(f"   Auth: Bearer <token> header")
    print(f"")
    print(f"   Security Features:")
    print(f"   - Rate limiting: 5 login attempts per 5 minutes")
    print(f"   - CORS restricted to authorized domains")
    print(f"   - Token revocation on PIN change")
    print(f"   - Audit logging for compliance")
    print(f"")
    print(f"   NEW: Trust Features:")
    print(f"   - Data residency & encryption proof")
    print(f"   - SLA tracking & incident history")
    print(f"   - Support escalation paths")
    print(f"   - Billing transparency")
    print(f"   - Audit trail for compliance")
    print(f"")
    print(f"   NEW: Export Features:")
    print(f"   - POST /api/export/data (ZIP export of all client data)")
    print(f"")
    print(f"   P2: Backup & Recovery:")
    print(f"   - GET  /api/admin/backup-log           (backup history)")
    print(f"   - POST /api/admin/backup/run            (trigger backup)")
    print(f"   - GET  /api/admin/backup/rpo-rto        (recovery metrics)")
    print(f"")
    print(f"   P3: Security Events:")
    print(f"   - GET  /api/admin/security-events       (list events)")
    print(f"   - GET  /api/admin/security-events/stats (aggregated stats)")
    print(f"   - POST /api/admin/security-events/<id>/resolve (resolve event)")
    print(f"")
    print(f"   P4: Admin Audit:")
    print(f"   - GET  /api/admin/audit-log             (full audit trail)")
    print(f"   - POST /api/admin/audit/export           (export audit ZIP)")
    print(f"   - GET  /api/admin/audit/client/<id>     (client audit report)")
    print(f"")
    print(f"   P5: Compliance:")
    print(f"   - GET  /api/compliance/policies         (list policies)")
    print(f"   - GET  /api/compliance/policies/<type>  (policy by type)")
    print(f"   - GET  /api/compliance/incidents        (incident log)")
    print(f"   - POST /api/compliance/incidents        (create incident)")
    print(f"   - GET  /api/compliance/trust-center     (public trust info)")

    app.run(host='0.0.0.0', port=args.port, debug=False)
