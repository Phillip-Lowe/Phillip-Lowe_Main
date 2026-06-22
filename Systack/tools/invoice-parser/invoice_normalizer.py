#!/usr/bin/env python3
"""
Invoice Normalizer — Bidirectional Invoice System
Converts raw parsed invoices into canonical LRFO (Ledger-Ready Financial Object)
Implements ORACLE design from 2026-06-07
"""

import json
import re
from datetime import datetime
from pathlib import Path


def normalize_invoice(raw_data, business_name="Green Systems LLC"):
    """
    Convert raw parsed invoice into canonical LRFO schema.
    
    Args:
        raw_data: dict from invoice_parser_production.parse_invoice()
        business_name: Your company name for direction resolution
    
    Returns:
        dict: Canonical LRFO with direction, entities, financials, etc.
    """
    
    # Extract raw text for metadata
    raw_text = raw_data.get("raw_text", "")
    
    # Build entity_issuer (who sent the invoice = FROM)
    entity_issuer = {
        "name": raw_data.get("vendor") or extract_vendor_from_text(raw_text),
        "address": extract_address(raw_text, "from|supplier|bill from"),
        "email": extract_email(raw_text),
        "tax_id": extract_tax_id(raw_text)
    }
    
    # Build entity_receiver (who is being billed = TO)
    entity_receiver = {
        "name": extract_billed_to(raw_text) or business_name,
        "address": extract_address(raw_text, "bill to|client|customer"),
        "email": extract_email(raw_text, "bill to|client")
    }
    
    # Resolve direction
    direction = resolve_direction(entity_issuer, entity_receiver, business_name)
    
    # Build line_items from raw items
    line_items = []
    for item in raw_data.get("items", []):
        line_items.append({
            "description": item.get("item", ""),
            "quantity": item.get("quantity", 1),
            "unit_price": item.get("unit_price", item.get("price", 0)),
            "total": item.get("price", 0)
        })
    
    # Build financials
    financials = {
        "subtotal": raw_data.get("subtotal"),
        "tax": raw_data.get("tax"),
        "discount": raw_data.get("discount"),
        "total": raw_data.get("total"),
        "currency": "USD"  # Default, could detect from text
    }
    
    # Build payment info
    payment = {
        "status": "UNPAID",  # Default unless we can detect otherwise
        "method": extract_payment_method(raw_text),
        "terms": extract_payment_terms(raw_text)
    }
    
    # Calculate confidence score
    confidence = calculate_confidence(raw_data, direction, financials)
    
    # Build canonical object
    lrfo = {
        "invoice_id": generate_invoice_id(raw_data),
        "invoice_number": raw_data.get("invoice_number"),
        "invoice_date": normalize_date(raw_data.get("date")),
        "due_date": normalize_date(extract_due_date(raw_text)),
        "direction": direction,
        "entity_issuer": entity_issuer,
        "entity_receiver": entity_receiver,
        "line_items": line_items,
        "financials": financials,
        "payment": payment,
        "metadata": {
            "source_type": "OCR | PDF | EMAIL | API",
            "confidence_score": confidence,
            "raw_text": raw_text[:500]  # Truncated for storage
        }
    }
    
    # Add ledger entry based on direction
    lrfo["ledger_entry"] = generate_ledger_entry(direction, financials, entity_issuer, entity_receiver)
    
    return lrfo


def resolve_direction(entity_issuer, entity_receiver, business_name):
    """
    Determine if invoice is INBOUND (AR) or OUTBOUND (AP).
    
    INBOUND = we issued the invoice (issuer is us) → customer owes us
    OUTBOUND = vendor issued to us (receiver is us) → we owe vendor
    """
    issuer_name = (entity_issuer.get("name") or "").lower()
    receiver_name = (entity_receiver.get("name") or "").lower()
    business_lower = business_name.lower()
    
    # Check if business name appears in issuer (we sent it)
    if business_lower in issuer_name or issuer_name in business_lower:
        return "INBOUND"
    
    # Check if business name appears in receiver (we received it)
    if business_lower in receiver_name or receiver_name in business_lower:
        return "OUTBOUND"
    
    # Fallback: if vendor is known and not us, it's OUTBOUND (they invoiced us)
    if entity_issuer.get("name") and business_lower not in issuer_name:
        return "OUTBOUND"
    
    return "UNKNOWN"


def generate_ledger_entry(direction, financials, entity_issuer, entity_receiver):
    """Generate accounting ledger entry based on direction."""
    total = financials.get("total") or 0
    
    if direction == "INBOUND":
        # Accounts Receivable: we are owed money
        return {
            "type": "AR",
            "description": f"Invoice to {entity_receiver.get('name', 'Customer')}",
            "debit_account": "Accounts Receivable",
            "credit_account": "Revenue",
            "amount": total,
            "status": "PENDING"
        }
    elif direction == "OUTBOUND":
        # Accounts Payable: we owe money
        return {
            "type": "AP",
            "description": f"Invoice from {entity_issuer.get('name', 'Vendor')}",
            "debit_account": "Expense / COGS",
            "credit_account": "Accounts Payable",
            "amount": total,
            "status": "PENDING"
        }
    else:
        return {
            "type": "UNKNOWN",
            "description": "Direction could not be determined",
            "debit_account": "Suspense",
            "credit_account": "Suspense",
            "amount": total,
            "status": "REVIEW_REQUIRED"
        }


def extract_vendor_from_text(text):
    """Extract vendor name from raw text using heuristics."""
    lines = text.split('\n')
    for i, line in enumerate(lines[:15]):
        line = line.strip()
        if not line:
            continue
        # Look for company indicators
        upper = line.upper()
        if any(suffix in upper for suffix in ['INC', 'LLC', 'LTD', 'CO.', 'CORP']):
            if not any(skip in upper for skip in ['STREET', 'AVE', 'ROAD', 'PHONE']):
                return line
    return None


def extract_billed_to(text):
    """Extract 'BILL TO' or 'TO' entity from text."""
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if line.strip().upper().startswith('BILL TO:') or line.strip().upper().startswith('TO:'):
            # Next non-empty line is likely the company
            for j in range(i+1, min(i+5, len(lines))):
                next_line = lines[j].strip()
                if next_line and not any(skip in next_line.lower() for skip in ['attn:', 'phone:', 'email:', '---']):
                    return next_line
    return None


def extract_address(text, context_pattern):
    """Extract address near a context pattern (e.g., 'from', 'bill to')."""
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if re.search(context_pattern, line, re.IGNORECASE):
            # Collect next 3-4 lines that look like address
            address_lines = []
            for j in range(i+1, min(i+6, len(lines))):
                next_line = lines[j].strip()
                if not next_line or next_line.startswith('---') or 'email:' in next_line.lower():
                    break
                if any(indicator in next_line.lower() for indicator in ['st', 'ave', 'rd', 'blvd', 'city', 'zip', 'district']):
                    address_lines.append(next_line)
            if address_lines:
                return ', '.join(address_lines)
    return None


def extract_email(text, context=None):
    """Extract email from text, optionally near a context."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(email_pattern, text)
    return matches[0] if matches else None


def extract_tax_id(text):
    """Extract tax ID (EIN, TIN, VAT) from text."""
    # US EIN: XX-XXXXXXX
    ein_pattern = r'\b\d{2}-\d{7}\b'
    match = re.search(ein_pattern, text)
    if match:
        return match.group(0)
    
    # VAT: various formats like DE123456789, GB123456789
    vat_pattern = r'\b([A-Z]{2}[0-9A-Z]{6,12})\b'
    match = re.search(vat_pattern, text)
    if match:
        # Validate it's not a random word
        val = match.group(1)
        if any(c.isdigit() for c in val) and len(val) >= 8:
            return val
    
    # Tax ID explicit: "Tax ID: 74-1234567" or "TIN: 12-3456789"
    tax_pattern = r'(?:Tax\s*ID|TIN|EIN)[:\s]+([0-9A-Za-z-]{5,})'
    match = re.search(tax_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    return None


def extract_due_date(text):
    """Extract due date from text."""
    patterns = [
        r'Due Date[:\s]+([A-Za-z0-9\s,/-]+)',
        r'Payment Due[:\s]+([A-Za-z0-9\s,/-]+)',
        r'Terms[:\s]+Net\s+(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def extract_payment_method(text):
    """Extract payment method from text."""
    methods = ['Bank Transfer', 'Wire Transfer', 'Check', 'PayPal', 'Credit Card', 'ACH', 'CashApp', 'Venmo']
    for method in methods:
        if method.lower() in text.lower():
            return method
    return None


def extract_payment_terms(text):
    """Extract payment terms from text."""
    patterns = [
        r'Payment Terms[:\s]+([A-Za-z0-9\s%]+)',
        r'Terms[:\s]+([A-Za-z0-9\s%]+)',
        r'Net\s+(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    return None


def normalize_date(date_str):
    """Normalize date string to YYYY-MM-DD format."""
    if not date_str:
        return None
    
    # Try common formats
    formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%B %d, %Y',
        '%b %d, %Y',
        '%m-%d-%Y',
        '%m-%d-%y',
        '%Y/%m/%d',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    return date_str  # Return as-is if can't parse


def generate_invoice_id(raw_data):
    """Generate unique invoice ID from number + date."""
    inv_num = raw_data.get("invoice_number", "")
    date_str = raw_data.get("date", "")
    if inv_num:
        return f"INV-{inv_num}"
    return f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def calculate_confidence(raw_data, direction, financials):
    """Calculate confidence score 0-1 based on data completeness."""
    score = 0.0
    
    # Has vendor
    if raw_data.get("vendor"):
        score += 0.2
    
    # Has date
    if raw_data.get("date"):
        score += 0.15
    
    # Has invoice number
    if raw_data.get("invoice_number"):
        score += 0.15
    
    # Has items
    if raw_data.get("items"):
        score += 0.2
    
    # Has total
    if financials.get("total"):
        score += 0.15
    
    # Direction resolved
    if direction != "UNKNOWN":
        score += 0.15
    else:
        score -= 0.3  # Heavy penalty for unknown direction
    
    return max(0.0, min(1.0, score))


def main():
    """Test normalizer with sample data."""
    # Test with a sample parsed invoice
    sample = {
        "vendor": "NovaTech Solutions Inc.",
        "date": "June 5, 2026",
        "invoice_number": "INV-2026-00458",
        "items": [
            {"item": "Web Application Development", "price": 3400.0},
            {"item": "API Integration", "price": 1425.0}
        ],
        "subtotal": 5195.0,
        "tax": 403.22,
        "total": 5078.72,
        "raw_text": "FROM:\nNovaTech Solutions Inc.\n\nBILL TO:\nGreen Systems LLC\n\nInvoice Number: INV-2026-00458"
    }
    
    result = normalize_invoice(sample, business_name="Green Systems LLC")
    print(json.dumps(result, indent=2))
    print(f"\nDirection: {result['direction']}")
    print(f"Ledger: {result['ledger_entry']['type']} — {result['ledger_entry']['description']}")
    print(f"Confidence: {result['metadata']['confidence_score']}")


if __name__ == '__main__':
    main()
