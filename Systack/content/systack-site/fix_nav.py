#!/usr/bin/env python3
"""Standardize top nav and footer nav across main SyStack pages."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.resolve()

TOP_NAV_STANDARD = """  <nav>
    <div class="nav-logo">
      <a href="/" style="display:flex;align-items:center;gap:10px;text-decoration:none;">
        <img src="brand/logo-nav.png" alt="Systack" class="nav-logo-img" width="40" height="40">
        <div class="nav-logo-text">Sy<span>Stack</span>.net</div>
      </a>
    </div>
    <div class="nav-menu">
      <a href="/">Home</a>
      <a href="/services.html">Business Systems</a>
      <a href="/saos/">SAOS</a>
      <a href="/work/">Our Work</a>
      <a href="/pricing.html">Pricing</a>
      <a href="/contact.html">Contact</a>
      <a href="/audit/" target="_blank" rel="noopener noreferrer" style="color:var(--cyan);font-weight:700;">🎯 Free Audit</a>
    </div>
    <a href="/contact.html" class="nav-cta">Get Started</a>
  </nav>"""

FOOTER_NAV_STANDARD = """    <div class="footer-nav">
      <a href="/">Home</a>
      <a href="/services.html">Business Systems</a>
      <a href="/saos/">SAOS</a>
      <a href="/work/">Our Work</a>
      <a href="/pricing.html">Pricing</a>
      <a href="/about.html">About</a>
      <a href="/contact.html">Contact</a>
      <a href="/audit/" target="_blank" rel="noopener noreferrer">🎯 Free Audit</a>
    </div>"""

# active_href is the href value of the page's nav link.
PAGES = {
    "index.html": {"active_href": "/", "preserve_logo_box": True},
    "about.html": {"active_href": None},
    "services.html": {"active_href": "/services.html"},
    "pricing.html": {"active_href": "/pricing.html"},
    "contact.html": {"active_href": "/contact.html"},
    "discovery.html": {"active_href": None},
}


def build_top_nav(active_href, preserve_logo_box=False):
    if preserve_logo_box:
        nav = """  <nav>
    <div class="nav-logo">
      <a href="/" style="display:flex;align-items:center;gap:10px;text-decoration:none;">
        <img src="brand/logo-nav.png" alt="Systack" class="nav-logo-img" width="40" height="40">
        <div class="nav-logo-text">Sy<span>Stack</span>.net</div>
      </a>
      <div style="background:linear-gradient(135deg,#ff9800,#f57c00);color:white;padding:24px;border-radius:12px;text-align:center;margin-top:20px;">
        <h4 style="margin:0 0 8px;font-size:16px;">🎯 Not Sure Where to Start?</h4>
        <p style="margin:0 0 12px;font-size:14px;opacity:0.95;">Take our 60-second automation audit. Get a scored report showing exactly where your business is leaking revenue.</p>
        <a href="/audit/" target="_blank" rel="noopener noreferrer" style="background:white;color:#f57c00;padding:10px 24px;border-radius:8px;font-weight:700;text-decoration:none;font-size:14px;display:inline-block;">Get Free Audit Report →</a>
      </div>
    </div>
    <div class="nav-menu">
      <a href="/">Home</a>
      <a href="/services.html">Business Systems</a>
      <a href="/saos/">SAOS</a>
      <a href="/work/">Our Work</a>
      <a href="/pricing.html">Pricing</a>
      <a href="/contact.html">Contact</a>
      <a href="/audit/" target="_blank" rel="noopener noreferrer" style="color:var(--cyan);font-weight:700;">🎯 Free Audit</a>
    </div>
    <a href="/contact.html" class="nav-cta">Get Started</a>
  </nav>"""
    else:
        nav = TOP_NAV_STANDARD

    if active_href == "/":
        nav = nav.replace('<a href="/">Home</a>', '<a href="/" class="active">Home</a>')
    elif active_href:
        # Match <a href="/xxx.html"> and add class="active" after the href.
        nav = re.sub(
            rf'(<a href="{re.escape(active_href)}")(>)',
            r'\1 class="active"\2',
            nav,
            count=1
        )
    return nav


def replace_top_nav(text, active_href, preserve_logo_box=False):
    new_nav = build_top_nav(active_href, preserve_logo_box)
    pattern = re.compile(r'\s*<nav>.*?</nav>\s*', re.DOTALL)
    return pattern.sub(lambda m: "\n\n" + new_nav + "\n", text, count=1)


def replace_footer_nav(text):
    pattern = re.compile(
        r'\s*<div class="footer-nav">.*?</div>\s*',
        re.DOTALL
    )
    return pattern.sub(lambda m: "\n" + FOOTER_NAV_STANDARD + "\n", text, count=1)


def main():
    for filename, cfg in PAGES.items():
        path = ROOT / filename
        if not path.exists():
            print(f"Skipping missing file: {filename}")
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        text = replace_top_nav(text, cfg.get("active_href"), cfg.get("preserve_logo_box", False))
        text = replace_footer_nav(text)
        if text != original:
            path.write_text(text, encoding="utf-8")
            print(f"Updated nav/footer in {filename}")
        else:
            print(f"No changes needed for {filename}")


if __name__ == "__main__":
    main()
