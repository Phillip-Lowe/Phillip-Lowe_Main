# Lessons Learned — PDF Generation on macOS
## 2026-06-16

---

## Approach 1: fpdf2 (Pure Python)

**Library:** `fpdf2` v2.8.4  
**Time spent:** ~45 min  
**Verdict:** ❌ Rejected

### What worked
- Pure Python, no system dependencies
- Already installed in the environment
- Generated a PDF on first attempt

### What failed
- **No CSS layout engine** — every element positioned manually with x/y coordinates
- **No proper typography** — manual font size, line height, spacing for everything
- **Unicode issues** — Helvetica core font doesn't support em-dash, smart quotes, etc.
- **Font dependency hell** — had to find and register Arial Unicode.ttf, Courier New.ttf
- **SFNSMono.ttf crashed** — Apple's system mono font has `fvar` table issues with fontTools subsetting
- **Manual markdown parsing** — wrote a regex-based MD→HTML converter that was fragile
- **Inline formatting nightmare** — bold, code, links all had to be manually tokenized mid-paragraph
- **Output quality** — 80KB PDFs vs 260KB from Chromium. Visibly lower quality.
- **No CSS @page rules** — can't do running headers/footers, page breaks, or A4 sizing properly

### Conclusion
fpdf2 is for simple receipts and labels, not branded documentation. Wrong tool.

---

## Approach 2: WeasyPrint (Python + System Libs)

**Library:** `weasyprint` v66.0  
**Time spent:** ~30 min  
**Verdict:** ❌ Rejected

### What worked
- Already installed (`pip3 install weasyprint` succeeded)
- Excellent CSS → PDF engine in theory
- Supports `@page` rules, running headers, proper typography

### What failed
- **System library dependency hell on macOS:**
  - Requires `libgobject-2.0`, `libglib-2.0`, `libpango-1.0`, `libpangocairo`, `libpangoft2`
  - These are installed via Homebrew at `/opt/homebrew/lib/`
  - But `ctypes.util.find_library()` returns `None` for all of them on macOS
  - cffi looks for Linux-style sonames (`libgobject-2.0-0`) not macOS dylib names
  - Created symlinks (`libgobject-2.0-0.dylib` → `libgobject-2.0.0.dylib`) — didn't help
  - `DYLD_LIBRARY_PATH=/opt/homebrew/lib` didn't help
  - The cffi `_dlopen` function uses its own search logic, not dyld

### Root cause
WeasyPrint's `text/ffi.py` hardcodes Linux library names. macOS Homebrew uses different naming conventions. This is a known, unresolved issue.

### Conclusion
WeasyPrint is excellent on Linux. On macOS, it's a time sink. Don't try unless you're on a Linux server.

---

## Approach 3: wkhtmltopdf

**Tool:** wkhtmltopdf  
**Time spent:** ~2 min  
**Verdict:** ❌ Rejected

### What failed
- Removed from Homebrew (`No available formula with the name "wkhtmltopdf"`)
- Project is unmaintained (last release 2017)
- QtWebKit engine is outdated, doesn't support modern CSS

### Conclusion
Dead project. Not worth pursuing.

---

## Approach 4: MacTeX + pandoc

**Tool:** MacTeX (LaTeX distribution)  
**Time spent:** ~2 min  
**Verdict:** ❌ Rejected

### What failed
- 4GB download for MacTeX
- Requires 6 additional Homebrew dependencies
- LaTeX is overkill for styled HTML→PDF conversion
- Would need to write LaTeX templates, not CSS

### Conclusion
Right tool for academic papers. Wrong tool for branded business docs.

---

## Approach 5: pandoc + pyppeteer (Headless Chromium) ✅ WINNER

**Tools:** pandoc 3.10 + pyppeteer 2.0.0  
**Time spent:** ~20 min  
**Verdict:** ✅ Adopted

### What worked
- **pandoc** (`brew install pandoc`): 277MB, installed in 60 seconds
  - Robust Markdown → HTML conversion
  - Handles all MD features (tables, code blocks, lists, links, formatting)
  - No custom parser needed
  
- **pyppeteer** (`pip3 install pyppeteer`): installed in 5 seconds
  - Headless Chromium (auto-downloads ~141MB on first run)
  - Full CSS rendering — gradients, flexbox, @page rules, running headers
  - `page.pdf()` method with A4 format, margins, printBackground
  - Output: 260KB PDFs with professional quality

### Key implementation details
- pandoc converts body MD → HTML fragment
- Python script wraps it in full HTML with embedded SyStack CSS
- pyppeteer renders the complete HTML to PDF
- CSS `@page` rules handle A4 sizing, margins, running headers/footers
- CSS `position: running()` for page headers/footers
- CSS gradient on cover bar renders perfectly
- Color swatches in brand table render as actual colored squares

### Minor issues
- `setContent()` doesn't accept `waitUntil` kwarg in pyppeteer 2.0.0 (removed it)
- First run downloads Chromium (~30 seconds, one-time)

### Conclusion
This is the stack. Reliable, maintainable, professional output. Use it for all Systack PDF generation.

---

## Decision Record

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-06-16 | Adopt pandoc + pyppeteer for all PDF generation | Only stack that works reliably on macOS with professional output |
| 2026-06-16 | Reject fpdf2 for documentation | No CSS, manual layout, poor typography |
| 2026-06-16 | Reject WeasyPrint on macOS | System library incompatibility, unresolved |
| 2026-06-16 | Reject wkhtmltopdf | Unmaintained, removed from Homebrew |
| 2026-06-16 | Reject MacTeX for business docs | 4GB overkill, wrong tool |

---

## Skill Location

`~/.openclaw/skills/branded-pdf-generator/`
