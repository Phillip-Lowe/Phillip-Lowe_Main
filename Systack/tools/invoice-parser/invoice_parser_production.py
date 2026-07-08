#!/usr/bin/env python3
"""
Invoice Parser — Production version (Fixed 2026-07-08)
Regex-based PDF extraction with improved patterns for:
- Invoice numbers (handles "Invoice Number: INV-2024-0042" and "Invoice #123")
- Dates (handles "May 15, 2024" and "07/08/2026" and "2024-05-15")
- Totals (prioritizes "TOTAL DUE" over "Subtotal")
- Line items (excludes summary rows)
"""

import re
import sys
from pathlib import Path


def process_pdf(filepath):
    """Process a PDF file and extract invoice data."""
    try:
        import PyPDF2
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
    except ImportError:
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
            "subtotal": None,
            "tax": None,
            "items": [],
            "success": False
        }

    result = {
        "raw_text": text[:5000],
        "vendor_name": _extract_vendor(text),
        "invoice_number": _extract_invoice_number(text),
        "invoice_date": _extract_date(text, ['invoice date', 'date issued', 'issued']),
        "due_date": _extract_date(text, ['due date', 'payment due', 'due by']),
        "subtotal": _extract_amount(text, ['subtotal', 'sub total', 'sub-total']),
        "tax": _extract_amount(text, ['tax', 'sales tax', 'vat', 'gst']),
        "total_amount": _extract_total(text),
        "items": _extract_items(text),
        "success": True
    }

    return result


def parse_invoice(filepath):
    """Alias for process_pdf."""
    return process_pdf(filepath)


def _extract_vendor(text):
    """Try to find vendor/company name from first meaningful line."""
    lines = text.split('\n')[:20]
    skip_words = ['invoice', 'bill to', 'ship to', 'date', 'page', 'receipt',
                  'statement', 'credit', 'memo', 'purchase order', 'po #',
                  'remittance', 'from:', 'to:']
    for line in lines:
        line = line.strip()
        if not line or len(line) < 2 or len(line) > 60:
            continue
        if any(skip in line.lower() for skip in skip_words):
            continue
        # Skip lines that are just numbers or addresses
        if re.match(r'^[\d\s\-\(\)\.,#]+$', line):
            continue
        # Skip email/phone lines
        if '@' in line or re.search(r'\(\d{3}\)', line):
            continue
        return line
    return None


def _extract_invoice_number(text):
    """Extract invoice number — handles multiple formats."""
    patterns = [
        # "Invoice Number: INV-2024-0042" or "Invoice No: 12345"
        r'(?:invoice\s*(?:number|no\.?|#)\s*[:\s]*)([A-Z]{0,4}[-]?\d[\dA-Z\-]+)',
        # "INV-2024-0042" standalone (starts with INV or similar)
        r'\b(INV[-\s]?\d[\d\-]+)',
        # "Invoice #123" → capture after #
        r'#\s*([A-Z0-9][A-Z0-9\-]{2,})',
        # "Invoice 12345" (number after invoice, but NOT the word itself)
        r'invoice\s+(?:number\s+)?([A-Z]?\d{3,}[A-Z0-9\-]*)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = match.group(1).strip()
            # Make sure we didn't capture the word "invoice" itself
            if val.lower() not in ['invoice', 'number', 'no', 'date']:
                return val
    return None


def _extract_date(text, labels):
    """Extract date — handles multiple date formats."""
    # Format 1: MM/DD/YYYY or MM-DD-YYYY
    for label in labels:
        pattern = rf'{label}[\s:]*([0-9]{{1,2}}[/\-.][0-9]{{1,2}}[/\-.][0-9]{{2,4}})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    # Format 2: "May 15, 2024" or "May 15 2024" or "15 May 2024"
    months = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
    for label in labels:
        # "Date: May 15, 2024"
        pattern = rf'{label}[\s:]*({months}\s+\d{{1,2}},?\s+\d{{2,4}})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
        # "Date: 15 May 2024"
        pattern = rf'{label}[\s:]*(\d{{1,2}}\s+{months}\s+\d{{2,4}})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    # Format 3: YYYY-MM-DD
    for label in labels:
        pattern = rf'{label}[\s:]*([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    # Fallback: find any date in the text
    patterns = [
        r'([0-9]{1,2}[/\-.][0-9]{1,2}[/\-.][0-9]{2,4})',
        rf'({months}\s+\d{{1,2}},?\s+\d{{2,4}})',
        rf'(\d{{1,2}}\s+{months}\s+\d{{2,4}})',
        r'([0-9]{4}-[0-9]{2}-[0-9]{2})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def _extract_amount(text, labels):
    """Extract a dollar amount near a label."""
    for label in labels:
        patterns = [
            # "Tax (8.5%): $1,164.50" — match amount AFTER label and colon
            rf'{label}[^\n]*?:\s*\$?\s*([0-9,]+\.\d{{2}})',
            # "Tax: $1,164.50" — direct colon
            rf'{label}\s*:\s*\$?\s*([0-9,]+\.\d{{2}})',
            # "Tax $1,164.50" — no colon
            rf'{label}\s+\$?\s*([0-9,]+\.\d{{2}})',
            # "$1,164.50 Tax" — amount before label
            rf'\$\s*([0-9,]+\.\d{{2}})[^\d]*{label}',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    continue
    return None


def _extract_total(text):
    """Extract total amount — prioritize 'TOTAL DUE' / 'AMOUNT DUE' over 'TOTAL'."""
    # Priority labels — try in order
    priority_labels = [
        r'total\s*due',
        r'amount\s*due',
        r'balance\s*due',
        r'grand\s*total',
        r'total\s+amount',
    ]

    for label in priority_labels:
        patterns = [
            rf'{label}[\s:$]*([0-9,]+\.\d{{2}})',
            rf'{label}[\s:]*\$\s*([0-9,]+\.\d{{2}})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    continue

    # Fallback to generic "total" (but not "subtotal")
    patterns = [
        r'(?:^|\n)\s*total[\s:$]*([0-9,]+\.\d{2})',
        r'(?<!sub)\btotal\b[\s:$]*([0-9,]+\.\d{2})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Make sure this isn't actually "subtotal"
            start = max(0, match.start() - 5)
            context = text[start:match.end()].lower()
            if 'subtotal' not in context and 'sub total' not in context:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    continue

    # Last resort: find largest dollar amount (excluding subtotal/tax)
    amounts = re.findall(r'\$\s*([0-9,]+\.\d{2})', text)
    if amounts:
        # Filter out amounts that appear on subtotal/tax lines
        lines = text.split('\n')
        valid_amounts = []
        for line in lines:
            if re.search(r'subtotal|sub\s*total|tax', line, re.IGNORECASE):
                continue
            line_amounts = re.findall(r'\$\s*([0-9,]+\.\d{2})', line)
            for a in line_amounts:
                try:
                    valid_amounts.append(float(a.replace(',', '')))
                except ValueError:
                    continue
        if valid_amounts:
            return max(valid_amounts)
        return max(float(a.replace(',', '')) for a in amounts)
    return None


def _extract_items(text):
    """Extract line items — exclude summary rows."""
    items = []
    skip_keywords = [
        'subtotal', 'sub total', 'sub-total', 'tax', 'sales tax',
        'total due', 'total:', 'amount due', 'balance due', 'grand total',
        'shipping', 'discount', 'deposit', 'payment', 'thank you',
        'remittance', 'terms:', 'net ', 'wire transfer', 'check ',
        'account:', 'routing:', 'po number', 'remit to',
    ]

    lines = text.split('\n')
    in_items_section = False

    for line in lines:
        line = line.strip()
        if not line or len(line) < 3:
            continue

        # Detect start of line items section
        if re.search(r'description\s+qty|description\s+quantity|item\s+price|qty\s+price',
                      line, re.IGNORECASE):
            in_items_section = True
            continue

        # Skip summary rows
        if any(skip in line.lower() for skip in skip_keywords):
            in_items_section = False  # Exit items section when we hit summary
            continue

        # Look for price pattern: $XX.XX at end of line
        match = re.search(r'^(.+?)\s+\$?\s*([0-9,]+\.\d{2})\s*$', line)
        if match:
            desc = match.group(1).strip()
            if len(desc) > 3:
                # Skip if it looks like a header or address
                if re.match(r'^[\d\s\-\(\)\.,#]+$', desc):
                    continue
                if '@' in desc:
                    continue
                try:
                    price = float(match.group(2).replace(',', ''))
                    items.append({
                        "description": desc[:200],
                        "price": price
                    })
                except ValueError:
                    continue

    return items[:50]  # Limit items


if __name__ == '__main__':
    if len(sys.argv) > 1:
        result = process_pdf(sys.argv[1])
        import json
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Usage: python3 invoice_parser_production.py <pdf_file>")