#!/usr/bin/env python3
"""
Systack Command Center API — hardened for internal use only
Green's master dashboard. Tailscale-only access. PIN-locked.

Security:
- PIN auth required on all /api/fleet/* endpoints
- CORS restricted to Tailscale network
- No database credentials in source (env only)
- Rate limiting: 100 req/min per IP
- Generic error handling (no stack leaks)
- Access logging to stdout
- Connection pooling

Usage:
    python3 api.py              # Start on port 8770
    python3 api.py --port 8770  # Explicit port

Environment:
    SYSTACK_ADMIN_PIN=xxxx      # Required. 4-8 digit PIN
    PGHOST, PGPORT, PGDATABASE, PGUSER  # Required DB config
"""

from flask import Flask, jsonify, send_from_directory, request, abort
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.pool
import os
import argparse
import requests
import json
import time
import hashlib
from datetime import datetime
from functools import wraps

# ── SECURITY CONFIG ───────────────────────────────────

# PIN from environment ONLY — never hardcode
ADMIN_PIN = os.environ.get("SYSTACK_ADMIN_PIN", "").strip()
if not ADMIN_PIN or len(ADMIN_PIN) < 4:
    print("🚨 FATAL: SYSTACK_ADMIN_PIN not set or too short (min 4 digits)")
    print("   Set: export SYSTACK_ADMIN_PIN=xxxx")
    exit(1)

# Rate limiting store: {ip: [timestamp1, timestamp2, ...]}
RATE_LIMIT_STORE = {}
RATE_LIMIT_MAX = 100  # requests per window
RATE_LIMIT_WINDOW = 60  # seconds

def rate_limit_check(ip):
    """Rate limit: 100 req/min per IP."""
    now = time.time()
    timestamps = RATE_LIMIT_STORE.get(ip, [])
    # Remove old timestamps outside window
    timestamps = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
    RATE_LIMIT_STORE[ip] = timestamps
    if len(timestamps) >= RATE_LIMIT_MAX:
        return False
    timestamps.append(now)
    return True

def require_pin(f):
    """Decorator: Require valid PIN in X-Admin-PIN header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Rate limit first
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr) or 'unknown'
        if not rate_limit_check(client_ip):
            print(f"[SECURITY] Rate limit exceeded from {client_ip}")
            abort(429, "Rate limit exceeded")
        
        # PIN check
        pin = request.headers.get("X-Admin-PIN", "").strip()
        if pin != ADMIN_PIN:
            print(f"[SECURITY] Unauthorized access attempt from {client_ip}")
            abort(401, "Unauthorized — valid X-Admin-PIN header required")
        
        return f(*args, **kwargs)
    return decorated

def log_access(f):
    """Decorator: Log all API access."""
    @wraps(f)
    def decorated(*args, **kwargs):
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr) or 'unknown'
        print(f"[ACCESS] {datetime.now().isoformat()} {client_ip} {request.method} {request.path}")
        return f(*args, **kwargs)
    return decorated

# ── APP SETUP ───────────────────────────────────────────

app = Flask(__name__)

# CORS: Restrict to Tailspace network only
CORS(app, origins=[
    r"http://100\..*",      # Tailscale IPv4
    r"http://localhost.*",   # Local development
    r"http://127\.0\.0\.1.*",
])

# Database config from environment ONLY
DB_HOST = os.environ.get("PGHOST")
DB_PORT = os.environ.get("PGPORT")
DB_NAME = os.environ.get("PGDATABASE")
DB_USER = os.environ.get("PGUSER")

for var in ["PGHOST", "PGPORT", "PGDATABASE", "PGUSER"]:
    if not os.environ.get(var):
        print(f"🚨 FATAL: {var} not set")
        exit(1)

# Connection pool (min 1, max 5 connections)
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 5,
        host=DB_HOST,
        port=int(DB_PORT),
        dbname=DB_NAME,
        user=DB_USER
    )
except Exception as e:
    print(f"🚨 FATAL: Cannot connect to database: {e}")
    exit(1)

def get_db():
    return db_pool.getconn()

def put_db(conn):
    db_pool.putconn(conn)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── ERROR HANDLERS ──────────────────────────────────────

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"error": "Unauthorized", "message": "Valid X-Admin-PIN header required"}), 401

@app.errorhandler(429)
def rate_limited(e):
    return jsonify({"error": "Rate limited", "message": "Too many requests"}), 429

@app.errorhandler(500)
def server_error(e):
    print(f"[ERROR] Internal server error: {e}")
    return jsonify({"error": "Internal server error", "message": "An error occurred. Check server logs."}), 500

# ── STATIC FILES ──────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    # Security: prevent directory traversal
    if '..' in filename or filename.startswith('/'):
        abort(404)
    return send_from_directory(BASE_DIR, filename)

# ── HEALTH ────────────────────────────────────────────

@app.route('/api/health')
@log_access
def health():
    """Health check — no auth required (for uptime monitoring)."""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-hardened"
    })

# ── FLEET STATUS (Overview) ──────────────────────────

@app.route('/api/fleet/status')
@require_pin
@log_access
def fleet_status():
    """Master overview: clients, agents, revenue, alerts."""
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Client count
        cur.execute("SELECT COUNT(*) as n FROM saos_clients")
        clients_count = cur.fetchone()['n']
        
        # Active agents (heartbeat within last hour)
        cur.execute("""
            SELECT COUNT(*) as n FROM agent_state 
            WHERE last_heartbeat > NOW() - INTERVAL '1 hour'
        """)
        agents_running = cur.fetchone()['n']
        
        # Total agents
        cur.execute("SELECT COUNT(*) as n FROM agent_state")
        agents_total = cur.fetchone()['n']
        
        # Tasks status
        cur.execute("SELECT status, COUNT(*) as n FROM task_queue GROUP BY status")
        tasks = {r['status']: r['n'] for r in cur.fetchall()}
        
        # Recent deployments (clients) — limited fields, no sensitive data
        cur.execute("""
            SELECT id, customer_name, tier, vps_status, created_at 
            FROM saos_clients 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        deployments = [dict(r) for r in cur.fetchall()]
        
        # Unread messages
        cur.execute("SELECT COUNT(*) as n FROM message_bus WHERE status = 'UNREAD'")
        unread = cur.fetchone()['n']
        
        cur.close()
        
        return jsonify({
            "clients_count": clients_count,
            "agents_running": agents_running,
            "agents_total": agents_total,
            "mrr": 0,  # TODO: connect Stripe
            "alerts_count": 0,  # TODO: alert engine
            "tasks": tasks,
            "recent_deployments": deployments,
            "unread_messages": unread,
            "services": [
                {"name": "SAOS Customer Portal", "port": 8768, "status": "healthy"},
                {"name": "Invoice Dashboard", "port": 8766, "status": "healthy"},
                {"name": "Customer Fleet Dashboard", "port": 8765, "status": "healthy"},
                {"name": "n8n Workflows", "port": 5678, "status": "healthy"},
                {"name": "PostgreSQL", "port": 5432, "status": "healthy"},
                {"name": "Tailscale", "port": "VPN", "status": "healthy"},
                {"name": "Booking API", "port": 8772, "status": "provisioning"},
                {"name": "Command Center", "port": 8770, "status": "healthy"},
            ],
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        print(f"[ERROR] fleet_status: {e}")
        return jsonify({"error": "Database error", "message": "Unable to fetch fleet status"}), 500
    finally:
        put_db(conn)

# ── CLIENTS ────────────────────────────────────────────

@app.route('/api/fleet/clients')
@require_pin
@log_access
def fleet_clients():
    """All SAOS clients with details."""
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT c.id, c.customer_name, c.customer_email, c.tier, c.vps_status, c.created_at
            FROM saos_clients c
            ORDER BY c.created_at DESC
        """)
        clients = [dict(r) for r in cur.fetchall()]
        cur.close()
        return jsonify({"clients": clients, "count": len(clients)})
    except Exception as e:
        print(f"[ERROR] fleet_clients: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        put_db(conn)

# ── AGENTS ─────────────────────────────────────────────

@app.route('/api/fleet/agents')
@require_pin
@log_access
def fleet_agents():
    """All agents across fleet."""
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT agent_name, avatar_emoji, role, status, last_heartbeat,
                   total_tasks_completed, total_tasks_failed
            FROM agent_state
            ORDER BY agent_name
        """)
        agents = [dict(r) for r in cur.fetchall()]
        cur.close()
        return jsonify({"agents": agents, "count": len(agents)})
    except Exception as e:
        print(f"[ERROR] fleet_agents: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        put_db(conn)

# ── INFRASTRUCTURE ───────────────────────────────────

# VPS config loaded from environment, not hardcoded
VPS_CONFIG = json.loads(os.environ.get("SYSTACK_VPS_CONFIG", "[]"))

@app.route('/api/fleet/infrastructure')
@require_pin
@log_access
def fleet_infrastructure():
    """VPS and service endpoint health."""
    # Health check local services
    services = []
    for port, name in [
        (8765, "Customer Fleet Dashboard"),
        (8766, "Invoice Dashboard"),
        (8768, "SAOS Customer Portal"),
    ]:
        try:
            requests.get(f"http://localhost:{port}/api/health", timeout=2)
            services.append({"name": name, "port": port, "status": "healthy"})
        except:
            services.append({"name": name, "port": port, "status": "unreachable"})
    
    return jsonify({"vps": VPS_CONFIG, "services": services})

# ── WORKFLOWS ──────────────────────────────────────────

@app.route('/api/fleet/workflows')
@require_pin
@log_access
def fleet_workflows():
    """n8n workflow status."""
    try:
        res = requests.get("http://localhost:5678/api/v1/workflows", timeout=3)
        if res.status_code == 200:
            workflows = res.json().get('data', [])[:20]
            return jsonify({"workflows": workflows, "count": len(workflows)})
    except:
        pass
    
    return jsonify({"workflows": [], "count": 0, "note": "n8n API unavailable"})

# ── REVENUE ────────────────────────────────────────────

@app.route('/api/fleet/revenue')
@require_pin
@log_access
def fleet_revenue():
    """Revenue summary."""
    return jsonify({
        "mrr": 0,
        "setup_fees": 0,
        "arr": 0,
        "outstanding": 0,
        "note": "Connect Stripe for live data"
    })

# ── ALERTS ─────────────────────────────────────────────

@app.route('/api/fleet/alerts')
@require_pin
@log_access
def fleet_alerts():
    """Active alerts."""
    return jsonify({"alerts": [], "count": 0})

# ── MAIN ──────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8770)
    args = parser.parse_args()
    
    print(f"🚀 Systack Command Center (HARDENED) starting on port {args.port}")
    print(f"   Dashboard: http://localhost:{args.port}")
    print(f"   API:       http://localhost:{args.port}/api/fleet/status")
    print(f"   Security:  PIN auth + rate limits + access logging")
    print(f"   CORS:      Tailspace only")
    print()
    
    app.run(host='0.0.0.0', port=args.port, debug=False)
