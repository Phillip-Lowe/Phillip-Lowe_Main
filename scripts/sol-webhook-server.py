#!/usr/bin/env python3
"""
SOL Webhook Server — Invoice Ingestion Endpoint with Vision Support
Port: 9000

Supports:
- Text-based extraction (pdfplumber/PyPDF2) for simple PDFs
- Vision-based extraction (Kimi 2.6 cloud or local llama) for complex/scanned PDFs
"""

import json
import os
import sys
import traceback
import base64
import tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path

# --- CONFIG ---
PORT = 9000
OLLAMA_URL = "http://localhost:11434/api/generate"
DB_PATH = os.path.expanduser("~/.openclaw/workspaces/sol/systack-invoices.db")
VISION_MODELS = {
    "kimi": "kimi-k2.6:cloud",      # Cloud vision (via Ollama)
    "local": "llama3.2-vision",      # Local vision (if installed)
}
DEFAULT_MODEL = "kimi-k2.6:cloud"   # Default to cloud vision
TEXT_MODEL = "qwen3.5:9b"           # Fallback text-only model

# --- DB SETUP ---

def init_db():
    """Initialize SQLite database for invoice storage."""
    import sqlite3
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT,
            vendor_name TEXT,
            invoice_date TEXT,
            total_amount REAL,
            line_items TEXT,
            source_email TEXT,
            file_path TEXT,
            extraction_method TEXT,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    log(f"Database initialized at {DB_PATH}")

def save_to_db(data):
    """Save extracted invoice data to SQLite."""
    import sqlite3
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO invoices 
            (invoice_number, vendor_name, invoice_date, total_amount, line_items, source_email, file_path, extraction_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('invoice_number'),
            data.get('vendor_name'),
            data.get('invoice_date'),
            data.get('total_amount'),
            json.dumps(data.get('line_items', [])),
            data.get('source_email'),
            data.get('file_path'),
            data.get('extraction_method')
        ))
        invoice_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return invoice_id
    except Exception as e:
        log(f"Database save failed: {e}")
        return None

# --- UTILS ---

def log(msg):
    print(f"[SOL-WEBHOOK] {msg}", flush=True)

def pdf_to_images(pdf_path, dpi=200):
    """Convert PDF pages to base64-encoded PNG images."""
    
    # Try pymupdf first (most reliable, no external deps)
    try:
        import fitz
        log("Using PyMuPDF for PDF-to-image conversion")
        doc = fitz.open(pdf_path)
        encoded = []
        for page_num in range(min(len(doc), 3)):  # Max 3 pages
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
            img_bytes = pix.tobytes("png")
            encoded.append(base64.b64encode(img_bytes).decode())
        doc.close()
        log(f"Converted {len(encoded)} page(s) to images")
        return encoded
    except ImportError:
        log("PyMuPDF not available")
    except Exception as e:
        log(f"PyMuPDF failed: {e}")
    
    # Fallback to pdf2image (requires poppler)
    try:
        import pdf2image
        log("Using pdf2image for PDF-to-image conversion")
        images = pdf2image.convert_from_path(pdf_path, dpi=dpi)
        encoded = []
        for img in images:
            import io
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            encoded.append(base64.b64encode(buffer.getvalue()).decode())
        log(f"Converted {len(encoded)} page(s) to images")
        return encoded
    except ImportError:
        log("pdf2image not installed")
    except Exception as e:
        log(f"pdf2image failed: {e}")
    
    log("No PDF-to-image library available. Install: pip3 install pymupdf")
    return []

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdfplumber."""
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        log(f"pdfplumber failed: {e}")
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or "" + "\n"
            return text.strip()
        except Exception as e2:
            log(f"PyPDF2 fallback failed: {e2}")
            return ""

def extract_with_vision_model(images_b64, model=DEFAULT_MODEL):
    """Extract invoice data using vision model with images."""
    if not images_b64:
        return {"error": "No images could be generated from PDF"}
    
    # Build multimodal prompt
    prompt_text = """You are an expert invoice data extraction system.

Look at these invoice images and extract the following fields. Return ONLY a valid JSON object with no markdown formatting, no code blocks, no extra text.

Fields to extract:
- vendor_name: The company or entity that issued the invoice
- invoice_number: The invoice identifier/number
- invoice_date: The date of the invoice in YYYY-MM-DD format if possible
- total_amount: The total amount due as a number (strip currency symbols)
- line_items: An array of objects, each with description, quantity, unit_price, and subtotal. If line items are unclear, return an empty array [].

Respond with ONLY this JSON structure:
{"vendor_name": "...", "invoice_number": "...", "invoice_date": "...", "total_amount": 0.00, "line_items": [{"description": "...", "quantity": 0, "unit_price": 0.00, "subtotal": 0.00}]}
"""
    
    # For Ollama vision models, we can send images as base64
    payload = {
        "model": model,
        "prompt": prompt_text,
        "images": images_b64[:2],  # Send first 2 pages max
        "stream": False,
        "options": {"temperature": 0.1}
    }
    
    try:
        import urllib.request
        req = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            raw = result.get('response', '').strip()
            
            # Try to parse JSON from response
            if raw.startswith('```'):
                raw = raw.split('```')[1] if '```json' in raw else raw.replace('```', '')
                raw = raw.strip()
            
            data = json.loads(raw)
            return data
    except Exception as e:
        log(f"Vision extraction failed: {e}")
        return {"error": str(e), "raw_response": locals().get('raw', 'N/A')}

def extract_with_text_model(text):
    """Extract invoice data using text-only model."""
    prompt = f"""You are an expert invoice data extraction system.

Extract the following fields from this invoice text and return ONLY a valid JSON object with no markdown formatting, no code blocks, no extra text.

Fields to extract:
- vendor_name: The company or entity that issued the invoice
- invoice_number: The invoice identifier/number
- invoice_date: The date of the invoice in YYYY-MM-DD format if possible
- total_amount: The total amount due as a number (strip currency symbols)
- line_items: An array of objects, each with description, quantity, unit_price, and subtotal. If line items are unclear, return an empty array [].

Invoice text:
---
{text[:8000]}
---

Respond with ONLY this JSON structure:
{{"vendor_name": "...", "invoice_number": "...", "invoice_date": "...", "total_amount": 0.00, "line_items": [{{"description": "...", "quantity": 0, "unit_price": 0.00, "subtotal": 0.00}}]}}
"""

    payload = {
        "model": TEXT_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    }

    try:
        import urllib.request
        req = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            raw = result.get('response', '').strip()
            if raw.startswith('```'):
                raw = raw.split('```')[1] if '```json' in raw else raw.replace('```', '')
                raw = raw.strip()
            data = json.loads(raw)
            return data
    except Exception as e:
        log(f"Text extraction failed: {e}")
        return {"error": str(e), "raw_response": locals().get('raw', 'N/A')}

def extract_invoice(pdf_path, use_vision=True, vision_model=None):
    """Main extraction function — tries vision first, falls back to text."""
    
    # If vision requested and model available, try vision
    if use_vision and vision_model:
        log(f"Attempting vision extraction with model: {vision_model}")
        images = pdf_to_images(pdf_path)
        if images:
            result = extract_with_vision_model(images, vision_model)
            if "error" not in result:
                log(f"Vision extraction succeeded with {len(images)} page(s)")
                return result
            else:
                log(f"Vision extraction failed, falling back to text: {result.get('error')}")
        else:
            log("Could not convert PDF to images, falling back to text extraction")
    
    # Text-based extraction
    log("Using text-based extraction")
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return {"error": "Could not extract any text from PDF"}
    
    return extract_with_text_model(text)

# --- HTTP HANDLER ---

class InvoiceHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        log(f"{self.client_address[0]} - {format % args}")

    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/invoice/extract':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')

            try:
                request = json.loads(body) if body else {}
                file_path = request.get('file_path')
                source_email = request.get('source_email', 'unknown')
                use_vision = request.get('use_vision', True)
                vision_model = request.get('vision_model', DEFAULT_MODEL)

                log(f"Received extraction request: {file_path} | vision={use_vision} | model={vision_model}")

                if not file_path or not os.path.exists(file_path):
                    self._send_json(400, {"status": "error", "message": f"File not found: {file_path}"})
                    return

                # Extract invoice data
                extracted = extract_invoice(file_path, use_vision=use_vision, vision_model=vision_model)

                if "error" in extracted:
                    self._send_json(500, {"status": "error", "message": extracted["error"], "raw": extracted.get("raw_response", "")})
                    return

                log(f"Extraction complete: {json.dumps(extracted, indent=2)[:300]}")

                # Save to local SQLite DB
                db_data = {
                    "invoice_number": extracted.get("invoice_number"),
                    "vendor_name": extracted.get("vendor_name"),
                    "invoice_date": extracted.get("invoice_date"),
                    "total_amount": extracted.get("total_amount"),
                    "line_items": extracted.get("line_items", []),
                    "source_email": source_email,
                    "file_path": file_path,
                    "extraction_method": "vision" if (use_vision and vision_model) else "text"
                }
                invoice_id = save_to_db(db_data)
                if invoice_id:
                    log(f"Saved to database with ID: {invoice_id}")

                response = {
                    "status": "success",
                    "invoice_id": invoice_id,
                    "source_email": source_email,
                    "file_path": file_path,
                    "extraction_method": db_data["extraction_method"],
                    "extracted_data": extracted
                }
                self._send_json(200, response)

            except Exception as e:
                log(f"Error processing request: {e}")
                traceback.print_exc()
                self._send_json(500, {"status": "error", "message": str(e)})

        elif path == '/health':
            self._send_json(200, {
                "status": "ok",
                "service": "sol-invoice-webhook",
                "port": PORT,
                "vision_models": VISION_MODELS,
                "default_model": DEFAULT_MODEL,
                "text_model": TEXT_MODEL
            })

        else:
            self._send_json(404, {"status": "error", "message": "Unknown endpoint"})

    def do_GET(self):
        if self.path == '/health':
            self._send_json(200, {
                "status": "ok",
                "service": "sol-invoice-webhook",
                "port": PORT,
                "vision_models": VISION_MODELS,
                "default_model": DEFAULT_MODEL,
                "text_model": TEXT_MODEL
            })
        else:
            self._send_json(404, {"status": "error", "message": "Unknown endpoint"})

# --- MAIN ---

if __name__ == '__main__':
    init_db()
    server = HTTPServer(('0.0.0.0', PORT), InvoiceHandler)
    log(f"SOL Invoice Webhook Server started on port {PORT}")
    log(f"Endpoints: POST /invoice/extract, GET /health")
    log(f"Database: {DB_PATH}")
    log(f"Vision models: {VISION_MODELS}")
    log(f"Default: {DEFAULT_MODEL}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("Shutting down...")
        server.shutdown()
