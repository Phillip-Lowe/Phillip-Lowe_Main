#!/usr/bin/env python3
"""
SyStack Booking Dashboard API — Internal Appointment Management
Port 8772. Tailscale-only. PIN-locked.

Features:
- Today's appointments with status management
- Calendar view (week/month)
- No-show analytics + trends
- Business hours & services settings

Security:
- PIN auth via X-Admin-PIN header
- CORS restricted to Tailscale network
- Rate limiting: 100 req/min per IP
- Generic error handling
- No DB credentials in source

Usage:
    python3 api.py              # Start on port 8772
    python3 api.py --port 8772

Environment:
    SYSTACK_ADMIN_PIN=xxxx      # Required (4+ digits)
    PGHOST, PGPORT, PGDATABASE, PGUSER  # Required DB config
"""

from flask import Flask, jsonify, send_from_directory, request, abort
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.pool
import os
import argparse
import time
import json
from datetime import datetime, timedelta, date
from functools import wraps

# ── SECURITY CONFIG ───────────────────────────────────

ADMIN_PIN = os.environ.get("SYSTACK_ADMIN_PIN", "").strip()
if not ADMIN_PIN or len(ADMIN_PIN) < 4:
    print("🚨 FATAL: SYSTACK_ADMIN_PIN not set or too short (min 4 digits)")
    exit(1)

RATE_LIMIT_STORE = {}
RATE_LIMIT_MAX = 100
RATE_LIMIT_WINDOW = 60

def rate_limit_check(ip):
    now = time.time()
    timestamps = RATE_LIMIT_STORE.get(ip, [])
    timestamps = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
    RATE_LIMIT_STORE[ip] = timestamps
    if len(timestamps) >= RATE_LIMIT_MAX:
        return False
    timestamps.append(now)
    return True

def require_pin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr) or 'unknown'
        if not rate_limit_check(client_ip):
            print(f"[SECURITY] Rate limit exceeded from {client_ip}")
            abort(429, "Rate limit exceeded")
        
        pin = request.headers.get("X-Admin-PIN", "").strip()
        if pin != ADMIN_PIN:
            print(f"[SECURITY] Unauthorized access attempt from {client_ip}")
            abort(401, "Unauthorized — valid X-Admin-PIN header required")
        
        return f(*args, **kwargs)
    return decorated

def log_access(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr) or 'unknown'
        print(f"[ACCESS] {datetime.now().isoformat()} {client_ip} {request.method} {request.path}")
        return f(*args, **kwargs)
    return decorated

# ── APP SETUP ───────────────────────────────────────────

app = Flask(__name__)

CORS(app, origins=[
    r"http://100\..*",
    r"http://localhost.*",
    r"http://127\.0\.0\.1.*",
])

DB_HOST = os.environ.get("PGHOST")
DB_PORT = os.environ.get("PGPORT")
DB_NAME = os.environ.get("PGDATABASE")
DB_USER = os.environ.get("PGUSER")

for var in ["PGHOST", "PGPORT", "PGDATABASE", "PGUSER"]:
    if not os.environ.get(var):
        print(f"🚨 FATAL: {var} not set")
        exit(1)

try:
    db_pool = psycopg2.pool.SimpleConnectionPool(1, 5,
        host=DB_HOST, port=int(DB_PORT), dbname=DB_NAME, user=DB_USER)
except Exception as e:
    print(f"🚨 FATAL: Cannot connect to database: {e}")
    exit(1)

def get_db():
    return db_pool.getconn()

def put_db(conn):
    db_pool.putconn(conn)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── INIT SETTINGS TABLE ─────────────────────────────────

def init_settings():
    """Ensure booking_settings table exists with default row."""
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS booking_settings (
                id serial PRIMARY KEY,
                business_name text DEFAULT 'SyStack Booking',
                timezone text DEFAULT 'America/Chicago',
                slot_duration_minutes integer DEFAULT 30,
                business_hours jsonb DEFAULT '{"mon":{"open":"09:00","close":"17:00"},"tue":{"open":"09:00","close":"17:00"},"wed":{"open":"09:00","close":"17:00"},"thu":{"open":"09:00","close":"17:00"},"fri":{"open":"09:00","close":"17:00"},"sat":{"open":"10:00","close":"14:00"},"sun":null}'::jsonb,
                services jsonb DEFAULT '[{"name":"Consultation","duration":30,"price":0},{"name":"Strategy Session","duration":60,"price":250}]'::jsonb,
                created_at timestamptz DEFAULT now(),
                updated_at timestamptz DEFAULT now()
            )
        """)
        cur.execute("INSERT INTO booking_settings (id) SELECT 1 WHERE NOT EXISTS (SELECT 1 FROM booking_settings)")
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"[WARN] Settings init: {e}")
    finally:
        put_db(conn)

init_settings()

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
    if '..' in filename or filename.startswith('/'):
        abort(404)
    return send_from_directory(BASE_DIR, filename)

# ── HEALTH ────────────────────────────────────────────

@app.route('/api/health')
@log_access
def health():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-booking"
    })

# ── TODAY'S APPOINTMENTS ──────────────────────────────

@app.route('/api/booking/today')
@require_pin
@log_access
def booking_today():
    """Today's appointments with optional status filter."""
    status_filter = request.args.get('status', '').strip()
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        today = datetime.now().strftime('%Y-%m-%d')
        
        query = """
            SELECT id, customer_name, email, phone, service, appointment_time,
                   status, confirmed, confirmation_token,
                   reminder_24h_sent, reminder_2h_sent,
                   source, created_at
            FROM bookings
            WHERE DATE(appointment_time) = %s
        """
        params = [today]
        
        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)
        
        query += " ORDER BY appointment_time ASC"
        
        cur.execute(query, params)
        rows = [dict(r) for r in cur.fetchall()]
        
        # Convert timestamps to ISO strings for JSON
        for row in rows:
            for key in ['appointment_time', 'created_at']:
                if row.get(key):
                    row[key] = row[key].isoformat() if hasattr(row[key], 'isoformat') else str(row[key])
        
        # Count by status
        cur.execute("""
            SELECT status, COUNT(*) as n FROM bookings
            WHERE DATE(appointment_time) = %s
            GROUP BY status
        """, [today])
        counts = {r['status']: r['n'] for r in cur.fetchall()}
        
        cur.close()
        return jsonify({
            "date": today,
            "appointments": rows,
            "counts": counts,
            "total": len(rows)
        })
    except Exception as e:
        print(f"[ERROR] booking_today: {e}")
        return jsonify({"error": "Database error", "message": "Unable to fetch today's appointments"}), 500
    finally:
        put_db(conn)

# ── UPCOMING APPOINTMENTS ─────────────────────────────

@app.route('/api/booking/upcoming')
@require_pin
@log_access
def booking_upcoming():
    """Next 7 days of appointments."""
    days = request.args.get('days', '7', type=int)
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        now = datetime.now()
        future = now + timedelta(days=days)
        
        cur.execute("""
            SELECT id, customer_name, email, phone, service, appointment_time,
                   status, confirmed, confirmation_token,
                   reminder_24h_sent, reminder_2h_sent,
                   source, created_at
            FROM bookings
            WHERE appointment_time >= %s AND appointment_time < %s
            ORDER BY appointment_time ASC
        """, [now, future])
        
        rows = [dict(r) for r in cur.fetchall()]
        for row in rows:
            for key in ['appointment_time', 'created_at']:
                if row.get(key):
                    row[key] = row[key].isoformat() if hasattr(row[key], 'isoformat') else str(row[key])
        
        cur.close()
        return jsonify({
            "from": now.isoformat(),
            "to": future.isoformat(),
            "appointments": rows,
            "total": len(rows)
        })
    except Exception as e:
        print(f"[ERROR] booking_upcoming: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        put_db(conn)

# ── CALENDAR DATA ─────────────────────────────────────

@app.route('/api/booking/calendar')
@require_pin
@log_access
def booking_calendar():
    """Calendar data for a date range."""
    start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
    end = request.args.get('end', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
    
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, customer_name, service, appointment_time, status, confirmed
            FROM bookings
            WHERE DATE(appointment_time) >= %s AND DATE(appointment_time) <= %s
            ORDER BY appointment_time ASC
        """, [start, end])
        
        rows = [dict(r) for r in cur.fetchall()]
        for row in rows:
            if row.get('appointment_time'):
                row['appointment_time'] = row['appointment_time'].isoformat() if hasattr(row['appointment_time'], 'isoformat') else str(row['appointment_time'])
        
        # Group by date
        by_date = {}
        for row in rows:
            appt_date = row['appointment_time'][:10] if isinstance(row['appointment_time'], str) else row['appointment_time'].strftime('%Y-%m-%d')
            if appt_date not in by_date:
                by_date[appt_date] = []
            by_date[appt_date].append(row)
        
        cur.close()
        return jsonify({
            "start": start,
            "end": end,
            "appointments_by_date": by_date,
            "total": len(rows)
        })
    except Exception as e:
        print(f"[ERROR] booking_calendar: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        put_db(conn)

# ── SINGLE APPOINTMENT ────────────────────────────────

@app.route('/api/booking/appointments/<int:appointment_id>')
@require_pin
@log_access
def booking_detail(appointment_id):
    """Get single appointment details."""
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT * FROM bookings WHERE id = %s
        """, [appointment_id])
        row = cur.fetchone()
        cur.close()
        
        if not row:
            return jsonify({"error": "Not found"}), 404
        
        row = dict(row)
        for key in ['appointment_time', 'created_at', 'updated_at', 'reminder_24h_sent_at', 'reminder_2h_sent_at', 'released_at']:
            if row.get(key):
                row[key] = row[key].isoformat() if hasattr(row[key], 'isoformat') else str(row[key])
        
        return jsonify(row)
    except Exception as e:
        print(f"[ERROR] booking_detail: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        put_db(conn)

# ── UPDATE APPOINTMENT STATUS ─────────────────────────

@app.route('/api/booking/appointments/<int:appointment_id>/status', methods=['POST'])
@require_pin
@log_access
def update_status(appointment_id):
    """Update appointment status."""
    data = request.get_json() or {}
    new_status = data.get('status', '').strip().lower()
    valid_statuses = ['booked', 'confirmed', 'completed', 'cancelled', 'no_show', 'released']
    
    if new_status not in valid_statuses:
        return jsonify({"error": "Invalid status", "valid_statuses": valid_statuses}), 400
    
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            UPDATE bookings
            SET status = %s, updated_at = NOW()
            WHERE id = %s
            RETURNING id, customer_name, status, appointment_time
        """, [new_status, appointment_id])
        row = cur.fetchone()
        conn.commit()
        cur.close()
        
        if not row:
            return jsonify({"error": "Appointment not found"}), 404
        
        return jsonify({
            "id": row['id'],
            "customer_name": row['customer_name'],
            "status": row['status'],
            "message": f"Status updated to {new_status}"
        })
    except Exception as e:
        print(f"[ERROR] update_status: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        put_db(conn)

# ── SERVICES LIST ─────────────────────────────────────

@app.route('/api/booking/services')
@require_pin
@log_access
def booking_services():
    """List unique services from bookings + settings."""
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # From actual bookings
        cur.execute("SELECT DISTINCT service FROM bookings ORDER BY service")
        booked_services = [r['service'] for r in cur.fetchall()]
        
        # From settings
        cur.execute("SELECT services FROM booking_settings WHERE id = 1")
        settings_row = cur.fetchone()
        configured_services = []
        if settings_row and settings_row['services']:
            configured_services = settings_row['services'] if isinstance(settings_row['services'], list) else []
        
        cur.close()
        return jsonify({
            "booked_services": booked_services,
            "configured_services": configured_services
        })
    except Exception as e:
        print(f"[ERROR] booking_services: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        put_db(conn)

# ── ANALYTICS ─────────────────────────────────────────

@app.route('/api/booking/analytics')
@require_pin
@log_access
def booking_analytics():
    """No-show analytics + trends."""
    days = request.args.get('days', '30', type=int)
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        since = datetime.now() - timedelta(days=days)
        
        # Total bookings in period
        cur.execute("SELECT COUNT(*) as n FROM bookings WHERE appointment_time >= %s", [since])
        total = cur.fetchone()['n']
        
        # By status
        cur.execute("""
            SELECT status, COUNT(*) as n FROM bookings
            WHERE appointment_time >= %s
            GROUP BY status
        """, [since])
        by_status = {r['status']: r['n'] for r in cur.fetchall()}
        
        # Confirmation rate
        confirmed_count = by_status.get('confirmed', 0) + by_status.get('completed', 0)
        confirmation_rate = round((confirmed_count / total * 100), 1) if total > 0 else 0
        
        # No-show rate
        no_show_count = by_status.get('no_show', 0)
        no_show_rate = round((no_show_count / total * 100), 1) if total > 0 else 0
        
        # Daily volume (last 30 days)
        cur.execute("""
            SELECT DATE(appointment_time) as day, COUNT(*) as n
            FROM bookings
            WHERE appointment_time >= %s
            GROUP BY DATE(appointment_time)
            ORDER BY day ASC
        """, [since])
        daily_volume = [{"date": str(r['day']), "count": r['n']} for r in cur.fetchall()]
        
        # Top services
        cur.execute("""
            SELECT service, COUNT(*) as n FROM bookings
            WHERE appointment_time >= %s
            GROUP BY service
            ORDER BY n DESC
            LIMIT 10
        """, [since])
        top_services = [{"service": r['service'], "count": r['n']} for r in cur.fetchall()]
        
        # No-show by service
        cur.execute("""
            SELECT service, COUNT(*) as n FROM bookings
            WHERE appointment_time >= %s AND status = 'no_show'
            GROUP BY service
            ORDER BY n DESC
        """, [since])
        no_show_by_service = [{"service": r['service'], "count": r['n']} for r in cur.fetchall()]
        
        cur.close()
        return jsonify({
            "period_days": days,
            "total_bookings": total,
            "by_status": by_status,
            "confirmation_rate": confirmation_rate,
            "no_show_rate": no_show_rate,
            "daily_volume": daily_volume,
            "top_services": top_services,
            "no_show_by_service": no_show_by_service
        })
    except Exception as e:
        print(f"[ERROR] booking_analytics: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        put_db(conn)

# ── SETTINGS ──────────────────────────────────────────

@app.route('/api/booking/settings')
@require_pin
@log_access
def get_settings():
    """Get business settings."""
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM booking_settings WHERE id = 1")
        row = cur.fetchone()
        cur.close()
        
        if not row:
            return jsonify({"error": "Settings not found"}), 404
        
        row = dict(row)
        for key in ['created_at', 'updated_at']:
            if row.get(key):
                row[key] = row[key].isoformat() if hasattr(row[key], 'isoformat') else str(row[key])
        
        return jsonify(row)
    except Exception as e:
        print(f"[ERROR] get_settings: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        put_db(conn)

@app.route('/api/booking/settings', methods=['POST'])
@require_pin
@log_access
def update_settings():
    """Update business settings."""
    data = request.get_json() or {}
    
    allowed_fields = ['business_name', 'timezone', 'slot_duration_minutes', 'business_hours', 'services']
    updates = {k: v for k, v in data.items() if k in allowed_fields}
    
    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400
    
    conn = get_db()
    try:
        cur = conn.cursor()
        
        # Build SET clause
        set_parts = []
        values = []
        for key, val in updates.items():
            set_parts.append(f"{key} = %s")
            values.append(json.dumps(val) if isinstance(val, (dict, list)) else val)
        
        set_parts.append("updated_at = NOW()")
        values.append(1)  # id
        
        query = f"UPDATE booking_settings SET {', '.join(set_parts)} WHERE id = %s"
        cur.execute(query, values)
        conn.commit()
        cur.close()
        
        return jsonify({"message": "Settings updated", "updated": list(updates.keys())})
    except Exception as e:
        print(f"[ERROR] update_settings: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        put_db(conn)

# ── MAIN ──────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8772)
    args = parser.parse_args()
    
    print(f"🚀 SyStack Booking Dashboard starting on port {args.port}")
    print(f"   Dashboard: http://localhost:{args.port}")
    print(f"   Security:  PIN auth + rate limits + access logging")
    print(f"   CORS:      Tailscale only")
    print()
    
    app.run(host='0.0.0.0', port=args.port, debug=False)