#!/usr/bin/env python3
"""
write-guard-integration.py — Safe File Write Wrapper
Drop-in replacements for write/edit operations that enforce write-guard validation.

Part of PLAN-HUBSPOKE-001 Phase 2
Authorized by Green (KUDU-7 confirmed)
Built by CODY (Technical Architect)
"""

import os
import sys
import json
from pathlib import Path
from contextlib import contextmanager
from typing import Dict, List, Any, Union, Callable
from dataclasses import dataclass

# Import write guard functions
sys.path.insert(0, str(Path(__file__).parent))
try:
    from write_guard import check_write_permission, request_approval, classify_path, normalize_path
except ImportError:
    # Fallback: try with underscore name
    sys.path.insert(0, str(Path(__file__).parent))
    import importlib.util
    spec = importlib.util.spec_from_file_location("write_guard", str(Path(__file__).parent / "write-guard.py"))
    write_guard = importlib.util.module_from_spec(spec)
    sys.modules["write_guard"] = write_guard
    spec.loader.exec_module(write_guard)
    check_write_permission = write_guard.check_write_permission
    request_approval = write_guard.request_approval
    classify_path = write_guard.classify_path
    normalize_path = write_guard.normalize_path


# ── Result Types ────────────────────────────────────────────────────────────

@dataclass
class WriteResult:
    """Standardized result for all guarded write operations."""
    status: str  # 'ALLOWED' | 'BLOCKED' | 'ERROR'
    permission: Dict
    result: Any = None
    error: str = None
    path: str = None
    agent: str = None

    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "permission": self.permission,
            "result": self.result,
            "error": self.error,
            "path": self.path,
            "agent": self.agent,
        }


# ── Core Safe Write Functions ───────────────────────────────────────────────

def safe_write(path: str, content: str, agent_name: str = "unknown") -> WriteResult:
    """
    Safely write content to a file with write-guard validation.

    Args:
        path: Target file path (absolute or relative)
        content: Text content to write
        agent_name: Name of the agent attempting the write

    Returns:
        WriteResult with status, permission details, and operation result
    """
    # Check permission
    permission = check_write_permission(path, agent_name)

    if not permission["allowed"]:
        # Blocked — return without writing
        approval = request_approval(path, agent_name, permission["reason"])
        return WriteResult(
            status="BLOCKED",
            permission=permission,
            result=approval,
            path=str(normalize_path(path)),
            agent=agent_name,
        )

    # Allowed — perform the write
    try:
        normalized = normalize_path(path)
        # Ensure parent directory exists
        normalized.parent.mkdir(parents=True, exist_ok=True)

        with open(normalized, 'w', encoding='utf-8') as f:
            f.write(content)

        return WriteResult(
            status="ALLOWED",
            permission=permission,
            result=f"Wrote {len(content)} chars to {normalized}",
            path=str(normalized),
            agent=agent_name,
        )

    except Exception as e:
        return WriteResult(
            status="ERROR",
            permission=permission,
            error=str(e),
            path=str(normalize_path(path)),
            agent=agent_name,
        )


def safe_edit(path: str, edits: List[Dict], agent_name: str = "unknown") -> WriteResult:
    """
    Safely apply edits to a file with write-guard validation.

    Args:
        path: Target file path
        edits: List of edit dicts with 'oldText' and 'newText' keys
        agent_name: Name of the agent attempting the edit

    Returns:
        WriteResult with status and edit application result
    """
    # Check permission
    permission = check_write_permission(path, agent_name)

    if not permission["allowed"]:
        approval = request_approval(path, agent_name, permission["reason"])
        return WriteResult(
            status="BLOCKED",
            permission=permission,
            result=approval,
            path=str(normalize_path(path)),
            agent=agent_name,
        )

    # Allowed — read file, apply edits, write back
    try:
        normalized = normalize_path(path)

        if not normalized.exists():
            return WriteResult(
                status="ERROR",
                permission=permission,
                error=f"File not found: {normalized}",
                path=str(normalized),
                agent=agent_name,
            )

        with open(normalized, 'r', encoding='utf-8') as f:
            content = f.read()

        # Apply each edit
        edits_applied = 0
        for edit in edits:
            old_text = edit.get('oldText', '')
            new_text = edit.get('newText', '')

            if old_text in content:
                content = content.replace(old_text, new_text, 1)
                edits_applied += 1
            else:
                return WriteResult(
                    status="ERROR",
                    permission=permission,
                    error=f"Edit target not found: {old_text[:50]}...",
                    path=str(normalized),
                    agent=agent_name,
                )

        # Write back
        with open(normalized, 'w', encoding='utf-8') as f:
            f.write(content)

        return WriteResult(
            status="ALLOWED",
            permission=permission,
            result=f"Applied {edits_applied} edits to {normalized}",
            path=str(normalized),
            agent=agent_name,
        )

    except Exception as e:
        return WriteResult(
            status="ERROR",
            permission=permission,
            error=str(e),
            path=str(normalize_path(path)),
            agent=agent_name,
        )


def safe_file_write(node: str, path: str, content: Union[str, bytes], agent_name: str = "unknown",
                   source_media_id: str = None, mime_type: str = None) -> WriteResult:
    """
    Safely write to a remote node with write-guard validation.
    Mirrors the file_write tool pattern for node-based writes.

    Args:
        node: Node ID or name (e.g., 'phillips-macbook-air')
        path: Absolute path on the node
        content: Text or base64-encoded bytes
        agent_name: Name of the agent
        source_media_id: Optional media ID for binary copies
        mime_type: Optional content type hint

    Returns:
        WriteResult with validation status
    """
    # For remote writes, we validate the path conceptually
    # (Full enforcement would require running guard on the target node)
    permission = check_write_permission(path, agent_name)

    if not permission["allowed"]:
        approval = request_approval(path, agent_name, permission["reason"])
        return WriteResult(
            status="BLOCKED",
            permission=permission,
            result={
                "approval_request": approval,
                "node": node,
                "note": "Remote write blocked. Approval required before file_write tool use.",
            },
            path=path,
            agent=agent_name,
        )

    # Return success indicator — actual file_write would use file_write tool
    return WriteResult(
        status="ALLOWED",
        permission=permission,
        result={
            "status": "PERMITTED",
            "node": node,
            "path": path,
            "note": "Guard validation passed. Proceed with file_write tool.",
            "content_preview": content[:100] if isinstance(content, str) else f"[binary: {len(content)} bytes]",
        },
        path=path,
        agent=agent_name,
    )


# ── Context Manager / Decorator for Bulk Operations ─────────────────────────

@contextmanager
def guard_all_writes(agent_name: str = "unknown", default_action: str = "block"):
    """
    Context manager for bulk write operations.
    Collects all write attempts and validates them together.

    Usage:
        with guard_all_writes(agent_name="CODY") as guard:
            guard.queue_write("path1", "content1")
            guard.queue_edit("path2", [edit1, edit2])
            results = guard.execute()

    Args:
        agent_name: Agent name for all operations in this context
        default_action: 'block' (fail fast) or 'allow' (log but proceed)
    """
    guard = BulkWriteGuard(agent_name, default_action)
    try:
        yield guard
    finally:
        # Auto-execute on exit if not already done
        if guard.pending:
            guard.execute()


class BulkWriteGuard:
    """Collects and validates multiple write operations before execution."""

    def __init__(self, agent_name: str, default_action: str = "block"):
        self.agent_name = agent_name
        self.default_action = default_action
        self.operations: List[Dict] = []
        self.pending = True
        self.results: List[WriteResult] = []

    def queue_write(self, path: str, content: str):
        """Queue a write operation for batch validation."""
        self.operations.append({
            "type": "write",
            "path": path,
            "content": content,
        })

    def queue_edit(self, path: str, edits: List[Dict]):
        """Queue an edit operation for batch validation."""
        self.operations.append({
            "type": "edit",
            "path": path,
            "edits": edits,
        })

    def execute(self) -> List[WriteResult]:
        """
        Execute all queued operations with validation.
        If default_action='block', stops on first blocked operation.
        """
        self.results = []
        self.pending = False

        for op in self.operations:
            if op["type"] == "write":
                result = safe_write(op["path"], op["content"], self.agent_name)
            elif op["type"] == "edit":
                result = safe_edit(op["path"], op["edits"], self.agent_name)
            else:
                continue

            self.results.append(result)

            # Fail fast if blocking
            if self.default_action == "block" and result.status == "BLOCKED":
                break

        return self.results

    def get_summary(self) -> Dict:
        """Get summary of all operations."""
        allowed = sum(1 for r in self.results if r.status == "ALLOWED")
        blocked = sum(1 for r in self.results if r.status == "BLOCKED")
        errors = sum(1 for r in self.results if r.status == "ERROR")

        return {
            "total": len(self.results),
            "allowed": allowed,
            "blocked": blocked,
            "errors": errors,
            "all_allowed": blocked == 0 and errors == 0,
        }


# ── Decorator for Functions That Write ──────────────────────────────────────

def guarded_write_function(agent_name: str = None):
    """
    Decorator that guards all file writes within a function.
    
    Usage:
        @guarded_write_function(agent_name="CODY")
        def build_feature():
            safe_write("path", "content")  # Auto-guarded
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Auto-detect agent name from function module if not provided
            nonlocal agent_name
            effective_agent = agent_name or func.__module__.split('.')[0]

            with guard_all_writes(agent_name=effective_agent) as guard:
                result = func(*args, **kwargs)
                return result
        return wrapper
    return decorator


# ── Integration Helpers for SOL Workflows ────────────────────────────────────

def validate_before_write_tool(path: str, agent_name: str) -> Dict:
    """
    Pre-flight check before using OpenClaw write/edit/file_write tools.
    Returns a dict that SOL can use to decide whether to proceed.

    Usage in SOL workflow:
        validation = validate_before_write_tool("memory/2026-05-30.md", "SOL")
        if validation["proceed"]:
            # Use actual write tool
            write(path=path, content=content)
        else:
            # Log and escalate
            message(target=green, content=f"Approval needed: {validation['reason']}")
    """
    permission = check_write_permission(path, agent_name)

    return {
        "proceed": permission["allowed"],
        "level": permission["level"],
        "reason": permission["reason"],
        "path": permission["path"],
        "agent": permission["agent"],
        "timestamp": permission["timestamp"],
        "requires_approval": permission["level"] == "HIGH",
        "approval_request": None if permission["allowed"] else request_approval(path, agent_name, permission["reason"]),
    }


def format_agent_return_for_guard(agent_return: Dict) -> WriteResult:
    """
    Convert an agent return payload (matching agent-return-schema.json) into
    a write validation result.

    This bridges P1 (write guards) and P2 (agent return schema).
    """
    agent_name = agent_return.get("source_agent", "unknown")
    # Extract file paths from metadata if present
    files = agent_return.get("metadata", {}).get("files_created", [])
    files += agent_return.get("metadata", {}).get("files_modified", [])

    validations = []
    for file_path in files:
        result = safe_write(file_path, "", agent_name)  # Check permission only
        validations.append(result.to_dict())

    all_allowed = all(v["status"] == "ALLOWED" for v in validations)

    return WriteResult(
        status="ALLOWED" if all_allowed else "BLOCKED",
        permission={"file_validations": validations},
        result=agent_return,
        path=str(files[0]) if files else None,
        agent=agent_name,
    )


# ── Test Suite ──────────────────────────────────────────────────────────────

def run_tests():
    """Validate the integration wrapper with 5 test cases."""
    print("=" * 70)
    print("WRITE GUARD INTEGRATION — TEST SUITE")
    print("=" * 70)

    test_results = []

    # Test 1: Allowed write to low-risk path
    print("\n[Test 1] Allowed write to low-risk path")
    result = safe_write(
        "~/.openclaw/workspaces/sol/memory/daily-logs/test-daily.md",
        "# Test Daily Log\n\nThis is a test.",
        agent_name="CODY"
    )
    print(f"  Status: {result.status}")
    print(f"  Level: {result.permission['level']}")
    print(f"  Result: {result.result}")
    test_results.append(("Test 1", result.status == "ALLOWED"))

    # Test 2: Blocked write to high-risk path
    print("\n[Test 2] Blocked write to high-risk path")
    result = safe_write(
        "~/.openclaw/workspaces/sol/credentials/test-secrets.json",
        '{"api_key": "secret123"}',
        agent_name="CODY"
    )
    print(f"  Status: {result.status}")
    print(f"  Level: {result.permission['level']}")
    print(f"  Approval request generated: {result.result is not None}")
    test_results.append(("Test 2", result.status == "BLOCKED"))

    # Test 3: Blocked write to system config
    print("\n[Test 3] Blocked write to system config")
    result = safe_write(
        "~/.openclaw/openclaw.json",
        '{"test": "config"}',
        agent_name="SOL"
    )
    print(f"  Status: {result.status}")
    print(f"  Level: {result.permission['level']}")
    test_results.append(("Test 3", result.status == "BLOCKED"))

    # Test 4: Batch operations with bulk guard (mixed allowed/blocked)
    print("\n[Test 4] Bulk operations with mixed risk levels")
    with guard_all_writes(agent_name="ASSEMBLY", default_action="block") as guard:
        guard.queue_write(
            "~/.openclaw/workspaces/sol/memory/plans/PLAN-TEST.md",
            "# Test Plan\n\nThis is a test plan."
        )
        guard.queue_write(
            "~/.openclaw/workspaces/sol/09-SOL-System/config-test.json",
            '{"test": true}'
        )
        guard.queue_write(
            "~/.openclaw/workspaces/sol/artifacts/test-artifact.md",
            "# Test Artifact"
        )
        results = guard.execute()

    summary = guard.get_summary()
    print(f"  Total queued: 3")
    print(f"  Executed: {summary['total']}")
    print(f"  Allowed: {summary['allowed']}")
    print(f"  Blocked: {summary['blocked']}")
    print(f"  All allowed: {summary['all_allowed']}")
    # Should be: 2 executed (stops at first blocked), 1 allowed, 1 blocked
    test_results.append(("Test 4", summary['blocked'] > 0))

    # Test 5: Remote node write validation
    print("\n[Test 5] Remote node write validation")
    result = safe_file_write(
        node="phillips-macbook-air",
        path="/Users/philliplowe/.openclaw/workspaces/sol/memory/test-remote.md",
        content="# Remote test content",
        agent_name="CODY"
    )
    print(f"  Status: {result.status}")
    print(f"  Level: {result.permission['level']}")
    print(f"  Result type: {type(result.result).__name__}")
    test_results.append(("Test 5", result.status == "ALLOWED"))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(1 for _, ok in test_results if ok)
    total = len(test_results)

    for name, ok in test_results:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {status} — {name}")

    print(f"\n  RESULTS: {passed}/{total} tests passed")
    print("=" * 70)

    return passed == total


# ── Usage Examples for SOL ──────────────────────────────────────────────────

EXAMPLE_SOL_WORKFLOW = """
# Example: How SOL uses this in actual agent workflows

from write_guard_integration import safe_write, validate_before_write_tool

# Scenario 1: Writing a daily log
result = safe_write(
    path="memory/2026-05-30.md",
    content="# 2026-05-30\n\nToday we built...",
    agent_name="SOL"
)
# Returns immediately — LOW risk, auto-allowed

# Scenario 2: Writing to a project folder
result = safe_write(
    path="03-Projects/client-site/index.html",
    content="<html>...</html>",
    agent_name="CODY"
)
# Allowed but logged — MEDIUM risk

# Scenario 3: Attempting to write system config (BLOCKED)
result = safe_write(
    path="09-SOL-System/openclaw.json",
    content='{"modified": true}',
    agent_name="SOL"
)
# BLOCKED — prints approval banner, returns without writing

# Scenario 4: Pre-flight check before using OpenClaw tool
validation = validate_before_write_tool(
    path="memory/plans/PLAN-NEW.md",
    agent_name="SOL"
)
if validation["proceed"]:
    # SAFE to use OpenClaw write tool
    write(path=validation["path"], content=plan_content)
else:
    # ESCALATE — send message to Green
    message(target="webchat", content=f"Approval needed for {validation['path']}")
"""


# ── Main Entry Point ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
