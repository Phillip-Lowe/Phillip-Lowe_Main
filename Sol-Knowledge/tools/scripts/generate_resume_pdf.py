#!/usr/bin/env python3
"""
Clean Resume/Cover Letter PDF Generator
========================================
Professional resume-style PDF using pandoc + headless Chromium.
No branding, no cover bars, no client deliverable banners — just clean typography.
"""

import sys
import os
import subprocess
import tempfile
import asyncio
from pathlib import Path
from pyppeteer import launch

RESUME_CSS = """
@page {
  size: letter;
  margin: 1.9cm 2.2cm 2.2cm 2.2cm;
}

@page :first {
  margin-top: 1.5cm;
}

body {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.55;
  color: #1e293b;
}

/* Header / Contact */
.resume-header {
  text-align: center;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1.5px solid #0f766e;
}

.resume-header h1 {
  font-size: 22pt;
  font-weight: 700;
  color: #0f766e;
  margin: 0 0 6px 0;
  letter-spacing: 0.5px;
  page-break-before: avoid;
}

.resume-header .contact {
  font-size: 9.5pt;
  color: #475569;
  margin: 0;
}

/* Section headings */
h2 {
  font-size: 11pt;
  font-weight: 700;
  color: #0f766e;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  margin: 18px 0 8px 0;
  padding-bottom: 3px;
  border-bottom: 1px solid #cbd5e1;
  page-break-after: avoid;
}

/* Job entries */
h3 {
  font-size: 10.5pt;
  font-weight: 700;
  color: #1e293b;
  margin: 12px 0 2px 0;
  page-break-after: avoid;
}

h3 + p {
  margin: 0 0 6px 0;
  font-size: 9.5pt;
  color: #475569;
  font-style: italic;
}

/* Body text */
p {
  margin: 4px 0 8px 0;
}

/* Bullet lists */
ul {
  margin: 4px 0 10px 0;
  padding-left: 20px;
}

li {
  margin: 3px 0;
}

/* Horizontal rules — page breaks between resume and cover letter */
hr {
  border: none;
  border-top: 2px solid #0f766e;
  margin: 24px 0;
  page-break-before: always;
}

/* Strong text */
strong {
  color: #1e293b;
}

/* Links */
a {
  color: #0f766e;
  text-decoration: none;
}

/* Cover letter styling */
.cover-letter {
  margin-top: 0;
}

.cover-letter p {
  margin: 8px 0;
}

.cover-letter .signature {
  margin-top: 20px;
}

.cover-letter .signature p {
  margin: 2px 0;
}

/* Two-column for competencies */
.competency-grid {
  column-count: 2;
  column-gap: 30px;
}

.competency-grid p {
  margin: 2px 0;
  font-size: 9.8pt;
  break-inside: avoid;
}
"""


def build_resume_html(markdown: str) -> str:
    """Convert markdown to clean resume HTML."""
    # Convert MD to HTML via pandoc
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(markdown)
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

    # Clean up: wrap header, fix cover letter section
    body_html = body_html.replace(
        '<h1>Phillip Lowe</h1>',
        '<div class="resume-header">\n<h1>Phillip Lowe</h1>\n<p class="contact">Little Rock, AR 72204 &nbsp;|&nbsp; (501) 274-6231 &nbsp;|&nbsp; plowe95@yahoo.com</p>\n</div>'
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Phillip Lowe — Resume</title>
<style>
{RESUME_CSS}
</style>
</head>
<body>
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

        await page.pdf({
            'path': pdf_path,
            'format': 'Letter',
            'margin': {
                'top': '19mm',
                'bottom': '22mm',
                'left': '22mm',
                'right': '22mm',
            },
            'printBackground': True,
            'displayHeaderFooter': False,
        })
    finally:
        await browser.close()


def generate_resume_pdf(md_path: str, pdf_path: str):
    """Convert markdown resume to clean PDF."""
    with open(md_path, "r") as f:
        markdown = f.read()

    html = build_resume_html(markdown)
    asyncio.run(html_to_pdf(html, pdf_path))
    print(f"✅ Generated: {pdf_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 generate_resume_pdf.py input.md output.pdf")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    generate_resume_pdf(input_file, output_file)
