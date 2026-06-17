#!/usr/bin/env python3
"""
write-guard.py — Fleet Write Guard Utility
Enforces path-based authorization before file writes to Obsidian vault or fleet workspace.

Part of PLAN-HUBSPOKE-001 (P1)
Authorized by Green (KUDU-7 confirmed)
Built by CODY (Technical Architect)
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple

# ── Path Classification Rules ────────────────────────────────────────────────

LOW_RISK_PATTERNS = [
    "02-Memory/daily-logs/",
    "02-Memory/plans/",
    "memory/",
    "memory/daily-logs/",
    "memory/plans/",
    "artifacts/",
    "artifacts/enforcement-layer/",
]

MEDIUM_RISK_PATTERNS = [
    "03-Projects/",
    "04-Clients/",
    "content-creation/",
    "demos/",
]

HIGH_RISK_PATTERNS = [
    "05-Financials/",
    "09-SOL-System/",
    "credentials/",
    "secrets/",
    "config/",
    "openclaw.json",
    ".env",
    ".env.local",
    ".env.production",
    ".openclaw/openclaw.json",
    "gateway.json",
    "pipeline.db",
    "fleet_observability.db",
]

# Obsidian vault base paths to check
VAULT_BASES = [
    Path.home() / "Library" / "Mobile Documents" / "iCloud~md~obsidian" / "Documents" / "My vault",
    Path.home() / "Documents" / "My vault",
    Path.home() / ".openclaw" / "workspaces" / "sol",
]

# ── Core Functions ───────────────────────────────────────────────────────────

def normalize_path(target_path: str) -> Path:
    """
    Normalize a path: expand user (~), resolve symlinks, make absolute.
    Returns a Path object.
    """
    expanded = os.path.expanduser(target_path)
    absolute = os.path.abspath(expanded)
    resolved = os.path.realpath(absolute)
    return Path(resolved)

def classify_path(target_path: str) -> Tuple[str, str]:
    """
    Classify a path into LOW, MEDIUM, or HIGH risk.
    Returns (risk_level, reason).
    """
    normalized = normalize_path(target_path)
    path_str = str(normalized).lower()  # Case-insensitive matching for macOS APFS

    # Check HIGH risk first (most restrictive)
    for pattern in HIGH_RISK_PATTERNS:
        if pattern.lower() in path_str:
            return ("HIGH", f"Path matches high-risk pattern: '{pattern}'")

    # Check MEDIUM risk
    for pattern in MEDIUM_RISK_PATTERNS:
        if pattern.lower() in path_str:
            return ("MEDIUM", f"Path matches medium-risk pattern: '{pattern}'")

    # Check LOW risk
    for pattern in LOW_RISK_PATTERNS:
        if pattern.lower() in path_str:
            return ("LOW", f"Path matches low-risk pattern: '{pattern}'")

    # Default: treat unknown paths as MEDIUM (safe default)
    return ("MEDIUM", "Path does not match any known low-risk pattern. Treating as medium-risk for safety.")

def check_write_permission(path: str, agent_name: str = "unknown") -> Dict:
    """
    Check if a write is permitted to the given path.

    Returns a dict:
    {
        "allowed": bool,
        "level": str,      # LOW | MEDIUM | HIGH
        "reason": str,
        "agent": str,
        "path": str,
        "timestamp": str,
    }
    """
    risk_level, reason = classify_path(path)

    allowed = risk_level in ("LOW", "MEDIUM")

    # HIGH risk is always blocked without explicit approval
    if risk_level == "HIGH":
        allowed = False

    return {
        "allowed": allowed,
        "level": risk_level,
        "reason": reason,
        "agent": agent_name,
        "path": str(normalize_path(path)),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

def request_approval(path: str, agent_name: str, reason: str = "") -> Dict:
    """
    Request manual approval for a high-risk write.
    For now, prints/logs the request. Future: integrate with messaging/notification system.

    Returns a dict with the approval request details.
    """
    normalized = normalize_path(path)
    timestamp = datetime.utcnow().isoformat() + "Z"

    approval_request = {
        "type": "APPROVAL_REQUIRED",
        "path": str(normalized),
        "agent": agent_name,
        "reason": reason,
        "timestamp": timestamp,
        "status": "PENDING",
    }

    # Print to stdout (captured by OpenClaw logs)
    print(f"\n{'='*60}")
    print(f"  WRITE GUARD — APPROVAL REQUIRED")
    print(f"{'='*60}")
    print(f"  Agent:     {agent_name}")
    print(f"  Path:      {normalized}")
    print(f"  Reason:    {reason}")
    print(f"  Timestamp: {timestamp}")
    print(f"{'='*60}")
    print(f"  ACTION: Explicit approval required from Green.")
    print(f"  Include authorization phrase to proceed.")
    print(f"{'='*60}\n")

    # Also write to stderr for log capture
    print(
        f"[WRITE-GUARD] APPROVAL_REQUIRED agent={agent_name} path={normalized} reason={reason}",
        file=sys.stderr,
    )

    return approval_request

def guarded_write(path: str, content: str, agent_name: str = "unknown") -> Dict:
    """
    High-level convenience function: check permission, request approval if needed,
    and return the full result. Does NOT actually write the file — just validates
    that the write SHOULD proceed.

    Returns dict with validation result.
    """
    permission = check_write_permission(path, agent_name)

    if permission["allowed"]:
        return {
            "status": "ALLOWED",
            "permission": permission,
            "message": f"Write permitted ({permission['level']} risk). Proceed.",
        }
    else:
        approval = request_approval(path, agent_name, permission["reason"])
        return {
            "status": "BLOCKED",
            "permission": permission,
            "approval_request": approval,
            "message": f"Write BLOCKED ({permission['level']} risk). Approval required.",
        }

# ── Test / Validation Block ──────────────────────────────────────────────────

def run_tests():
    """
    Validate the write guard with test paths.
    Called when script is executed directly.
    """
    print("=" * 60)
    print("WRITE GUARD — VALIDATION TESTS")
    print("=" * 60)

    test_cases = [
        # (path, expected_level, expected_allowed)
        ("~/Library/Mobile Documents/iCloud~md~obsidian/Documents/My vault/02-Memory/daily-logs/2026-05-30.md", "LOW", True),
        ("~/.openclaw/workspaces/sol/memory/plans/PLAN-TEST.md", "LOW", True),
        ("~/.openclaw/workspaces/sol/artifacts/enforcement-layer/test.js", "LOW", True),
        ("~/Documents/My vault/03-Projects/client-site/index.html", "MEDIUM", True),
        ("~/.openclaw/workspaces/sol/content-creation/draft.md", "MEDIUM", True),
        ("~/Documents/My vault/05-Financials/invoices/invoice-001.pdf", "HIGH", False),
        ("~/.openclaw/workspaces/sol/09-SOL-System/openclaw.json", "HIGH", False),
        ("~/.openclaw/openclaw.json", "HIGH", False),
        ("~/.openclaw/workspaces/sol/credentials/email-creds.json", "HIGH", False),
        ("/tmp/random-file.md", "MEDIUM", True),  # Unknown path defaults to MEDIUM
    ]

    passed = 0
    failed = 0

    for path, expected_level, expected_allowed in test_cases:
        result = check_write_permission(path, agent_name="CODY")
        level_ok = result["level"] == expected_level
        allowed_ok = result["allowed"] == expected_allowed

        status = "PASS" if (level_ok and allowed_ok) else "FAIL"
        if status == "PASS":
            passed += 1
        else:
            failed += 1

        print(f"\n  [{status}] Path: {path}")
        print(f"        Expected: level={expected_level}, allowed={expected_allowed}")
        print(f"        Actual:   level={result['level']}, allowed={result['allowed']}")
        print(f"        Reason:   {result['reason']}")

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 60)

    if failed > 0:
        print("\n[ERROR] Validation failed. Do not deploy.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All tests passed. Write guard is validated.")
        return True

# ── Main Entry Point ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_tests()
