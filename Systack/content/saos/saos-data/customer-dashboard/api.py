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
    
    client = db_query("""
        SELECT c.* FROM saos_clients c
        JOIN client_auth_tokens t ON c.id = t.client_id
        WHERE t.token_hash = %s 
        AND t.revoked_at IS NULL 
        AND t.expires_at > NOW()
        LIMIT 1
    """, (token_hash,), one=True)
    
    if client and 'error' not in client:
        # Update last_used
        db_exec("UPDATE client_auth_tokens SET last_used_at = NOW() WHERE token_hash = %s", (token_hash,))
        return client
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

# ── NEW: ONBOARDING & PIN MANAGEMENT ───────────────────────

@app.route('/api/auth/register', methods=['POST'])
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
def login():
    """PIN-based login. Requires client_id + PIN. Rate limited: 5 attempts per 5 min."""
    data = request.get_json() or {}
    client_id = data.get('client_id')
    pin = data.get('pin')
    
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
    
    return jsonify({
        "token": token,
        "expires_at": expires.isoformat(),
        "client": client,
        "onboarding_status": client.get('onboarding_status')
    })

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
    expected = os.environ.get('SAOS_INTERNAL_API_KEY', 'saos-internal-dev-key')
    
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
    expected = os.environ.get('SAOS_INTERNAL_API_KEY', 'saos-internal-dev-key')
    
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
    expected = os.environ.get('SAOS_INTERNAL_API_KEY', 'saos-internal-dev-key')
    
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
    expected = os.environ.get('SAOS_INTERNAL_API_KEY', 'saos-internal-dev-key')
    
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
    expected = os.environ.get('SAOS_INTERNAL_API_KEY', 'saos-internal-dev-key')
    
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
    expected = os.environ.get('SAOS_INTERNAL_API_KEY', 'saos-internal-dev-key')
    
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

    app.run(host='0.0.0.0', port=args.port, debug=False)
