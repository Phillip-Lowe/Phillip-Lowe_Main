#!/usr/bin/env python3
"""Create a sample invoice PDF for testing the extraction pipeline."""

from fpdf import FPDF
import os

class InvoicePDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 24)
        self.set_text_color(40, 60, 80)
        self.cell(0, 15, 'ACME SUPPLIES INC.', 0, 1, 'L')
        self.set_font('Arial', '', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, '123 Business Ave, Suite 100', 0, 1, 'L')
        self.cell(0, 6, 'Little Rock, AR 72201', 0, 1, 'L')
        self.cell(0, 6, 'Phone: (501) 555-0199 | acme@example.com', 0, 1, 'L')
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def add_invoice_details(self):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(40, 60, 80)
        self.cell(0, 10, 'INVOICE', 0, 1, 'L')
        
        self.set_font('Arial', '', 11)
        self.set_text_color(50, 50, 50)
        self.cell(50, 8, 'Invoice Number:', 0, 0)
        self.cell(0, 8, 'INV-2024-0042', 0, 1)
        self.cell(50, 8, 'Date:', 0, 0)
        self.cell(0, 8, 'May 15, 2024', 0, 1)
        self.cell(50, 8, 'Due Date:', 0, 0)
        self.cell(0, 8, 'June 15, 2024', 0, 1)
        self.ln(5)

    def add_bill_to(self):
        self.set_font('Arial', 'B', 11)
        self.set_text_color(40, 60, 80)
        self.cell(0, 8, 'BILL TO:', 0, 1)
        self.set_font('Arial', '', 11)
        self.set_text_color(50, 50, 50)
        self.cell(0, 7, 'Systack Automation Agency', 0, 1)
        self.cell(0, 7, '456 Innovation Blvd', 0, 1)
        self.cell(0, 7, 'Benton, AR 72015', 0, 1)
        self.ln(5)

    def add_line_items(self):
        # Table header
        self.set_fill_color(240, 240, 240)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(40, 60, 80)
        self.cell(80, 10, 'Description', 1, 0, 'L', True)
        self.cell(30, 10, 'Quantity', 1, 0, 'C', True)
        self.cell(40, 10, 'Unit Price', 1, 0, 'R', True)
        self.cell(40, 10, 'Subtotal', 1, 1, 'R', True)
        
        # Items
        items = [
            ('Automated Invoice Processing License', '1', '$4,500.00', '$4,500.00'),
            ('Setup & Configuration (Premium)', '1', '$2,000.00', '$2,000.00'),
            ('Monthly Support (6 months prepaid)', '6', '$1,200.00', '$7,200.00'),
        ]
        
        self.set_font('Arial', '', 10)
        self.set_text_color(50, 50, 50)
        for desc, qty, price, subtotal in items:
            self.cell(80, 10, desc, 1, 0, 'L')
            self.cell(30, 10, qty, 1, 0, 'C')
            self.cell(40, 10, price, 1, 0, 'R')
            self.cell(40, 10, subtotal, 1, 1, 'R')
        
        # Totals
        self.ln(5)
        self.set_font('Arial', 'B', 11)
        self.cell(150, 10, 'Subtotal:', 0, 0, 'R')
        self.cell(0, 10, '$13,700.00', 0, 1, 'R')
        self.cell(150, 10, 'Tax (8.5%):', 0, 0, 'R')
        self.set_font('Arial', '', 11)
        self.cell(0, 10, '$1,164.50', 0, 1, 'R')
        self.set_font('Arial', 'B', 12)
        self.set_text_color(200, 50, 50)
        self.cell(150, 12, 'TOTAL DUE:', 0, 0, 'R')
        self.cell(0, 12, '$14,864.50', 0, 1, 'R')

pdf = InvoicePDF()
pdf.add_page()
pdf.add_invoice_details()
pdf.add_bill_to()
pdf.add_line_items()

output_path = os.path.expanduser('~/.openclaw/workspaces/sol/test-data/sample-invoice-acme.pdf')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
pdf.output(output_path)
print(f"Sample invoice created: {output_path}")
