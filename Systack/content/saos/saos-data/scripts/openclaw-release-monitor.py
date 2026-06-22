#!/usr/bin/env python3
"""
OpenClaw Release Monitor
Checks GitHub releases for new versions and logs findings.
Run via cron — does NOT auto-update, only notifies.
"""

import json
import urllib.request
import urllib.error
import os
import sys
from datetime import datetime, timezone

RELEASES_API = "https://api.github.com/repos/openclaw/openclaw/releases?per_page=10"
STATE_FILE = os.path.expanduser("~/.openclaw/workspaces/sol/memory/.dreams/openclaw-releases.json")
LOG_FILE = os.path.expanduser(f"~/.openclaw/workspaces/sol/memory/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-openclaw-releases.md")

INTEREST_KEYWORDS = [
    "memory-core", "memory", "dreaming", "dream", "fleet", "agent",
    "n8n", "workflow", "performance", "fix", "improvement", "enhance",
    "MCP", "context", "embedding", "vector", "sync", "scaling"
]

def fetch_releases():
    req = urllib.request.Request(RELEASES_API, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "sol-release-monitor"
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"last_check": None, "known_releases": [], "new_since_last": []}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def log_entry(text):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(text + "\n")

def is_interesting(release_body: str) -> tuple[bool, list[str]]:
    body_lower = (release_body or "").lower()
    matched = [kw for kw in INTEREST_KEYWORDS if kw.lower() in body_lower]
    return bool(matched), matched

def main():
    now = datetime.now(timezone.utc).isoformat()
    state = load_state()
    
    try:
        releases = fetch_releases()
    except Exception as e:
        log_entry(f"\n## {now} — CHECK FAILED\n- Error: {e}\n")
        save_state({**state, "last_check": now})
        return

    current_tags = [r["tag_name"] for r in releases]
    known = set(state.get("known_releases", []))
    new_tags = [t for t in current_tags if t not in known]
    
    # Always log check
    log_entry(f"\n## {now} — Release Check\n- Checked: {len(releases)} releases\n- Known: {len(known)}\n- New since last: {len(new_tags)}\n")
    
    interesting_releases = []
    
    if new_tags:
        log_entry("### New Releases Detected")
        for tag in new_tags:
            release = next(r for r in releases if r["tag_name"] == tag)
            published = release.get("published_at", "unknown")
            body = release.get("body", "")
            prerelease = "🧪 BETA" if release.get("prerelease") else "🚀 STABLE"
            
            is_interesting_flag, matched_kws = is_interesting(body)
            interest_badge = "⭐ INTERESTING" if is_interesting_flag else ""
            
            body_snippet = body[:500].replace("\n", " ")
            log_entry(f"- **{tag}** ({prerelease}) {interest_badge} — Published: {published}\n  - {body_snippet}...")
            
            if is_interesting_flag:
                interesting_releases.append({
                    "tag": tag,
                    "published": published,
                    "prerelease": release.get("prerelease", False),
                    "matched_keywords": matched_kws,
                    "body": body
                })
        
        state["new_since_last"] = new_tags
    
    state["last_check"] = now
    state["known_releases"] = current_tags
    save_state(state)
    
    # Summary print
    print(f"Checked {len(releases)} releases. New: {len(new_tags)}")
    if new_tags:
        print("NEW RELEASES:", ", ".join(new_tags))
    
    if interesting_releases:
        print(f"\n⭐ {len(interesting_releases)} INTERESTING RELEASE(S) FOUND:")
        for r in interesting_releases:
            status = "BETA" if r["prerelease"] else "STABLE"
            print(f"  - {r['tag']} ({status}) — Keywords: {', '.join(r['matched_keywords'])}")
            
            # Log summary for Green
            log_entry(f"\n### 🌿 Green Summary — {r['tag']}")
            log_entry(f"- **Status:** {'Beta' if r['prerelease'] else 'Stable'} release")
            log_entry(f"- **Published:** {r['published']}")
            log_entry(f"- **Matched Keywords:** {', '.join(r['matched_keywords'])}")
            log_entry(f"- **Full Body:**\n```\n{r['body'][:2000]}\n```")
            
            if not r["prerelease"]:
                log_entry(f"- **Recommendation:** Consider updating — stable release with relevant improvements.")
            else:
                log_entry(f"- **Recommendation:** Monitor for stable promotion — beta with interesting features.")
    else:
        print("\nNo interesting releases found.")
        log_entry("\n### No relevant releases for our criteria today.")

if __name__ == "__main__":
    main()
