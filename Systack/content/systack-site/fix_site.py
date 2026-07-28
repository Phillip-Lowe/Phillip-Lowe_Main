#!/usr/bin/env python3
"""Bulk fixes for SyStack site validation."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.resolve()

def fix_clean_urls(text):
    """Replace clean URLs with .html versions for the listed pages."""
    for page in ["contact", "pricing", "services", "about", "discovery"]:
        pattern = rf'href="/{page}(?=["#?\s])'
        replacement = rf'href="/{page}.html'
        text = re.sub(pattern, replacement, text)
    return text

def add_rel_to_external_blank_links(text, file_path):
    """Add rel=noopener noreferrer to any <a> with target=_blank missing rel."""

    def replace_tag(match):
        prefix = match.group(1)
        attrs_before_target = match.group(2)
        target_attr = match.group(3)
        attrs_after_target = match.group(4)
        # If rel is already present anywhere in the tag, leave it alone.
        full_inner = attrs_before_target + " " + target_attr + " " + attrs_after_target
        if re.search(r'\brel\s*=\s*["\']', full_inner, re.IGNORECASE):
            return match.group(0)
        return f'<a{prefix}{attrs_before_target} {target_attr}{attrs_after_target} rel="noopener noreferrer">'

    # Match <a ... target="_blank" ...> (case-insensitive, spaces flexible)
    pattern = re.compile(
        r'<a(\s+)((?:[^>]*?\s+)?)(target\s*=\s*["\']_blank["\'])((?:\s+[^>]*)?)>',
        re.IGNORECASE | re.DOTALL
    )
    return pattern.sub(replace_tag, text)

def main():
    html_files = sorted(ROOT.rglob("*.html"))
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        original = text
        text = fix_clean_urls(text)
        text = add_rel_to_external_blank_links(text, path)
        if text != original:
            path.write_text(text, encoding="utf-8")
            print(f"Updated {path.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
