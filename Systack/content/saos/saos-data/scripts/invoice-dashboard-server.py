#!/usr/bin/env python3
"""
Invoice Dashboard Server — View extracted invoices from SQLite
Port: 9001
"""

import json
import os
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = 9001
DB_PATH = os.path.expanduser("~/.openclaw/workspaces/sol/systack-invoices.db")

def log(msg):
    print(f"[INVOICE-DASHBOARD] {msg}", flush=True)

class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        log(f"{self.client_address[0]} - {format % args}")

    def _send_html(self, status_code, html):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _get_invoices(self, limit=50):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, invoice_number, vendor_name, invoice_date, 
                       total_amount, source_email, extraction_method, 
                       extracted_at, processed
                FROM invoices 
                ORDER BY extracted_at DESC 
                LIMIT ?
            ''', (limit,))
            rows = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return rows
        except Exception as e:
            log(f"DB error: {e}")
            return []

    def _get_stats(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM invoices')
            total = cursor.fetchone()[0]
            cursor.execute('SELECT COALESCE(SUM(total_amount), 0) FROM invoices')
            revenue = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM invoices WHERE processed = 0')
            pending = cursor.fetchone()[0]
            conn.close()
            return {"total": total, "revenue": revenue, "pending": pending}
        except Exception as e:
            log(f"Stats error: {e}")
            return {"total": 0, "revenue": 0, "pending": 0}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/':
            # Dashboard HTML
            invoices = self._get_invoices()
            stats = self._get_stats()
            html = self._render_dashboard(invoices, stats)
            self._send_html(200, html)

        elif path == '/api/invoices':
            params = parse_qs(parsed.query)
            limit = int(params.get('limit', [50])[0])
            invoices = self._get_invoices(limit)
            self._send_json(200, {"invoices": invoices})

        elif path == '/api/stats':
            self._send_json(200, self._get_stats())

        elif path == '/health':
            self._send_json(200, {"status": "ok", "service": "invoice-dashboard", "port": PORT})

        else:
            self._send_json(404, {"status": "error", "message": "Not found"})

    def _render_dashboard(self, invoices, stats):
        rows_html = ""
        for inv in invoices:
            rows_html += f"""
                <tr>
                    <td>{inv['id']}</td>
                    <td><strong>{inv['invoice_number'] or 'N/A'}</strong></td>
                    <td>{inv['vendor_name'] or 'N/A'}</td>
                    <td>{inv['invoice_date'] or 'N/A'}</td>
                    <td>${inv['total_amount']:,.2f}</td>
                    <td>{inv['source_email'] or 'N/A'}</td>
                    <td><span class="badge {'processed' if inv['processed'] else 'pending'}">{('Processed' if inv['processed'] else 'Pending')}</span></td>
                    <td>{inv['extracted_at']}</td>
                </tr>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Systack — Invoice Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 30px; border-radius: 16px; margin-bottom: 24px; border: 1px solid #475569; }}
        .header h1 {{ font-size: 28px; font-weight: 800; color: #f8fafc; margin-bottom: 8px; }}
        .header p {{ color: #94a3b8; font-size: 14px; }}
        .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }}
        .stat-card {{ background: #1e293b; padding: 24px; border-radius: 12px; border: 1px solid #334155; text-align: center; }}
        .stat-value {{ font-size: 36px; font-weight: 800; color: #22d3ee; margin-bottom: 4px; }}
        .stat-label {{ color: #94a3b8; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .table-container {{ background: #1e293b; border-radius: 12px; border: 1px solid #334155; overflow: hidden; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
        th {{ background: #0f172a; color: #f8fafc; padding: 16px; text-align: left; font-weight: 600; border-bottom: 2px solid #334155; }}
        td {{ padding: 14px 16px; border-bottom: 1px solid #334155; color: #cbd5e1; }}
        tr:hover td {{ background: #334155; }}
        .badge {{ padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }}
        .badge.pending {{ background: #f59e0b20; color: #f59e0b; }}
        .badge.processed {{ background: #22c55e20; color: #22c55e; }}
        .empty {{ text-align: center; padding: 60px; color: #64748b; }}
        .footer {{ text-align: center; padding: 30px; color: #64748b; font-size: 12px; }}
        @media (max-width: 768px) {{
            .stats {{ grid-template-columns: 1fr; }}
            table {{ font-size: 12px; }}
            td, th {{ padding: 10px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄 Invoice Dashboard</h1>
            <p>Systack Automation — Extracted Invoice Data</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{stats['total']}</div>
                <div class="stat-label">Total Invoices</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats['revenue']:,.2f}</div>
                <div class="stat-label">Total Value</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['pending']}</div>
                <div class="stat-label">Pending Review</div>
            </div>
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Invoice #</th>
                        <th>Vendor</th>
                        <th>Date</th>
                        <th>Amount</th>
                        <th>Source</th>
                        <th>Status</th>
                        <th>Received</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html if invoices else '<tr><td colspan="8" class="empty">No invoices yet. Send a PDF to get started.</td></tr>'}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            Systack Invoice Ingestion System | Powered by SOL + Ollama
        </div>
    </div>
</body>
</html>"""

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), DashboardHandler)
    log(f"Invoice Dashboard Server started on port {PORT}")
    log(f"View at: http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("Shutting down...")
        server.shutdown()
