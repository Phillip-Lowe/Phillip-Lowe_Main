#!/usr/bin/env python3
"""
Invoice Extractor API — Simple HTTP endpoint for PDF upload
Run: python3 invoice_api.py
Endpoint: POST /extract (multipart/form-data, field: invoice)
"""

import json
import sys
import os
import tempfile
import io
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add workspace to path so we can import
sys.path.insert(0, '/Users/philliplowe/.openclaw/workspaces/sol')
from invoice_parser_production import process_pdf
from invoice_db import init_db

# CORS headers for web requests
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
}


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


class InvoiceHandler(BaseHTTPRequestHandler):
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
            self.send_response(200)
            for k, v in CORS_HEADERS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "service": "invoice-extractor"}).encode())
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
            # Process
            raw_result = process_pdf(tmp_path)
            
            # Save to database
            try:
                from invoice_db import save_invoice
                db_id = save_invoice(
                    file_name=file_data.get('filename', 'unknown.pdf'),
                    vendor=raw_result.get('vendor_name'),
                    invoice_date=raw_result.get('invoice_date'),
                    invoice_number=raw_result.get('invoice_number'),
                    subtotal=raw_result.get('total_amount'),  # Use total as subtotal for now
                    tax=None,
                    total=raw_result.get('total_amount'),
                    raw_text=raw_result.get('raw_text', '')[:5000],
                    parsed_json=json.dumps(raw_result),
                    source="api"
                )
                raw_result['sqlite_id'] = db_id
            except Exception as db_err:
                raw_result['db_error'] = str(db_err)
            
            if raw_result.get('error'):
                result = raw_result
            else:
                # Merge normalized + raw for frontend compatibility
                result = dict(raw_result)  # Start with raw (has vendor, items, total, success, etc.)
                try:
                    sys.path.insert(0, '/Users/philliplowe/.openclaw/workspaces/sol')
                    from invoice_normalizer import normalize_invoice
                    normalized = normalize_invoice(raw_result, business_name="Green Systems LLC")
                    # Add normalized fields but don't overwrite raw
                    result['direction'] = normalized.get('direction')
                    result['entity_issuer'] = normalized.get('entity_issuer')
                    result['entity_receiver'] = normalized.get('entity_receiver')
                    result['ledger_entry'] = normalized.get('ledger_entry')
                    result['financials'] = normalized.get('financials')
                    result['confidence'] = normalized.get('metadata', {}).get('confidence_score')
                except Exception as e:
                    result['normalizer_error'] = str(e)
            
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


def run_server(port=8765):
    init_db()
    server = HTTPServer(('0.0.0.0', port), InvoiceHandler)
    print(f"Invoice Extractor API running on http://0.0.0.0:{port}")
    print(f"  POST /extract — upload PDF invoice")
    print(f"  GET  /health  — health check")
    print(f"  CORS enabled for web clients")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=3000)
    args = parser.parse_args()
    run_server(args.port)
