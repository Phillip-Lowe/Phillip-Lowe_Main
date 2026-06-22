---
name: branded-pdf-generator
description: "Convert Markdown files to branded, print-ready PDFs with SyStack color palette. Uses pandoc for MD→HTML and headless Chromium (pyppeteer) for CSS→PDF rendering."
---

# Branded PDF Generator

Reliable Markdown → Branded PDF pipeline for Systack client deliverables and internal documentation.

## Quick Start

```bash
# Single file
python3 scripts/generate_pdf.py input.md output.pdf --title "Document Title"

# Batch convert all .md files in a directory
python3 scripts/generate_pdf.py --dir /path/to/docs/

# Batch convert order-system docs
python3 scripts/generate_pdf.py --all
```

## Stack (Why This Works)

| Tool | Role | Why |
|------|------|-----|
| **pandoc** (`brew install pandoc`) | Markdown → HTML | Robust parser, handles all MD features |
| **pyppeteer** (`pip3 install pyppeteer`) | HTML → PDF | Headless Chromium, full CSS rendering |
| **SyStack CSS** (embedded) | Branding | Navy/teal/cyan palette, cover bar, tables |

## What Was Tried and Rejected (Lessons Learned 2026-06-16)

| Approach | Verdict | Why It Failed |
|----------|---------|---------------|
| **fpdf2** | ❌ Rejected | No CSS layout engine. Manual positioning. Poor typography. Unicode font issues. 80KB output vs 260KB proper. |
| **WeasyPrint** | ❌ Rejected | System library hell on macOS. Requires gobject/pango/cffi. `ctypes.util.find_library` returns None for brew-installed libs. Symlinks don't help (cffi uses soname, not filename). |
| **wkhtmltopdf** | ❌ Rejected | Removed from Homebrew. Unmaintained. |
| **MacTeX + pandoc** | ❌ Rejected | 4GB install for LaTeX. Overkill for styled docs. |
| **pandoc + pyppeteer** | ✅ Winner | pandoc handles MD parsing perfectly. Chromium handles CSS perfectly. Both are reliable, maintained tools. |

## Dependencies

```bash
# Required
brew install pandoc
pip3 install pyppeteer

# Optional (for PDF preview/thumbnail)
pip3 install pdf2image
```

First run of pyppeteer downloads Chromium (~141MB) automatically.

## Branding

All PDFs use the **SyStack color palette**:

| Role | Color | Hex |
|------|-------|-----|
| Headers, CTAs | Navy | `#001a2d` |
| Secondary accents | Teal | `#007da9` |
| Primary buttons, links | Cyan | `#00a1db` |
| Gradients | Cyan Bright | `#00c5e0` |
| Body text | Gray 600 | `#475569` |
| Headings | Gray 800 | `#1e293b` |
| Success | Green | `#22c55e` |
| Error | Red | `#ef4444` |

## Document Features

- **Cover bar**: Navy→teal gradient with "CLIENT DELIVERABLE" or "SYSTACK INTERNAL" label
- **Brand reference table**: Full color palette with visual swatches on every document
- **Metadata table**: Document ID, version, status, date, support info
- **Running headers/footers**: Document title, page numbers, Systack attribution
- **Proper typography**: CSS `@page` rules, A4 sizing, print-ready margins
- **Internal watermark**: "SYSTACK INTERNAL" diagonal watermark on internal docs

## File Structure

```
branded-pdf-generator/
  SKILL.md              # This file
  scripts/
    generate_pdf.py     # Main PDF generator script
  references/
    lessons-learned.md  # Detailed failure log for each approach tried
  assets/
    systack-colors.css  # Standalone SyStack CSS (reusable)
```

## Usage Notes

- Markdown files should include metadata as bold fields at top (see template)
- Internal docs are auto-detected by keywords in filename ("internal", "implementation", "workflow", "troubleshooting", "architecture")
- Pandoc must be in PATH
- First pyppeteer run downloads Chromium to `~/Library/Application Support/pyppeteer/`
- Output PDFs are ~200-300KB with full CSS rendering
