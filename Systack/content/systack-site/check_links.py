#!/usr/bin/env python3
"""Check that internal links in HTML files point to existing files."""
import re
from pathlib import Path
from urllib.parse import urlparse, urljoin

ROOT = Path(__file__).parent.resolve()

EXTERNAL_PREFIXES = (
    "http://", "https://", "mailto:", "tel:", "#",
)

# Files that exist but aren't checked because they are dynamic/endpoints.
IGNORED_PATHS = {
    "/audit/",  # directory index handled by audit/index.html
    "/saos/",
    "/work/",
    "/case-studies/",
    "/services/",
    "/docs/client/",
    "/demos/",
    "/personal-agent/",
    "/partners/",
}


def is_external(href):
    return href.startswith(EXTERNAL_PREFIXES) or href.startswith("//")


def resolve_link(href, base_file):
    """Resolve an href to an absolute file path relative to ROOT."""
    if is_external(href):
        return None, "external"

    if href.startswith("/"):
        # Absolute path within site.
        path_part = href.split("?")[0].split("#")[0]
        # Strip trailing slash for directory index resolution.
        if path_part.endswith("/"):
            candidate = ROOT / path_part.lstrip("/") / "index.html"
        else:
            candidate = ROOT / path_part.lstrip("/")
        return candidate, "absolute"
    else:
        # Relative path.
        path_part = href.split("?")[0].split("#")[0]
        base_dir = base_file.parent
        candidate = (base_dir / path_part).resolve()
        return candidate, "relative"


def main():
    html_files = sorted(ROOT.rglob("*.html"))
    broken = []
    checked = 0

    for path in html_files:
        text = path.read_text(encoding="utf-8")
        # Find all href attributes.
        for match in re.finditer(r'href\s*=\s*"([^"]+)"', text):
            href = match.group(1).strip()
            if not href or href == "#" or is_external(href):
                continue
            checked += 1
            candidate, kind = resolve_link(href, path)
            if candidate is None:
                continue
            rel = candidate.relative_to(ROOT)
            if not candidate.exists():
                # Allow directory index fallback.
                if str(rel).endswith("/index.html"):
                    dir_path = candidate.parent
                    if dir_path.exists() and dir_path.is_dir():
                        continue
                broken.append((path.relative_to(ROOT), href, str(rel)))

    print(f"Checked {checked} internal links across {len(html_files)} HTML files.")
    if broken:
        print(f"\nBROKEN LINKS ({len(broken)}):")
        for src, href, target in broken:
            print(f"  {src}: href={href} -> missing {target}")
        return 1
    else:
        print("No broken internal links found.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
