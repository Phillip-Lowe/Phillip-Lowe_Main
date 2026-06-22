#!/usr/bin/env python3
"""
Invoice Pipeline Web Dashboard API
Serves JSON data from SQLite invoice database for the web dashboard frontend.

Usage:
    python3 invoice_dashboard_api.py          # Start on port 8766
    python3 invoice_dashboard_api.py --port 9000
"""

import json
import sys
import os
import sqlite3
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

DB_PATH = Path(__file__).parent / "invoice_data.db"

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def query_summary():
    """Dashboard summary metrics."""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as n FROM invoices")
    total_invoices = cur.fetchone()['n']
    
    cur.execute("SELECT COUNT(*) as n FROM invoices_normalized")
    total_normalized = cur.fetchone()['n']
    
    cur.execute("SELECT COUNT(*) as n, SUM(amount_due) as total_due, SUM(amount_paid) as total_paid FROM accounts_receivable")
    ar = cur.fetchone()
    
    cur.execute("SELECT COUNT(*) as n, SUM(amount_due) as total_due, SUM(amount_paid) as total_paid FROM accounts_payable")
    ap = cur.fetchone()
    
    cur.execute("SELECT COUNT(*) as n FROM review_queue WHERE status = 'PENDING'")
    pending_review = cur.fetchone()['n']
    
    cur.execute("SELECT COUNT(*) as n FROM invoices WHERE processed_at >= datetime('now', '-7 days')")
    last_7_days = cur.fetchone()['n']
    
    cur.execute("SELECT COUNT(*) as n FROM invoices WHERE processed_at >= datetime('now', '-1 days')")
    last_24h = cur.fetchone()['n']
    
    # Payment status breakdown
    cur.execute("SELECT payment_status, COUNT(*) as n FROM invoices_normalized GROUP BY payment_status")
    payment_statuses = {r['payment_status'] or 'unknown': r['n'] for r in cur.fetchall()}
    
    # Top vendors
    cur.execute("SELECT vendor, COUNT(*) as n, SUM(total) as total_spend FROM invoices WHERE vendor IS NOT NULL GROUP BY vendor ORDER BY n DESC LIMIT 10")
    top_vendors = [dict(r) for r in cur.fetchall()]
    
    conn.close()
    
    ar_due = ar['total_due'] or 0
    ap_due = ap['total_due'] or 0
    net = ar_due - ap_due
    
    return {
        "total_invoices": total_invoices,
        "total_normalized": total_normalized,
        "last_7_days": last_7_days,
        "last_24h": last_24h,
        "pending_review": pending_review,
        "ar_count": ar['n'] or 0,
        "ar_total": ar_due,
        "ar_paid": ar['total_paid'] or 0,
        "ap_count": ap['n'] or 0,
        "ap_total": ap_due,
        "ap_paid": ap['total_paid'] or 0,
        "net_position": net,
        "payment_statuses": payment_statuses,
        "top_vendors": top_vendors,
    }


def query_invoices(page=1, per_page=25, vendor=None, status=None, search=None, sort_by='processed_at', sort_dir='DESC'):
    """Paginated invoice list with filters."""
    conn = get_db()
    cur = conn.cursor()
    
    where_clauses = []
    params = []
    
    if vendor:
        where_clauses.append("i.vendor LIKE ?")
        params.append(f"%{vendor}%")
    
    if status:
        where_clauses.append("n.payment_status = ?")
        params.append(status)
    
    if search:
        where_clauses.append("(i.vendor LIKE ? OR i.invoice_number LIKE ? OR i.file_name LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    
    where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    # Count total
    count_sql = f"""
        SELECT COUNT(*) as n 
        FROM invoices i 
        LEFT JOIN invoices_normalized n ON i.id = n.raw_invoice_id
        {where}
    """
    cur.execute(count_sql, params)
    total = cur.fetchone()['n']
    
    # Fetch page
    offset = (page - 1) * per_page
    data_sql = f"""
        SELECT i.id, i.vendor, i.invoice_date, i.invoice_number, i.total, i.file_name, i.source, i.processed_at,
               n.direction, n.payment_status, n.confidence_score, n.entity_issuer_name, n.entity_receiver_name
        FROM invoices i
        LEFT JOIN invoices_normalized n ON i.id = n.raw_invoice_id
        {where}
        ORDER BY i.{sort_by} {sort_dir}
        LIMIT ? OFFSET ?
    """
    cur.execute(data_sql, params + [per_page, offset])
    rows = [dict(r) for r in cur.fetchall()]
    
    conn.close()
    
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": max(1, (total + per_page - 1) // per_page),
        "invoices": rows,
    }


def query_invoice_detail(invoice_id):
    """Full detail for a single invoice."""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
    invoice = cur.fetchone()
    if not invoice:
        conn.close()
        return None
    
    invoice = dict(invoice)
    
    cur.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
    items = [dict(r) for r in cur.fetchall()]
    
    cur.execute("SELECT * FROM invoices_normalized WHERE raw_invoice_id = ?", (invoice_id,))
    normalized = cur.fetchone()
    
    cur.execute("SELECT * FROM accounts_receivable WHERE invoice_id = ?", (invoice.get('invoice_number'),))
    ar = cur.fetchone()
    
    cur.execute("SELECT * FROM accounts_payable WHERE invoice_id = ?", (invoice.get('invoice_number'),))
    ap = cur.fetchone()
    
    conn.close()
    
    return {
        "invoice": invoice,
        "items": items,
        "normalized": dict(normalized) if normalized else None,
        "ar": dict(ar) if ar else None,
        "ap": dict(ap) if ap else None,
    }


def query_aging():
    """Aging report for AR."""
    conn = get_db()
    cur = conn.cursor()
    
    buckets = {
        "current": "0-30 days",
        "30_60": "31-60 days",
        "60_90": "61-90 days",
        "90_plus": "90+ days",
    }
    
    results = {}
    for key, label in buckets.items():
        if key == "current":
            cur.execute("""
                SELECT COUNT(*) as n, SUM(amount_due - amount_paid) as total
                FROM accounts_receivable
                WHERE due_date >= date('now') AND due_date <= date('now', '+30 days')
            """)
        elif key == "30_60":
            cur.execute("""
                SELECT COUNT(*) as n, SUM(amount_due - amount_paid) as total
                FROM accounts_receivable
                WHERE due_date >= date('now', '+31 days') AND due_date <= date('now', '+60 days')
            """)
        elif key == "60_90":
            cur.execute("""
                SELECT COUNT(*) as n, SUM(amount_due - amount_paid) as total
                FROM accounts_receivable
                WHERE due_date >= date('now', '+61 days') AND due_date <= date('now', '+90 days')
            """)
        else:
            cur.execute("""
                SELECT COUNT(*) as n, SUM(amount_due - amount_paid) as total
                FROM accounts_receivable
                WHERE due_date > date('now', '+90 days') OR due_date < date('now')
            """)
        
        row = cur.fetchone()
        results[key] = {
            "label": label,
            "count": row['n'] or 0,
            "total": row['total'] or 0,
        }
    
    conn.close()
    return results


def query_vendors():
    """All vendors with stats."""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT vendor, COUNT(*) as invoice_count, SUM(total) as total_spend,
               MIN(invoice_date) as first_seen, MAX(invoice_date) as last_seen
        FROM invoices WHERE vendor IS NOT NULL
        GROUP BY vendor ORDER BY invoice_count DESC
    """)
    vendors = [dict(r) for r in cur.fetchall()]
    conn.close()
    return vendors


class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_OPTIONS(self):
        self.send_response(200)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()
    
    def _json_response(self, data, status=200):
        self.send_response(status)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str, indent=2).encode())
    
    def do_GET(self):
        path = self.path.split('?')[0]
        params = {}
        if '?' in self.path:
            for pair in self.path.split('?')[1].split('&'):
                if '=' in pair:
                    k, v = pair.split('=', 1)
                    params[k] = v
        
        try:
            if path == '/api/summary':
                self._json_response(query_summary())
            
            elif path == '/api/invoices':
                page = int(params.get('page', 1))
                per_page = int(params.get('per_page', 25))
                vendor = params.get('vendor')
                status = params.get('status')
                search = params.get('search')
                sort_by = params.get('sort_by', 'processed_at')
                sort_dir = params.get('sort_dir', 'DESC')
                self._json_response(query_invoices(page, per_page, vendor, status, search, sort_by, sort_dir))
            
            elif path.startswith('/api/invoices/'):
                invoice_id = int(path.split('/')[-1])
                detail = query_invoice_detail(invoice_id)
                if detail:
                    self._json_response(detail)
                else:
                    self._json_response({"error": "Invoice not found"}, 404)
            
            elif path == '/api/aging':
                self._json_response(query_aging())
            
            elif path == '/api/vendors':
                self._json_response(query_vendors())
            
            elif path == '/api/export/csv':
                self._csv_export(params)
            
            elif path == '/health':
                self._json_response({"status": "ok", "service": "invoice-dashboard-api", "db": str(DB_PATH)})
            
            else:
                self._json_response({"error": "Not found", "endpoints": [
                    "/api/summary", "/api/invoices", "/api/invoices/{id}",
                    "/api/aging", "/api/vendors", "/api/export/csv", "/health"
                ]}, 404)
        
        except Exception as e:
            self._json_response({"error": str(e)}, 500)
    
    def _csv_export(self, params):
        """Export invoices as CSV."""
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT i.id, i.vendor, i.invoice_date, i.invoice_number, i.total, i.file_name, i.source, i.processed_at,
                   n.direction, n.payment_status, n.entity_issuer_name, n.entity_receiver_name
            FROM invoices i
            LEFT JOIN invoices_normalized n ON i.id = n.raw_invoice_id
            ORDER BY i.processed_at DESC
        """)
        rows = cur.fetchall()
        conn.close()
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/csv; charset=utf-8')
        self.send_header('Content-Disposition', f'attachment; filename="invoices-export-{datetime.now().strftime("%Y%m%d")}.csv"')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Header
        headers = ['ID', 'Vendor', 'Date', 'Invoice #', 'Total', 'File', 'Source', 'Processed', 'Direction', 'Status', 'Issuer', 'Receiver']
        self.wfile.write(','.join(headers).encode() + b'\n')
        
        for r in rows:
            vals = [
                str(r['id']),
                f'"{r["vendor"] or ""}"',
                f'"{r["invoice_date"] or ""}"',
                f'"{r["invoice_number"] or ""}"',
                str(r['total'] or 0),
                f'"{r["file_name"] or ""}"',
                r['source'] or '',
                str(r['processed_at'] or ''),
                r['direction'] or '',
                r['payment_status'] or '',
                f'"{r["entity_issuer_name"] or ""}"',
                f'"{r["entity_receiver_name"] or ""}"',
            ]
            self.wfile.write(','.join(vals).encode() + b'\n')


def run_server(port=8766):
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f"📊 Invoice Dashboard API running on http://0.0.0.0:{port}")
    print(f"   /api/summary     — dashboard metrics")
    print(f"   /api/invoices    — paginated list with filters")
    print(f"   /api/invoices/ID — full detail")
    print(f"   /api/aging       — AR aging report")
    print(f"   /api/vendors     — vendor directory")
    print(f"   /api/export/csv  — CSV download")
    print(f"   /health          — health check")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    run_server(args.port)
