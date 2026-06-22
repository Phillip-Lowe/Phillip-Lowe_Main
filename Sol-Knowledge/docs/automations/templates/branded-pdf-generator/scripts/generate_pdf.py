#!/usr/bin/env python3
"""
SyStack Branded PDF Generator v2
=================================
Reliable Markdown → Branded PDF pipeline using:
  1. pandoc: Markdown → standalone HTML
  2. pyppeteer (headless Chromium): HTML → PDF with full CSS rendering

Why this stack (lessons learned 2026-06-16):
  - fpdf2: no CSS layout, manual positioning, poor typography → rejected
  - WeasyPrint: system library hell on macOS (gobject/pango/cffi) → rejected
  - wkhtmltopdf: removed from Homebrew, unmaintained → rejected
  - MacTeX: 4GB install, overkill → rejected
  - pandoc + pyppeteer: pandoc handles MD→HTML, Chromium handles CSS→PDF perfectly → WINNER

Usage:
    python3 generate_pdf.py input.md output.pdf [--title "Document Title"] [--brand utopia-deli|systack]
    python3 generate_pdf.py --all  # batch convert all in docs/automations/order-system/
"""

import sys
import os
import re
import argparse
import asyncio
import subprocess
import tempfile
from pathlib import Path
from pyppeteer import launch

# SyStack Brand Colors (CSS)
SYSTACK_CSS = """
:root {
  --navy: #001a2d;
  --navy-light: #002845;
  --teal: #007da9;
  --cyan: #00a1db;
  --cyan-bright: #00c5e0;
  --white: #ffffff;
  --gray-50: #f8fafc;
  --gray-100: #f1f5f9;
  --gray-200: #e2e8f0;
  --gray-400: #94a3b8;
  --gray-600: #475569;
  --gray-800: #1e293b;
  --green: #22c55e;
  --red: #ef4444;
  --purple: #8b5cf6;
}

@page {
  size: A4;
  margin: 2cm 2.2cm 2.5cm 2.2cm;
  @top-center {
    content: element(pageHeader);
  }
  @bottom-center {
    content: element(pageFooter);
  }
}

@page :first {
  @top-center { content: none; }
  margin-top: 0;
}

body {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.6;
  color: var(--gray-600);
}

/* Running page header */
.page-header {
  position: running(pageHeader);
  font-size: 7.5pt;
  color: var(--gray-400);
  text-align: right;
  padding-bottom: 3px;
  border-bottom: 1px solid var(--gray-200);
  width: 100%;
}

.page-footer {
  position: running(pageFooter);
  font-size: 7pt;
  color: var(--gray-400);
  text-align: center;
  padding-top: 3px;
  border-top: 1px solid var(--gray-200);
  width: 100%;
}

/* Cover bar */
.cover-bar {
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-light) 50%, var(--teal) 100%);
  color: var(--white);
  padding: 36px 32px 28px 32px;
  margin: 0 0 28px 0;
  width: 100%;
}

.cover-bar .doc-label {
  font-size: 9pt;
  text-transform: uppercase;
  letter-spacing: 2.5px;
  color: var(--cyan-bright);
  margin-bottom: 8px;
  font-weight: 600;
}

.cover-bar h1 {
  font-size: 22pt;
  font-weight: 700;
  color: var(--white);
  margin: 0 0 6px 0;
  line-height: 1.2;
}

.cover-bar .subtitle {
  font-size: 10pt;
  color: var(--gray-400);
  margin-top: 4px;
}

/* Metadata table */
.meta-table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0 24px 0;
  font-size: 9pt;
}

.meta-table td {
  padding: 4px 12px 4px 0;
  vertical-align: top;
}

.meta-table td:first-child {
  font-weight: 600;
  color: var(--gray-800);
  white-space: nowrap;
  width: 110px;
}

.meta-table td:last-child {
  color: var(--gray-600);
}

/* Brand reference table */
.brand-table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0 20px 0;
  font-size: 8.5pt;
}

.brand-table th {
  background: var(--navy);
  color: var(--white);
  padding: 6px 10px;
  text-align: left;
  font-weight: 600;
  font-size: 7.5pt;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.brand-table td {
  padding: 5px 10px;
  border-bottom: 1px solid var(--gray-200);
}

.brand-table tr:nth-child(even) td {
  background: var(--gray-50);
}

.brand-table .swatch {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 3px;
  border: 1px solid var(--gray-200);
  vertical-align: middle;
  margin-right: 6px;
}

/* Headings */
h1 {
  font-size: 18pt;
  font-weight: 700;
  color: var(--navy);
  margin: 28px 0 12px 0;
  padding-bottom: 6px;
  border-bottom: 2px solid var(--teal);
  page-break-before: always;
  string-set: heading content();
}

h1:first-of-type {
  page-break-before: avoid;
}

h2 {
  font-size: 13pt;
  font-weight: 700;
  color: var(--gray-800);
  margin: 22px 0 8px 0;
  padding-left: 10px;
  border-left: 3px solid var(--cyan);
}

h3 {
  font-size: 11pt;
  font-weight: 600;
  color: var(--gray-800);
  margin: 16px 0 6px 0;
}

h4 {
  font-size: 10.5pt;
  font-weight: 600;
  color: var(--gray-600);
  margin: 12px 0 4px 0;
}

/* Paragraphs and lists */
p { margin: 6px 0 10px 0; }
ul, ol { margin: 6px 0 10px 0; padding-left: 22px; }
li { margin: 2px 0; }

/* Code */
code {
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: 8.5pt;
  background: var(--gray-100);
  padding: 1px 5px;
  border-radius: 3px;
  color: var(--navy);
}

pre {
  background: var(--navy);
  color: var(--cyan-bright);
  padding: 14px 16px;
  border-radius: 6px;
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: 8pt;
  line-height: 1.5;
  overflow-x: auto;
  margin: 10px 0 14px 0;
}

pre code {
  background: none;
  color: inherit;
  padding: 0;
  font-size: inherit;
}

/* Tables */
table:not(.meta-table):not(.brand-table) {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0 16px 0;
  font-size: 9pt;
}

table:not(.meta-table):not(.brand-table) th {
  background: var(--navy);
  color: var(--white);
  padding: 7px 10px;
  text-align: left;
  font-weight: 600;
  font-size: 8pt;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

table:not(.meta-table):not(.brand-table) td {
  padding: 6px 10px;
  border-bottom: 1px solid var(--gray-200);
}

table:not(.meta-table):not(.brand-table) tr:nth-child(even) td {
  background: var(--gray-50);
}

/* Horizontal rules */
hr {
  border: none;
  border-top: 1px solid var(--gray-200);
  margin: 20px 0;
}

/* Strong */
strong { color: var(--gray-800); }

/* Links */
a { color: var(--cyan); text-decoration: none; }

/* Blockquotes */
blockquote {
  border-left: 3px solid var(--teal);
  margin: 10px 0;
  padding: 8px 14px;
  background: var(--gray-50);
  color: var(--gray-600);
  font-style: italic;
}

/* Status badges */
.status-live {
  display: inline-block;
  background: var(--green);
  color: white;
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 8pt;
  font-weight: 600;
}

.status-internal {
  display: inline-block;
  background: var(--purple);
  color: white;
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 8pt;
  font-weight: 600;
}

/* Watermark for internal docs */
body.internal::after {
  content: "SYSTACK INTERNAL";
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-30deg);
  font-size: 64pt;
  color: rgba(0, 26, 45, 0.04);
  font-weight: 900;
  pointer-events: none;
  z-index: -1;
  white-space: nowrap;
}

/* Page breaks */
.page-break { page-break-before: always; }
"""

# Client Brand Palettes (for brand reference tables in documents)
CLIENT_BRANDS = {
    "utopia-deli": {
        "name": "Utopia Deli",
        "colors": [
            ("Primary", "Deep Burgundy", "#590B3F", "#590B3F"),
            ("Primary Light", "Burgundy Light", "#7a1a55", "#7a1a55"),
            ("Accent", "Rust Red", "#AF3D4B", "#AF3D4B"),
            ("Accent Hover", "Rust Light", "#c44d5b", "#c44d5b"),
            ("Secondary", "Purple", "#754681", "#754681"),
            ("Gold", "Warm Gold", "#D59F5C", "#D59F5C"),
            ("Gold Light", "Cream", "#f5e6d0", "#f5e6d0"),
            ("Background", "Off-White", "#FBFCFE", "#FBFCFE"),
            ("Card", "White", "#FFFFFF", "#FFFFFF"),
            ("Text", "Dark Gray", "#1F2937", "#1F2937"),
            ("Text Light", "Medium Gray", "#6B7280", "#6B7280"),
            ("Border", "Light Gray", "#E5E7EB", "#E5E7EB"),
            ("Success", "Green", "#22c55e", "#22c55e"),
            ("Error", "Red", "#dc2626", "#dc2626"),
        ]
    },
    "systack": {
        "name": "Systack",
        "colors": [
            ("Headers, CTAs", "Navy", "#001a2d", "#001a2d"),
            ("Navy Light", "Navy Light", "#002845", "#002845"),
            ("Secondary accents", "Teal", "#007da9", "#007da9"),
            ("Primary buttons, links", "Cyan", "#00a1db", "#00a1db"),
            ("Gradients", "Cyan Bright", "#00c5e0", "#00c5e0"),
            ("Backgrounds", "Gray 50", "#f8fafc", "#f8fafc"),
            ("Cards", "Gray 100", "#f1f5f9", "#f1f5f9"),
            ("Borders", "Gray 200", "#e2e8f0", "#e2e8f0"),
            ("Muted text", "Gray 400", "#94a3b8", "#94a3b8"),
            ("Body text", "Gray 600", "#475569", "#475569"),
            ("Headings", "Gray 800", "#1e293b", "#1e293b"),
            ("Success", "Green", "#22c55e", "#22c55e"),
            ("Error", "Red", "#ef4444", "#ef4444"),
            ("Accent highlights", "Purple", "#8b5cf6", "#8b5cf6"),
        ]
    },
}


def parse_meta(markdown: str) -> tuple:
    """Extract metadata from first lines of markdown."""
    lines = markdown.strip().split("\n")
    meta = {}
    content_start = 0

    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("**Document ID:**"):
            meta["doc_id"] = line.replace("**Document ID:**", "").strip()
        elif line.startswith("**Version:**"):
            meta["version"] = line.replace("**Version:**", "").strip()
        elif line.startswith("**Status:**"):
            meta["status"] = line.replace("**Status:**", "").strip()
        elif line.startswith("**Prepared for:**"):
            meta["prepared_for"] = line.replace("**Prepared for:**", "").strip()
        elif line.startswith("**Prepared by:**"):
            meta["prepared_by"] = line.replace("**Prepared by:**", "").strip()
        elif line.startswith("**Date:**"):
            meta["date"] = line.replace("**Date:**", "").strip()
        elif line.startswith("**Support:**"):
            meta["support"] = line.replace("**Support:**", "").strip()
        elif line.startswith("**Builder:**"):
            meta["builder"] = line.replace("**Builder:**", "").strip()
        elif line.startswith("**Source System:**"):
            meta["source"] = line.replace("**Source System:**", "").strip()
        elif line.startswith("# "):
            meta["title"] = line.replace("# ", "").strip()
            content_start = i
            break
        elif line and not line.startswith("**"):
            content_start = i
            break

    return meta, content_start


def build_brand_table_html(brand="systack"):
    """Generate the brand color reference table for a specific client."""
    brand_data = CLIENT_BRANDS.get(brand, CLIENT_BRANDS["systack"])
    colors = brand_data["colors"]
    rows = ""
    for role, name, hex_val, bg in colors:
        rows += f'<tr><td>{role}</td><td>{name}</td><td><span class="swatch" style="background:{bg}"></span> {hex_val}</td></tr>\n'
    return f"""<table class="brand-table">
<thead><tr><th>Role</th><th>Color</th><th>Hex</th></tr></thead>
<tbody>{rows}</tbody>
</table>"""


def build_meta_html(meta: dict) -> str:
    """Build metadata table HTML."""
    rows = []
    fields = [
        ("doc_id", "Document ID"),
        ("version", "Version"),
        ("status", "Status"),
        ("prepared_for", "Prepared for"),
        ("prepared_by", "Prepared by"),
        ("builder", "Builder"),
        ("source", "Source System"),
        ("date", "Date"),
        ("support", "Support"),
    ]
    for key, label in fields:
        val = meta.get(key, "")
        if val:
            if key == "status":
                cls = "status-live" if "live" in val.lower() else "status-internal" if "internal" in val.lower() else ""
                val = f'<span class="{cls}">{val}</span>' if cls else val
            rows.append(f"<tr><td>{label}</td><td>{val}</td></tr>")
    if not rows:
        return ""
    return f'<table class="meta-table">\n{"".join(rows)}\n</table>'


def build_html(markdown: str, title: str = None, brand: str = "systack") -> str:
    """Build complete standalone HTML document with SyStack styling and client brand table."""
    meta, content_start = parse_meta(markdown)

    doc_title = title or meta.get("title", "Document")
    doc_id = meta.get("doc_id", "")
    date = meta.get("date", "")
    subtitle = meta.get("prepared_for", "")
    is_internal = "internal" in meta.get("status", "").lower()

    # Get content after metadata
    content_lines = markdown.split("\n")[content_start:]
    body_md = "\n".join(content_lines)

    # Convert body MD to HTML using pandoc
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(body_md)
        md_path = f.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
        html_path = f.name

    subprocess.run(
        ["pandoc", md_path, "-f", "markdown", "-t", "html", "--no-highlight", "-o", html_path],
        check=True, capture_output=True
    )

    with open(html_path, "r") as f:
        body_html = f.read()

    os.unlink(md_path)
    os.unlink(html_path)

    # Build metadata section
    meta_html = build_meta_html(meta)
    brand_html = build_brand_table_html(brand)

    # Header/footer
    header_text = f"{doc_title} — {doc_id or date}"
    footer_text = f"Systack (systack.net) | {doc_title} | Page <span class='pageNumber'></span>"

    body_class = "internal" if is_internal else ""
    doc_label = "SYSTACK INTERNAL" if is_internal else "CLIENT DELIVERABLE"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{doc_title}</title>
<style>
{SYSTACK_CSS}
</style>
</head>
<body class="{body_class}">

<div class="page-header">{header_text}</div>
<div class="page-footer">{footer_text}</div>

<div class="cover-bar">
    <div class="doc-label">{doc_label}</div>
    <h1>{doc_title}</h1>
    <div class="subtitle">{subtitle or "Systack Documentation"}</div>
</div>

{meta_html}

{brand_html}

{body_html}

</body>
</html>"""

    return html


async def html_to_pdf(html: str, pdf_path: str):
    """Render HTML to PDF using headless Chromium."""
    browser = await launch(
        headless=True,
        args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
        ]
    )

    try:
        page = await browser.newPage()
        await page.setContent(html)

        # A4 size
        await page.pdf({
            'path': pdf_path,
            'format': 'A4',
            'margin': {
                'top': '20mm',
                'bottom': '25mm',
                'left': '22mm',
                'right': '22mm',
            },
            'printBackground': True,
            'displayHeaderFooter': False,
            'preferCSSPageSize': True,
        })
    finally:
        await browser.close()


def generate_pdf(md_path: str, pdf_path: str, title: str = None, brand: str = "systack"):
    """Convert markdown file to branded PDF."""
    with open(md_path, "r") as f:
        markdown = f.read()

    html = build_html(markdown, title, brand)
    asyncio.run(html_to_pdf(html, pdf_path))
    print(f"✅ Generated: {pdf_path}")


def batch_generate(directory: str, brand: str = "systack"):
    """Convert all markdown files in directory to PDFs."""
    md_files = sorted(Path(directory).glob("*.md"))
    md_files = [f for f in md_files if f.name not in ("generate_pdf.py", "generate_pdf_v1.py")]

    if not md_files:
        print(f"No markdown files found in {directory}")
        return

    for md_file in md_files:
        pdf_file = md_file.with_suffix(".pdf")
        generate_pdf(str(md_file), str(pdf_file), brand=brand)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SyStack Branded PDF Generator v2 (pandoc + Chromium)")
    parser.add_argument("input", nargs="?", help="Input markdown file")
    parser.add_argument("output", nargs="?", help="Output PDF file")
    parser.add_argument("--title", help="Document title override")
    parser.add_argument("--all", action="store_true", help="Batch convert all markdown files in docs/automations/order-system/")
    parser.add_argument("--dir", help="Batch convert all markdown files in specified directory")
    parser.add_argument("--brand", default="systack", help="Client brand for reference table: utopia-deli, systack")

    args = parser.parse_args()

    if args.all:
        batch_generate("docs/automations/order-system/", brand=args.brand)
    elif args.dir:
        batch_generate(args.dir, brand=args.brand)
    elif args.input and args.output:
        generate_pdf(args.input, args.output, args.title, brand=args.brand)
    else:
        parser.print_help()
        sys.exit(1)
