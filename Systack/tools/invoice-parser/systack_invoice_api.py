#!/usr/bin/env python3
"""
Systack Invoice Pipeline API
Connects to SQLite invoice_data.db
Run: python3 systack_invoice_api.py 9001
Endpoint: POST /extract (multipart/form-data, field: invoice)
"""

import json
import sys
import os
import tempfile
import sqlite3
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add workspace to path so we can import
sys.path.insert(0, '/Users/philliplowe/.openclaw/workspaces/sol')
from invoice_parser_production import process_pdf

DB_PATH = Path(__file__).parent / "invoice_data.db"

# CORS headers for web requests
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
}


def get_db_connection():
    """Get SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_invoice_summary(invoice_id, result):
    """Get summary of a specific invoice for email notification."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get invoice items
        cursor.execute("""
            SELECT item_name, price, quantity
            FROM invoice_items 
            WHERE invoice_id = ?
            ORDER BY id
        """, (invoice_id,))
        items = cursor.fetchall()
        
        # Get current month totals
        cursor.execute("""
            SELECT 
                COUNT(*) as total_invoices,
                COALESCE(SUM(total), 0) as total_amount
            FROM invoices 
            WHERE strftime('%Y-%m', processed_at) = strftime('%Y-%m', 'now')
        """)
        month_row = cursor.fetchone()
        
        conn.close()
        
        summary = {
            'invoice_id': invoice_id,
            'vendor': result.get('vendor', 'Unknown Vendor'),
            'invoice_number': result.get('invoice_number', 'N/A'),
            'invoice_date': result.get('date', ''),
            'subtotal': float(result.get('subtotal', 0)),
            'tax': float(result.get('tax', 0)),
            'total': float(result.get('total', 0)),
            'items': [{'name': i[0], 'price': float(i[1]), 'quantity': i[2]} for i in items],
            'month_total_invoices': month_row[0],
            'month_total_amount': float(month_row[1])
        }
        return summary
        
    except Exception as e:
        if conn:
            conn.close()
        return {
            'invoice_id': invoice_id,
            'vendor': result.get('vendor', 'Unknown Vendor'),
            'invoice_number': result.get('invoice_number', 'N/A'),
            'total': float(result.get('total', 0)),
            'items': result.get('items', []),
            'month_total_invoices': 0,
            'month_total_amount': 0.0
        }


def format_invoice_email(summary):
    """Format single invoice summary as HTML email body."""
    vendor = summary['vendor']
    inv_num = summary['invoice_number']
    total = summary['total']
    items = summary['items']
    
    html = f"""<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
<div style="max-width: 600px; margin: 0 auto; padding: 20px;">

<h2 style="color: #1a365d;">📄 Invoice Collected — Systack</h2>

<div style="background: #ebf8ff; padding: 15px; border-radius: 8px; margin: 20px 0;">
    <p><strong>Vendor:</strong> {vendor}</p>
    <p><strong>Invoice #:</strong> {inv_num}</p>
    <p><strong>Date:</strong> {summary.get('invoice_date', 'N/A')}</p>
    <p><strong>Total:</strong> ${total:,.2f}</p>
</div>

<h3 style="color: #1a365d;">Line Items</h3>
<table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
<tr style="background: #ebf8ff;">
    <th style="padding: 10px; text-align: left; border-bottom: 2px solid #1a365d;">Item</th>
    <th style="padding: 10px; text-align: center; border-bottom: 2px solid #1a365d;">Qty</th>
    <th style="padding: 10px; text-align: right; border-bottom: 2px solid #1a365d;">Price</th>
    <th style="padding: 10px; text-align: right; border-bottom: 2px solid #1a365d;">Line Total</th>
</tr>
"""
    
    for item in items:
        name = item.get('name', 'Unknown')
        qty = item.get('quantity', 1)
        price = item.get('price', 0)
        line_total = qty * price
        html += f"""
<tr>
    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{name}</td>
    <td style="padding: 8px; text-align: center; border-bottom: 1px solid #ddd;">{qty}</td>
    <td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">${price:,.2f}</td>
    <td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">${line_total:,.2f}</td>
</tr>
"""
    
    html += f"""
<tr style="font-weight: bold; background: #f5f5f5;">
    <td colspan="3" style="padding: 10px; text-align: right; border-top: 2px solid #1a365d;">Subtotal:</td>
    <td style="padding: 10px; text-align: right; border-top: 2px solid #1a365d;">${summary.get('subtotal', 0):,.2f}</td>
</tr>
<tr style="font-weight: bold;">
    <td colspan="3" style="padding: 10px; text-align: right;">Tax:</td>
    <td style="padding: 10px; text-align: right;">${summary.get('tax', 0):,.2f}</td>
</tr>
<tr style="font-weight: bold; font-size: 1.1em; color: #1a365d;">
    <td colspan="3" style="padding: 10px; text-align: right;">Total:</td>
    <td style="padding: 10px; text-align: right;">${total:,.2f}</td>
</tr>
</table>

<div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0;">
    <p style="margin: 0; color: #666;"><strong>This Month:</strong> {summary['month_total_invoices']} invoices collected, ${summary['month_total_amount']:,.2f} total</p>
</div>

<hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
<p style="color: #666; font-size: 12px;">
    This is an automated notification from the Systack Invoice Pipeline.<br>
    Invoice #{summary['invoice_id']} saved to database.
</p>

</div>
</body>
</html>"""
    
    return html


def save_to_sqlite(result, file_name=None):
    """Save parsed invoice to SQLite database."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Extract data
        vendor = result.get('vendor', '')
        invoice_number = result.get('invoice_number', '')
        invoice_date = result.get('date', '')
        subtotal = result.get('subtotal', 0)
        tax = result.get('tax', 0)
        total = result.get('total', 0)
        items = result.get('items', [])
        raw_text = result.get('raw_text', '')
        
        # Insert invoice
        cursor.execute("""
            INSERT INTO invoices 
            (file_name, vendor, invoice_date, invoice_number, subtotal, tax, total, raw_text, parsed_json, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'email_pipeline')
        """, (
            file_name,
            vendor,
            invoice_date,
            invoice_number,
            subtotal,
            tax,
            total,
            raw_text,
            json.dumps(result)
        ))
        
        invoice_id = cursor.lastrowid
        
        # Insert items
        for item in items:
            cursor.execute("""
                INSERT INTO invoice_items (invoice_id, item_name, price)
                VALUES (?, ?, ?)
            """, (
                invoice_id,
                item.get('name', ''),
                item.get('price', 0)
            ))
        
        conn.commit()
        return invoice_id
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


def parse_multipart(body, content_type):
    """Parse multipart form data manually."""
    # Extract boundary
    boundary = None
    for part in content_type.split(';'):
        part = part.strip()
        if part.startswith('boundary='):
            boundary = part[9:].strip('"\'')
            break
    
    if not boundary:
        return None
    
    # Split on boundary
    boundary_bytes = ('--' + boundary).encode()
    parts = body.split(boundary_bytes)
    
    for part in parts:
        part = part.strip()
        if not part or part == b'--':
            continue
        
        # Find blank line separating headers from body
        blank_line = part.find(b'\r\n\r\n')
        if blank_line == -1:
            blank_line = part.find(b'\n\n')
            if blank_line == -1:
                continue
            header_bytes = part[:blank_line + 2]
            body_bytes = part[blank_line + 2:]
        else:
            header_bytes = part[:blank_line + 4]
            body_bytes = part[blank_line + 4:]
        
        # Parse headers
        headers = {}
        for line in header_bytes.decode('utf-8', errors='replace').split('\r\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                headers[key.lower().strip()] = val.strip()
        
        # Check if this is the invoice field
        disposition = headers.get('content-disposition', '')
        if 'name="invoice"' in disposition or "name='invoice'" in disposition:
            # Extract filename if present
            filename = None
            if 'filename="' in disposition:
                start = disposition.find('filename="') + 10
                end = disposition.find('"', start)
                filename = disposition[start:end]
            elif "filename='" in disposition:
                start = disposition.find("filename='") + 10
                end = disposition.find("'", start)
                filename = disposition[start:end]
            
            # Remove trailing \r\n or --
            if body_bytes.endswith(b'\r\n'):
                body_bytes = body_bytes[:-2]
            elif body_bytes.endswith(b'\n'):
                body_bytes = body_bytes[:-1]
            
            return {'filename': filename, 'data': body_bytes}
    
    return None


class SystackInvoiceHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default logging
        pass
    
    def do_OPTIONS(self):
        self.send_response(200)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/health':
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM invoices")
                count = cursor.fetchone()[0]
                conn.close()
                
                self.send_response(200)
                for k, v in CORS_HEADERS.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "ok",
                    "service": "systack-invoice-pipeline",
                    "database": "sqlite",
                    "invoices_count": count
                }).encode())
            except Exception as e:
                self.send_response(500)
                for k, v in CORS_HEADERS.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "error": str(e)}).encode())
            return
        
        self.send_response(404)
        self.end_headers()
    
    def do_POST(self):
        if self.path != '/extract':
            self.send_response(404)
            self.end_headers()
            return
        
        # Parse multipart form
        content_type = self.headers.get('Content-Type', '')
        if 'multipart/form-data' not in content_type:
            self.send_response(400)
            for k, v in CORS_HEADERS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Expected multipart/form-data"}).encode())
            return
        
        # Read body
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_response(400)
            for k, v in CORS_HEADERS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "No file uploaded"}).encode())
            return
        
        body = self.rfile.read(content_length)
        
        # Parse multipart
        file_data = parse_multipart(body, content_type)
        
        if not file_data:
            self.send_response(400)
            for k, v in CORS_HEADERS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "No 'invoice' file found in request"}).encode())
            return
        
        # Save to temp file
        suffix = Path(file_data['filename'] or 'invoice.pdf').suffix
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(file_data['data'])
            tmp_path = tmp.name
        
        try:
            # Process with parser
            result = process_pdf(tmp_path, save_to_db=False)  # Don't save to SQLite yet
            
            if result.get('error'):
                # Error from parser
                os.unlink(tmp_path)
                self.send_response(400)
                for k, v in CORS_HEADERS.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
            
            # Save to SQLite
            invoice_id = save_to_sqlite(result, file_name=file_data['filename'])
            result['sqlite_id'] = invoice_id
            result['database'] = 'invoice_data.db'
            result['source'] = 'systack_email_pipeline'
            
            # Generate invoice summary for email notification
            summary = get_invoice_summary(invoice_id, result)
            email_html = format_invoice_email(summary)
            
            # Add email_html to result for n8n to use
            result['email_html'] = email_html
            result['email_subject'] = f"Invoice Collected: {result.get('vendor', 'Unknown Vendor')} — {result.get('invoice_number', 'N/A')}"
            
            # Clean up
            os.unlink(tmp_path)
            
            # Respond
            self.send_response(200)
            for k, v in CORS_HEADERS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode())
            
        except Exception as e:
            # Clean up on error
            try:
                os.unlink(tmp_path)
            except:
                pass
            
            self.send_response(500)
            for k, v in CORS_HEADERS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e), "success": False}).encode())


def run_server(port=9001):
    print(f"Systack Invoice Pipeline API running on http://0.0.0.0:{port}")
    print(f"  POST /extract — upload PDF invoice → saves to SQLite")
    print(f"  GET  /health  — check database connection")
    print(f"  CORS enabled for web clients")
    print()
    print(f"Database: {DB_PATH}")
    print(f"Table: invoices")
    
    server = HTTPServer(('0.0.0.0', port), SystackInvoiceHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9001
    run_server(port)
