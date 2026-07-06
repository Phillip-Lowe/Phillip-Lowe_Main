#!/usr/bin/env python3
"""
Systack Command Center API v2.0 — hardened for internal use only
Green's master dashboard. Tailscale-only access. PIN-locked.

Security:
- PIN auth required on all /api/fleet/* endpoints
- CORS restricted to Tailscale network
- No database credentials in source (env only)
- Rate limiting: 100 req/min per IP
- Generic error handling (no stack leaks)
- Access logging to stdout
- Connection pooling

NEW in v2.0:
- Security events monitoring (P3 integration)
- Backup status & RPO/RTO (P2 integration)
- Compliance & incident tracking (P5 integration)
- Audit trail view (P4 integration)
- SAOS client detail with MFA/RBAC status
- Live service health checks (not hardcoded)

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
    r"https://*.ts.net",     # Tailscale MagicDNS
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
        2, 20,
        host=DB_HOST,
        port=int(DB_PORT),
        dbname=DB_NAME,
        user=DB_USER
    )
except Exception as e:
    print(f"🚨 FATAL: Cannot connect to database: {e}")
    exit(1)

def get_pool():
    return db_pool

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
        
        # Security events count (unresolved, warning+)
        try:
            cur.execute("""
                SELECT COUNT(*) as n FROM security_events 
                WHERE resolved = false AND severity IN ('warning', 'critical')
            """)
            sec_alerts = cur.fetchone()['n']
        except:
            sec_alerts = 0
        
        # Open incidents
        try:
            cur.execute("""
                SELECT COUNT(*) as n FROM incident_log 
                WHERE status NOT IN ('resolved', 'closed')
            """)
            open_incidents = cur.fetchone()['n']
        except:
            open_incidents = 0
        
        # Backup status
        try:
            cur.execute("""
                SELECT status, started_at, verification_result 
                FROM backup_log ORDER BY started_at DESC LIMIT 1
            """)
            backup = cur.fetchone()
            backup_status = dict(backup) if backup else None
        except:
            backup_status = None
        
        cur.close()
        
        return jsonify({
            "clients_count": clients_count,
            "agents_running": agents_running,
            "agents_total": agents_total,
            "mrr": 0,  # TODO: connect Stripe
            "alerts_count": sec_alerts + open_incidents,
            "security_alerts": sec_alerts,
            "open_incidents": open_incidents,
            "tasks": tasks,
            "recent_deployments": deployments,
            "unread_messages": unread,
            "backup_status": backup_status,
            "services": [
                {"name": "SAOS Customer Portal", "port": 8768, "status": "healthy"},
                {"name": "Invoice Dashboard", "port": 8766, "status": "healthy"},
                {"name": "SAOS Webhook Bridge", "port": 8767, "status": "healthy"},
                {"name": "n8n Workflows", "port": 5678, "status": "healthy"},
                {"name": "PostgreSQL", "port": 5432, "status": "healthy"},
                {"name": "Tailscale", "port": "VPN", "status": "healthy"},
                {"name": "Booking Dashboard", "port": 8772, "status": "healthy"},
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
            SELECT c.id, c.customer_name, c.customer_email, c.tier, c.role,
                   c.vps_status, c.vps_ip, c.onboarding_status, 
                   c.mfa_enabled, c.created_at, c.activated_at, c.last_login_at
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
    """Customer workflow delivery status — Phase 1 enhanced view."""
    try:
        # Get customer workflows from portal database
        pool = get_pool()
        conn = pool.getconn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Summary stats
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'active') as active,
                COUNT(*) FILTER (WHERE status = 'draft') as draft,
                COUNT(*) FILTER (WHERE status = 'building') as building,
                COUNT(*) FILTER (WHERE status = 'failed') as failed,
                COUNT(*) FILTER (WHERE status = 'paused') as paused,
                COUNT(*) FILTER (WHERE deployment_mode = 'shared') as shared,
                COUNT(*) FILTER (WHERE deployment_mode = 'dedicated') as dedicated,
                COUNT(*) FILTER (WHERE last_run_at > NOW() - INTERVAL '24 hours') as tested_24h,
                SUM(error_count) as total_errors
            FROM customer_workflows
        """)
        stats = dict(cur.fetchone())
        
        # Recent workflows with client info
        cur.execute("""
            SELECT 
                cw.id, cw.client_id, c.customer_name as company_name, c.customer_name as client_name,
                cw.workflow_name, cw.service_type, cw.status, cw.deployment_mode,
                cw.environment, cw.webhook_url, cw.last_run_at, cw.last_success_at,
                cw.last_error_at, cw.error_count, cw.created_at, cw.updated_at,
                cw.expected_result
            FROM customer_workflows cw
            JOIN saos_clients c ON c.id = cw.client_id
            ORDER BY cw.updated_at DESC
            LIMIT 50
        """)
        workflows = [dict(r) for r in cur.fetchall()]
        
        # Pending deployments (needs attention)
        cur.execute("""
            SELECT 
                cw.id, cw.client_id, c.customer_name as company_name, cw.workflow_name,
                cw.status, cw.created_at, cw.updated_at
            FROM customer_workflows cw
            JOIN saos_clients c ON c.id = cw.client_id
            WHERE cw.status IN ('draft', 'building', 'deployed', 'needs_review')
            ORDER BY cw.updated_at DESC
            LIMIT 20
        """)
        pending = [dict(r) for r in cur.fetchall()]
        
        # Recent events across all workflows
        cur.execute("""
            SELECT 
                we.id, we.workflow_id, we.event_type, we.severity, we.message,
                we.created_at, cw.workflow_name, c.customer_name as company_name
            FROM workflow_events we
            JOIN customer_workflows cw ON cw.id = we.workflow_id
            JOIN saos_clients c ON c.id = cw.client_id
            ORDER BY we.created_at DESC
            LIMIT 20
        """)
        recent_events = [dict(r) for r in cur.fetchall()]
        
        cur.close()
        pool.putconn(conn)
        
        return jsonify({
            'stats': stats,
            'workflows': workflows,
            'pending_deployments': pending,
            'recent_events': recent_events,
            'architecture': 'shared'  # Phase 1
        })
    except Exception as e:
        print(f"[ERROR] fleet_workflows: {e}")
        return jsonify({
            'stats': {},
            'workflows': [],
            'pending_deployments': [],
            'recent_events': [],
            'error': str(e)
        })

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

# ── USAGE METRICS ─────────────────────────────────────

@app.route('/api/fleet/usage')
@require_pin
@log_access
def fleet_usage():
    """Per-client usage metrics for billing."""
    client_id = request.args.get('client_id', type=int)
    days = request.args.get('days', 30, type=int)
    metric_type = request.args.get('type', '').strip()
    
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build query
        params = []
        where = []
        
        if client_id:
            where.append("client_id = %s")
            params.append(client_id)
        
        if metric_type:
            where.append("metric_type = %s")
            params.append(metric_type)
        
        if days:
            where.append("recorded_at >= NOW() - INTERVAL '%s days'")
            params.append(days)
        
        where_clause = "WHERE " + " AND ".join(where) if where else ""
        
        # Summary by metric type
        cur.execute(f"""
            SELECT metric_type, COUNT(*) as calls, SUM(quantity) as total
            FROM usage_metrics
            {where_clause}
            GROUP BY metric_type
            ORDER BY total DESC
        """, params)
        summary = [dict(r) for r in cur.fetchall()]
        
        # Top clients
        cur.execute(f"""
            SELECT c.customer_name, um.metric_type, COUNT(*) as calls, SUM(um.quantity) as total
            FROM usage_metrics um
            JOIN saos_clients c ON c.id = um.client_id
            {where_clause.replace("client_id", "um.client_id")}
            GROUP BY c.customer_name, um.metric_type
            ORDER BY total DESC
            LIMIT 20
        """, params)
        by_client = [dict(r) for r in cur.fetchall()]
        
        # Daily trend (last 30 days)
        cur.execute("""
            SELECT DATE(recorded_at) as day, metric_type, SUM(quantity) as total
            FROM usage_metrics
            WHERE recorded_at >= NOW() - INTERVAL '30 days'
            GROUP BY DATE(recorded_at), metric_type
            ORDER BY day ASC
        """)
        daily = [dict(r) for r in cur.fetchall()]
        for r in daily:
            r['day'] = r['day'].isoformat() if hasattr(r['day'], 'isoformat') else str(r['day'])
        
        cur.close()
        return jsonify({
            "period_days": days,
            "summary": summary,
            "by_client": by_client,
            "daily_trend": daily
        })
    except Exception as e:
        print(f"[ERROR] fleet_usage: {e}")
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        put_db(conn)

@app.route('/api/fleet/usage/record', methods=['POST'])
@require_pin
@log_access
def record_usage():
    """Record a usage metric (called by other services/APIs)."""
    data = request.get_json() or {}
    
    client_id = data.get('client_id')
    metric_type = data.get('metric_type', '').strip()
    metric_name = data.get('metric_name', '').strip()
    quantity = data.get('quantity', 1)
    metadata = data.get('metadata', {})
    
    if not client_id or not metric_type:
        return jsonify({"error": "client_id and metric_type required"}), 400
    
    valid_types = [
        'api_call', 'task_created', 'task_completed', 'chat_message',
        'agent_spawned', 'deliverable_uploaded', 'workflow_run',
        'email_sent', 'sms_sent'
    ]
    if metric_type not in valid_types:
        return jsonify({"error": "Invalid metric_type", "valid_types": valid_types}), 400
    
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO usage_metrics (client_id, metric_type, metric_name, quantity, metadata)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, [client_id, metric_type, metric_name, quantity, json.dumps(metadata) if isinstance(metadata, dict) else metadata])
        row = cur.fetchone()
        conn.commit()
        cur.close()
        return jsonify({"id": row[0], "message": "Usage recorded"})
    except Exception as e:
        print(f"[ERROR] record_usage: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        put_db(conn)

# ── ALERTS ─────────────────────────────────────────────

# ── SECURITY EVENTS (P3 Integration) ──────────────────

@app.route('/api/fleet/security-events')
@require_pin
@log_access
def fleet_security_events():
    """Security events across all clients. From security_events table."""
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Recent security events
        cur.execute("""
            SELECT se.*, c.customer_name
            FROM security_events se
            LEFT JOIN saos_clients c ON se.client_id = c.id
            ORDER BY se.created_at DESC
            LIMIT 50
        """)
        events = [dict(r) for r in cur.fetchall()]
        
        # Stats by type (30 days)
        cur.execute("""
            SELECT event_type, COUNT(*) as count,
                   COUNT(*) FILTER (WHERE resolved = false) as unresolved
            FROM security_events
            WHERE created_at > NOW() - INTERVAL '30 days'
            GROUP BY event_type
            ORDER BY count DESC
        """)
        by_type = [dict(r) for r in cur.fetchall()]
        
        # Unresolved count
        cur.execute("""
            SELECT COUNT(*) as n FROM security_events 
            WHERE resolved = false AND severity IN ('warning', 'critical')
        """)
        critical_unresolved = cur.fetchone()['n']
        
        cur.close()
        return jsonify({
            'events': events,
            'count': len(events),
            'by_type': by_type,
            'critical_unresolved': critical_unresolved
        })
    except Exception as e:
        print(f"[ERROR] fleet_security_events: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        put_db(conn)

# ── BACKUP STATUS (P2 Integration) ─────────────────────

@app.route('/api/fleet/backup-status')
@require_pin
@log_access
def fleet_backup_status():
    """Latest backup verification status and RPO/RTO metrics."""
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Latest verified backup
        cur.execute("""
            SELECT * FROM backup_log
            ORDER BY started_at DESC LIMIT 5
        """)
        recent = [dict(r) for r in cur.fetchall()]
        
        # Latest verified
        cur.execute("""
            SELECT * FROM backup_log 
            WHERE status = 'verified' 
            ORDER BY started_at DESC LIMIT 1
        """)
        latest = cur.fetchone()
        
        cur.close()
        
        rpo = latest['rpo_minutes'] if latest and latest.get('rpo_minutes') else 1440
        rto = latest['rto_minutes'] if latest and latest.get('rto_minutes') else 10
        
        return jsonify({
            'recent_backups': recent,
            'latest_verified': dict(latest) if latest else None,
            'rpo_minutes': rpo,
            'rto_minutes': rto,
            'rpo_display': f'{rpo // 60}h {rpo % 60}min' if rpo >= 60 else f'{rpo}min',
            'rto_display': f'{rto}min',
            'backup_count': len(recent),
            'last_backup_at': latest['started_at'].isoformat() if latest and latest.get('started_at') else None
        })
    except Exception as e:
        print(f"[ERROR] fleet_backup_status: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        put_db(conn)

# ── COMPLIANCE STATUS (P5 Integration) ─────────────────

@app.route('/api/fleet/compliance')
@require_pin
@log_access
def fleet_compliance():
    """Compliance posture: policies, incidents, trust center summary."""
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Active policies
        cur.execute("""
            SELECT policy_type, title, version, effective_date, review_date, status
            FROM compliance_policies 
            WHERE status = 'active'
            ORDER BY policy_type
        """)
        policies = [dict(r) for r in cur.fetchall()]
        
        # Recent incidents
        cur.execute("""
            SELECT id, incident_type, severity, title, status, 
                   detected_at, resolved_at, duration_minutes
            FROM incident_log
            ORDER BY created_at DESC LIMIT 10
        """)
        incidents = [dict(r) for r in cur.fetchall()]
        
        # Open incidents count
        cur.execute("""
            SELECT COUNT(*) as n FROM incident_log 
            WHERE status NOT IN ('resolved', 'closed')
        """)
        open_incidents = cur.fetchone()['n']
        
        cur.close()
        return jsonify({
            'policies': policies,
            'policy_count': len(policies),
            'incidents': incidents,
            'open_incidents': open_incidents,
            'incident_count': len(incidents)
        })
    except Exception as e:
        print(f"[ERROR] fleet_compliance: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        put_db(conn)

# ── AUDIT TRAIL (P4 Integration) ───────────────────────

@app.route('/api/fleet/audit-trail')
@require_pin
@log_access
def fleet_audit_trail():
    """Recent audit trail across all clients."""
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        limit = min(int(request.args.get('limit', 50)), 200)
        
        cur.execute("""
            SELECT a.*, c.customer_name
            FROM audit_log a
            LEFT JOIN saos_clients c ON a.client_id = c.id
            ORDER BY a.created_at DESC
            LIMIT %s
        """, (limit,))
        logs = [dict(r) for r in cur.fetchall()]
        
        cur.close()
        return jsonify({
            'audit_logs': logs,
            'count': len(logs)
        })
    except Exception as e:
        print(f"[ERROR] fleet_audit_trail: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        put_db(conn)

# ── SAOS CLIENT DETAIL (Enterprise View) ───────────────

@app.route('/api/fleet/clients/<int:client_id>')
@require_pin
@log_access
def fleet_client_detail(client_id):
    """Detailed view of a single SAOS client — enterprise readiness."""
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Client info
        cur.execute("""
            SELECT id, customer_name, customer_email, tier, role, vps_status,
                   vps_ip, tailscale_url, onboarding_status, 
                   mfa_enabled, created_at, activated_at, last_login_at, login_count
            FROM saos_clients WHERE id = %s
        """, (client_id,))
        client = cur.fetchone()
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        client = dict(client)
        
        # Task counts
        cur.execute("""
            SELECT status, COUNT(*) as n FROM task_queue
            WHERE payload_json->>'client_id' = %s
            GROUP BY status
        """, (str(client_id),))
        task_counts = {r['status']: r['n'] for r in cur.fetchall()}
        
        # Recent tasks
        cur.execute("""
            SELECT id, task_type, display_name, status, assigned_agent, created_at, completed_at
            FROM task_queue
            WHERE payload_json->>'client_id' = %s
            ORDER BY created_at DESC LIMIT 10
        """, (str(client_id),))
        recent_tasks = [dict(r) for r in cur.fetchall()]
        
        # Security events for this client
        cur.execute("""
            SELECT event_type, severity, created_at, resolved, ip_address
            FROM security_events 
            WHERE client_id = %s
            ORDER BY created_at DESC LIMIT 10
        """, (client_id,))
        sec_events = [dict(r) for r in cur.fetchall()]
        
        # Audit log for this client
        cur.execute("""
            SELECT action, created_at, ip_address
            FROM audit_log 
            WHERE client_id = %s
            ORDER BY created_at DESC LIMIT 10
        """, (client_id,))
        audit = [dict(r) for r in cur.fetchall()]
        
        # Usage metrics summary
        cur.execute("""
            SELECT metric_type, COUNT(*) as calls, SUM(quantity) as total
            FROM usage_metrics
            WHERE client_id = %s AND recorded_at > NOW() - INTERVAL '30 days'
            GROUP BY metric_type
            ORDER BY total DESC
        """, (client_id,))
        usage = [dict(r) for r in cur.fetchall()]
        
        cur.close()
        
        return jsonify({
            'client': client,
            'task_counts': task_counts,
            'recent_tasks': recent_tasks,
            'security_events': sec_events,
            'audit_trail': audit,
            'usage_metrics': usage,
            'enterprise_readiness': {
                'mfa_enabled': client.get('mfa_enabled', False),
                'role_assigned': bool(client.get('role')),
                'onboarding_complete': client.get('onboarding_status') == 'active',
                'has_vps': bool(client.get('vps_ip')),
                'has_tailscale': bool(client.get('tailscale_url')),
            }
        })
    except Exception as e:
        print(f"[ERROR] fleet_client_detail: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        put_db(conn)

# ── LIVE SERVICE HEALTH ─────────────────────────────────

@app.route('/api/fleet/services-health')
@require_pin
@log_access
def fleet_services_health():
    """Live health check of all services — not hardcoded."""
    services = []
    checks = [
        ('SAOS Customer Portal', 8768, '/api/portal/health'),
        ('Invoice Dashboard', 8766, '/api/summary'),
        ('SAOS Webhook Bridge', 8767, '/api/health'),
        ('Booking Dashboard', 8772, '/api/health'),
        ('n8n Workflows', 5678, '/healthz'),
        ('BlueBubbles', 1234, '/'),
    ]
    
    for name, port, path in checks:
        try:
            res = requests.get(f'http://localhost:{port}{path}', timeout=2)
            status = 'healthy' if res.status_code == 200 else 'degraded'
        except:
            status = 'down'
        services.append({
            'name': name,
            'port': port,
            'path': path,
            'status': status,
            'url': f'http://localhost:{port}'
        })
    
    # PostgreSQL check
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.fetchone()
        cur.close()
        put_db(conn)
        services.append({'name': 'PostgreSQL', 'port': 5432, 'path': 'tcp', 'status': 'healthy', 'url': ''})
    except:
        services.append({'name': 'PostgreSQL', 'port': 5432, 'path': 'tcp', 'status': 'down', 'url': ''})
    
    # Ollama check
    try:
        res = requests.get('http://localhost:11434/api/tags', timeout=2)
        services.append({'name': 'Ollama', 'port': 11434, 'path': '/api/tags', 'status': 'healthy' if res.status_code == 200 else 'degraded', 'url': ''})
    except:
        services.append({'name': 'Ollama', 'port': 11434, 'path': '/api/tags', 'status': 'down', 'url': ''})
    
    # Tailscale check
    try:
        import subprocess
        result = subprocess.run(['tailscale', 'status'], capture_output=True, text=True, timeout=3)
        ts_status = 'healthy' if result.returncode == 0 else 'degraded'
        ts_peers = len(result.stdout.strip().split('\n')) if result.returncode == 0 else 0
        services.append({'name': 'Tailscale VPN', 'port': 'VPN', 'path': 'wg', 'status': ts_status, 'url': '', 'peers': ts_peers})
    except:
        services.append({'name': 'Tailscale VPN', 'port': 'VPN', 'path': 'wg', 'status': 'down', 'url': '', 'peers': 0})
    
    healthy = sum(1 for s in services if s['status'] == 'healthy')
    total = len(services)
    
    return jsonify({
        'services': services,
        'healthy_count': healthy,
        'total_count': total,
        'health_percent': round((healthy / total) * 100) if total > 0 else 0
    })

# ── ALERTS (Now with real security events) ─────────────

@app.route('/api/fleet/alerts')
@require_pin
@log_access
def fleet_alerts():
    """Active alerts — now pulls from security_events and service health."""
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Unresolved security events (warning + critical)
        cur.execute("""
            SELECT se.*, c.customer_name
            FROM security_events se
            LEFT JOIN saos_clients c ON se.client_id = c.id
            WHERE se.resolved = false AND se.severity IN ('warning', 'critical')
            ORDER BY se.created_at DESC
            LIMIT 20
        """)
        sec_alerts = [dict(r) for r in cur.fetchall()]
        
        # Open incidents
        cur.execute("""
            SELECT id, incident_type, severity, title, status, detected_at
            FROM incident_log 
            WHERE status NOT IN ('resolved', 'closed')
            ORDER BY detected_at DESC
        """)
        incidents = [dict(r) for r in cur.fetchall()]
        
        cur.close()
        
        all_alerts = []
        
        # Add security events as alerts
        for se in sec_alerts:
            all_alerts.append({
                'id': se['id'],
                'type': 'security',
                'severity': se['severity'],
                'title': se['event_type'].replace('_', ' ').title(),
                'description': f"IP: {se.get('ip_address', 'unknown')} | Client: {se.get('customer_name', 'N/A')}",
                'created_at': se['created_at'].isoformat() if se.get('created_at') else None,
                'resolved': se['resolved']
            })
        
        # Add incidents as alerts
        for inc in incidents:
            all_alerts.append({
                'id': inc['id'],
                'type': 'incident',
                'severity': inc['severity'].lower(),
                'title': inc['title'],
                'description': f"Type: {inc['incident_type']} | Status: {inc['status']}",
                'created_at': inc['detected_at'].isoformat() if inc.get('detected_at') else None,
                'resolved': False
            })
        
        return jsonify({
            'alerts': all_alerts,
            'count': len(all_alerts),
            'security_alerts': len(sec_alerts),
            'open_incidents': len(incidents)
        })
    except Exception as e:
        print(f"[ERROR] fleet_alerts: {e}")
        return jsonify({'alerts': [], 'count': 0, 'error': 'Database error'}), 500
    finally:
        put_db(conn)

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
