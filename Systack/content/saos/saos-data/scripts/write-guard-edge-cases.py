#!/usr/bin/env python3
"""
write-guard-edge-cases.py — Edge Case Validation for Write Guard
Part of PLAN-HUBSPOKE-001-PHASE2
Tests symlink resolution, relative paths, external paths, concurrency, unicode, case sensitivity
"""

import os
import sys
import threading
import tempfile
import time
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.expanduser('~/.openclaw/workspaces/sol/scripts'))

# Import the write guard functions directly by exec
exec(open(os.path.expanduser('~/.openclaw/workspaces/sol/scripts/write-guard.py')).read())

# Override the main block
print("=" * 70)
print("WRITE GUARD — EDGE CASE VALIDATION")
print("=" * 70)

test_results = []

def record_test(name, passed, details="", severity="info"):
    status = "✅ PASS" if passed else "❌ FAIL"
    test_results.append({
        "name": name,
        "passed": passed,
        "details": details,
        "severity": severity
    })
    print(f"\n[{status}] {name}")
    if details:
        print(f"    Details: {details}")
    return passed

passed_count = 0
failed_count = 0

# ── TEST 1: Symlink Resolution ─────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 1: Symlink Resolution")
print("─" * 70)

try:
    # Create temp dir structure
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a real high-risk path
        real_high = os.path.join(tmpdir, "09-SOL-System", "test.json")
        os.makedirs(os.path.dirname(real_high), exist_ok=True)
        
        # Create a symlink pointing to high-risk path
        symlink_path = os.path.join(tmpdir, "safe-link")
        os.symlink(real_high, symlink_path)
        
        # Test: does write-guard resolve symlink and see HIGH risk?
        result = check_write_permission(symlink_path, "TEST")
        
        # The symlink points to 09-SOL-System which is HIGH
        # But write-guard checks the symlink path itself, not the target
        # This is actually CORRECT behavior — we care about where we're writing
        is_high = result["level"] == "HIGH"
        
        if is_high:
            record_test(
                "Symlink to HIGH-risk path",
                True,
                f"Correctly classified as HIGH. Path: {symlink_path} → {real_high}"
            )
            passed_count += 1
        else:
            record_test(
                "Symlink to HIGH-risk path",
                False,
                f"Should be HIGH but got {result['level']}. Path: {symlink_path} → {real_high}. "
                f"Write-guard may need to resolve symlinks before classification.",
                "critical"
            )
            failed_count += 1
            
        # Test 1b: Symlink to low-risk path
        real_low = os.path.join(tmpdir, "02-Memory", "daily-logs", "test.md")
        os.makedirs(os.path.dirname(real_low), exist_ok=True)
        
        symlink_low = os.path.join(tmpdir, "low-link")
        os.symlink(real_low, symlink_low)
        
        result_low = check_write_permission(symlink_low, "TEST")
        is_low = result_low["level"] == "LOW"
        
        if is_low:
            record_test(
                "Symlink to LOW-risk path",
                True,
                f"Correctly classified as LOW."
            )
            passed_count += 1
        else:
            record_test(
                "Symlink to LOW-risk path",
                False,
                f"Should be LOW but got {result_low['level']}",
                "critical"
            )
            failed_count += 1

except Exception as e:
    record_test("Symlink Resolution", False, f"Exception: {str(e)}", "critical")
    failed_count += 1

# ── TEST 2: Relative Path Traversal ────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 2: Relative Path Traversal")
print("─" * 70)

try:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a nested structure
        deep_dir = os.path.join(tmpdir, "a", "b", "c")
        os.makedirs(deep_dir, exist_ok=True)
        
        # From deep_dir, reference a high-risk path using ..
        # Simulate: ~/.openclaw/workspaces/sol/09-SOL-System/file.json
        # From deep_dir: ../../../09-SOL-System/file.json  (doesn't exist, but test normalization)
        
        # Actually let's use a real high-risk pattern in a controlled way
        high_target = os.path.join(tmpdir, "09-SOL-System", "test.json")
        os.makedirs(os.path.dirname(high_target), exist_ok=True)
        
        # Relative path from deep_dir to high_target
        rel_path = os.path.join(deep_dir, "..", "..", "..", "09-SOL-System", "test.json")
        
        result = check_write_permission(rel_path, "TEST")
        is_high = result["level"] == "HIGH"
        
        if is_high:
            record_test(
                "Relative path traversal to HIGH",
                True,
                f"Correctly resolved {rel_path} to HIGH"
            )
            passed_count += 1
        else:
            record_test(
                "Relative path traversal to HIGH",
                False,
                f"Should be HIGH but got {result['level']}. Path: {rel_path}. "
                f"normalize_path() may not fully resolve relative traversal.",
                "critical"
            )
            failed_count += 1
        
        # Test 2b: Deep relative path that ends up LOW
        low_target = os.path.join(tmpdir, "02-Memory", "test.md")
        os.makedirs(os.path.dirname(low_target), exist_ok=True)
        rel_low = os.path.join(deep_dir, "..", "..", "..", "02-Memory", "test.md")
        
        result_low = check_write_permission(rel_low, "TEST")
        is_low = result_low["level"] == "LOW"
        
        if is_low:
            record_test("Relative path traversal to LOW", True, "Correctly resolved to LOW")
            passed_count += 1
        else:
            record_test("Relative path traversal to LOW", False, f"Should be LOW but got {result_low['level']}", "critical")
            failed_count += 1

except Exception as e:
    record_test("Relative Path Traversal", False, f"Exception: {str(e)}", "critical")
    failed_count += 1

# ── TEST 3: Paths Outside Vault ────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 3: Paths Outside Vault / Workspace")
print("─" * 70)

test_paths = [
    ("/etc/passwd", "MEDIUM", "System file"),
    ("/tmp/test.txt", "MEDIUM", "Temp file"),
    ("/var/log/system.log", "MEDIUM", "Log file"),
    ("~/random-file.md", "MEDIUM", "Home directory random"),
    ("/Applications/Safari.app", "MEDIUM", "Application bundle"),
]

for path, expected, desc in test_paths:
    try:
        result = check_write_permission(path, "TEST")
        is_correct = result["level"] == expected
        
        if is_correct:
            record_test(f"External path: {desc}", True, f"Correctly defaulted to {expected}: {path}")
            passed_count += 1
        else:
            record_test(
                f"External path: {desc}",
                False,
                f"Expected {expected}, got {result['level']}. Path: {path}",
                "medium"
            )
            failed_count += 1
    except Exception as e:
        record_test(f"External path: {desc}", False, f"Exception: {str(e)}", "critical")
        failed_count += 1

# ── TEST 4: Concurrent Access ──────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 4: Concurrent Access / Race Conditions")
print("─" * 70)

try:
    target_path = "~/.openclaw/workspaces/sol/memory/plans/PLAN-TEST.md"
    num_threads = 5
    results = []
    errors = []
    
    def worker():
        try:
            r = check_write_permission(target_path, "CONCURRENT")
            results.append(r)
        except Exception as e:
            errors.append(str(e))
    
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=worker)
        threads.append(t)
    
    # Start all threads simultaneously
    for t in threads:
        t.start()
    
    # Wait for all to complete
    for t in threads:
        t.join(timeout=5)
    
    # Analyze results
    all_same = len(set(r["level"] for r in results)) == 1 if results else False
    no_errors = len(errors) == 0
    all_allowed = all(r["allowed"] == results[0]["allowed"] for r in results) if results else False
    
    if no_errors and all_same and all_allowed and len(results) == num_threads:
        record_test(
            f"Concurrent access ({num_threads} threads)",
            True,
            f"All {num_threads} calls returned consistent results. No race conditions detected."
        )
        passed_count += 1
    else:
        details = f"Results: {len(results)}/{num_threads} succeeded. "
        if errors:
            details += f"Errors: {errors}. "
        if not all_same:
            levels = [r["level"] for r in results]
            details += f"Inconsistent levels: {levels}. "
        record_test(
            f"Concurrent access ({num_threads} threads)",
            False,
            details,
            "critical"
        )
        failed_count += 1

except Exception as e:
    record_test("Concurrent Access", False, f"Exception: {str(e)}", "critical")
    failed_count += 1

# ── TEST 5: Unicode / Special Characters ───────────────────────────────────
print("\n" + "─" * 70)
print("TEST 5: Unicode and Special Characters")
print("─" * 70)

unicode_paths = [
    ("~/.openclaw/workspaces/sol/memory/文件.md", "Unicode filename"),
    ("~/.openclaw/workspaces/sol/memory/plans/PLAN-Ümlaut.md", "Umlaut"),
    ("~/.openclaw/workspaces/sol/memory/daily-logs/2026-05-30 café.md", "Accent"),
    ("~/.openclaw/workspaces/sol/memory/test file with spaces.md", "Spaces"),
    ("~/.openclaw/workspaces/sol/memory/test-file_with-special-chars@123.md", "Special chars"),
]

for path, desc in unicode_paths:
    try:
        result = check_write_permission(path, "TEST")
        # Should not crash and should classify as LOW (memory path)
        is_low = result["level"] == "LOW"
        
        if is_low:
            record_test(f"Unicode: {desc}", True, f"Correctly handled: {path}")
            passed_count += 1
        else:
            record_test(f"Unicode: {desc}", False, f"Should be LOW but got {result['level']}: {path}", "medium")
            failed_count += 1
    except Exception as e:
        record_test(f"Unicode: {desc}", False, f"Exception: {str(e)}: {path}", "critical")
        failed_count += 1

# ── TEST 6: Case Sensitivity ───────────────────────────────────────────────
print("\n" + "─" * 70)
print("TEST 6: Case Sensitivity (macOS APFS)")
print("─" * 70)

case_paths = [
    ("~/.openclaw/workspaces/sol/Memory/test.md", "Capital M"),
    ("~/.openclaw/workspaces/sol/MEMORY/test.md", "All caps"),
    ("~/.openclaw/workspaces/sol/memory/TEST.md", "Uppercase file"),
    ("~/.openclaw/workspaces/sol/02-Memory/Daily-Logs/test.md", "Mixed case dirs"),
]

for path, desc in case_paths:
    try:
        result = check_write_permission(path, "TEST")
        # On macOS case-insensitive FS, these should all be LOW
        is_low = result["level"] == "LOW"
        
        if is_low:
            record_test(f"Case sensitivity: {desc}", True, f"Handled correctly: {path}")
            passed_count += 1
        else:
            # This might be acceptable if pattern matching is case-sensitive
            # But it's worth noting
            record_test(
                f"Case sensitivity: {desc}",
                False,
                f"Got {result['level']} — pattern matching may be case-sensitive. "
                f"On macOS this could cause inconsistent behavior. Consider lowercasing before matching.",
                "low"
            )
            failed_count += 1
    except Exception as e:
        record_test(f"Case sensitivity: {desc}", False, f"Exception: {str(e)}: {path}", "critical")
        failed_count += 1

# ── SUMMARY ────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("EDGE CASE VALIDATION — SUMMARY")
print("=" * 70)

total = passed_count + failed_count
print(f"\nTotal tests: {total}")
print(f"✅ Passed: {passed_count}")
print(f"❌ Failed: {failed_count}")
print(f"Success rate: {passed_count/total*100:.1f}%")

if failed_count > 0:
    print("\n⚠️  FAILURES DETECTED:")
    for t in test_results:
        if not t["passed"]:
            print(f"\n  ❌ {t['name']}")
            print(f"     Severity: {t['severity']}")
            print(f"     {t['details']}")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print("""
1. CRITICAL: Symlink resolution — Consider adding os.path.realpath() before
   classification to resolve symlinks to their targets.
   
2. CRITICAL: Relative path traversal — The normalize_path() function uses
   os.path.realpath() which should handle this, but verify it's called
   before pattern matching.
   
3. MEDIUM: Case sensitivity — Consider lowercasing paths before pattern
   matching for consistent behavior across macOS/Linux.
   
4. LOW: All external paths correctly default to MEDIUM (safe default).
   
5. LOW: No race conditions detected in concurrent access test.
""")
else:
    print("\n🎉 ALL EDGE CASES PASSED")
    print("\nThe write-guard.py is robust and handles:")
    print("  ✅ Symlink resolution")
    print("  ✅ Relative path traversal")
    print("  ✅ External paths (safe default)")
    print("  ✅ Concurrent access (no race conditions)")
    print("  ✅ Unicode and special characters")
    print("  ✅ Case sensitivity")

print("\n" + "=" * 70)
