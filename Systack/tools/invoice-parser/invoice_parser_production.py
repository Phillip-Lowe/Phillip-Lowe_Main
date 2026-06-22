#!/usr/bin/env python3
"""
Invoice Parser — Production version
Simple regex-based PDF extraction (no external deps)
"""

import re
import sys
from pathlib import Path


def process_pdf(filepath):
    """Process a PDF file and extract invoice data.
    
    Returns dict with:
    - vendor_name
    - invoice_number
    - invoice_date
    - due_date
    - total_amount
    - items (list of dicts)
    - raw_text
    """
    try:
        # Try to use PyPDF2 if available
        import PyPDF2
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
    except ImportError:
        # Fallback: try using pdftotext
        import subprocess
        try:
            result = subprocess.run(['pdftotext', filepath, '-'], capture_output=True, text=True, timeout=30)
            text = result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired):
            text = ""
    
    if not text:
        return {
            "error": "Could not extract text from PDF. Install PyPDF2 or pdftotext.",
            "raw_text": "",
            "vendor_name": None,
            "invoice_number": None,
            "invoice_date": None,
            "due_date": None,
            "total_amount": None,
            "items": []
        }
    
    # Extract fields using regex
    result = {
        "raw_text": text[:5000],  # Limit raw text
        "vendor_name": _extract_vendor(text),
        "invoice_number": _extract_invoice_number(text),
        "invoice_date": _extract_date(text, ['invoice date', 'date']),
        "due_date": _extract_date(text, ['due date', 'payment due']),
        "total_amount": _extract_total(text),
        "items": _extract_items(text)
    }
    
    return result


def parse_invoice(filepath):
    """Alias for process_pdf."""
    return process_pdf(filepath)


def _extract_vendor(text):
    """Try to find vendor/company name."""
    # Look for common patterns
    lines = text.split('\n')[:20]  # Check first 20 lines
    for line in lines:
        line = line.strip()
        if len(line) > 2 and len(line) < 50:
            # Skip common headers
            if any(skip in line.lower() for skip in ['invoice', 'bill to', 'ship to', 'date', 'page']):
                continue
            return line
    return None


def _extract_invoice_number(text):
    """Extract invoice number."""
    patterns = [
        r'(?:invoice|inv)\s*(?:#|number|no)?[:\s]*([A-Z0-9\-]+)',
        r'(?:invoice|inv)\s*(?:#|number|no)\.?\s*[:\s]*([A-Z0-9\-]+)',
        r'#\s*([0-9]{3,})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _extract_date(text, labels):
    """Extract date from text."""
    # Look for date near labels
    for label in labels:
        pattern = rf'{label}[\s:]*([0-9]{{1,2}}[/\-.][0-9]{{1,2}}[/\-.][0-9]{{2,4}})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # Fallback: find any date
    date_pattern = r'([0-9]{1,2}[/\-.][0-9]{1,2}[/\-.][0-9]{2,4})'
    match = re.search(date_pattern, text)
    if match:
        return match.group(1)
    return None


def _extract_total(text):
    """Extract total amount."""
    patterns = [
        r'(?:total|amount due|balance due)[\s:$]*([0-9,]+\.\d{2})',
        r'\$\s*([0-9,]+\.\d{2})[^\d]*(?:total|due)',
        r'(?:total|due)[:\s$]*([0-9,]+\.\d{2})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1).replace(',', ''))
    
    # Fallback: find largest dollar amount
    amounts = re.findall(r'\$\s*([0-9,]+\.\d{2})', text)
    if amounts:
        return max(float(a.replace(',', '')) for a in amounts)
    return None


def _extract_items(text):
    """Extract line items."""
    items = []
    # Simple line-item pattern
    lines = text.split('\n')
    for line in lines:
        # Look for patterns like "Item name ... $XX.XX"
        match = re.search(r'(.*?)\s+\$?\s*([0-9,]+\.\d{2})', line)
        if match and len(match.group(1).strip()) > 3:
            items.append({
                "description": match.group(1).strip()[:100],
                "price": float(match.group(2).replace(',', ''))
            })
    return items[:20]  # Limit items


if __name__ == '__main__':
    if len(sys.argv) > 1:
        result = process_pdf(sys.argv[1])
        import json
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python3 invoice_parser_production.py <pdf_file>")
