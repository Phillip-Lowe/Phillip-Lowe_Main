#!/usr/bin/env python3
"""
agent-return-schema.py — Agent Output Schema Validator
Enforces structured metadata on all agent returns before Obsidian storage.

Part of PLAN-HUBSPOKE-001 (P2)
Authorized by Green (KUDU-7 confirmed)
Built by CODY (Technical Architect)

Required Schema:
{
  "source_agent": "string (agent name)",
  "core_fact": "string (primary finding/decision)",
  "action_items": ["array of strings"],
  "plan_id": "string (optional)",
  "confidence": "number 0-1 (optional)",
  "timestamp": "ISO-8601"
}
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# ── Schema Definition ─────────────────────────────────────────────────────────

REQUIRED_FIELDS = ["source_agent", "core_fact", "action_items"]
OPTIONAL_FIELDS = ["plan_id", "confidence", "timestamp"]
VALID_AGENTS = [
    "SOL", "CODY", "VALI", "PESSI", "CHATTY", "GENI", "ASSEMBLY", "ATLAS"
]

def validate_agent_return(data: Any, strict: bool = True) -> Dict:
    """
    Validate an agent return payload against the canonical schema.

    Args:
        data: The payload to validate (dict, JSON string, or raw string)
        strict: If True, reject payloads missing required fields.
                If False, attempt auto-formatting.

    Returns:
        {
            "valid": bool,
            "errors": List[str],
            "data": Dict (the validated/corrected data),
            "formatted_for_obsidian": str (markdown block)
        }
    """
    errors = []
    parsed_data = {}

    # ── Parse input ─────────────────────────────────────────────────────────
    if isinstance(data, str):
        # Try to parse as JSON
        try:
            parsed_data = json.loads(data)
        except json.JSONDecodeError:
            # If strict, reject. If not strict, try to structure raw text.
            if strict:
                errors.append("Payload is not valid JSON and strict mode is enabled.")
                return {
                    "valid": False,
                    "errors": errors,
                    "data": {"raw_text": data},
                    "formatted_for_obsidian": f"\n```\n{data}\n```\n",
                }
            else:
                # Auto-format raw text into schema structure
                parsed_data = {
                    "source_agent": "unknown",
                    "core_fact": data[:200] + ("..." if len(data) > 200 else ""),
                    "action_items": ["Review raw output and structure manually"],
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
    elif isinstance(data, dict):
        parsed_data = data
    else:
        errors.append(f"Unsupported payload type: {type(data).__name__}")
        return {
            "valid": False,
            "errors": errors,
            "data": {},
            "formatted_for_obsidian": str(data),
        }

    # ── Validate required fields ─────────────────────────────────────────────
    for field in REQUIRED_FIELDS:
        if field not in parsed_data or not parsed_data[field]:
            errors.append(f"Missing or empty required field: '{field}'")

    # ── Validate field types ─────────────────────────────────────────────────
    if "source_agent" in parsed_data:
        agent = parsed_data["source_agent"]
        if not isinstance(agent, str):
            errors.append(f"'source_agent' must be a string, got {type(agent).__name__}")
        # Allow unknown agents in lenient mode, but warn
        elif agent.upper() not in [a.upper() for a in VALID_AGENTS] and agent != "unknown":
            errors.append(f"Unknown agent '{agent}'. Valid agents: {', '.join(VALID_AGENTS)}")

    if "core_fact" in parsed_data:
        fact = parsed_data["core_fact"]
        if not isinstance(fact, str):
            errors.append(f"'core_fact' must be a string, got {type(fact).__name__}")
        elif len(fact) < 10:
            errors.append("'core_fact' must be at least 10 characters.")

    if "action_items" in parsed_data:
        items = parsed_data["action_items"]
        if not isinstance(items, list):
            errors.append(f"'action_items' must be an array, got {type(items).__name__}")
        else:
            for i, item in enumerate(items):
                if not isinstance(item, str):
                    errors.append(f"'action_items[{i}]' must be a string, got {type(item).__name__}")

    # ── Validate optional fields ────────────────────────────────────────────
    if "confidence" in parsed_data:
        conf = parsed_data["confidence"]
        if not isinstance(conf, (int, float)):
            errors.append(f"'confidence' must be a number, got {type(conf).__name__}")
        elif not (0 <= conf <= 1):
            errors.append(f"'confidence' must be between 0 and 1, got {conf}")

    if "timestamp" in parsed_data:
        ts = parsed_data["timestamp"]
        if not isinstance(ts, str):
            errors.append(f"'timestamp' must be a string, got {type(ts).__name__}")
    else:
        # Auto-add timestamp if missing
        parsed_data["timestamp"] = datetime.utcnow().isoformat() + "Z"

    # ── Build formatted markdown for Obsidian ────────────────────────────────
    formatted = format_for_obsidian(parsed_data)

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "data": parsed_data,
        "formatted_for_obsidian": formatted,
    }

def format_for_obsidian(data: Dict) -> str:
    """
    Convert validated agent return data into a structured markdown block
    suitable for Obsidian Dataview indexing.
    """
    lines = [
        "---",
        f"source_agent: {data.get('source_agent', 'unknown')}",
        f"plan_id: {data.get('plan_id', 'none')}",
        f"confidence: {data.get('confidence', 'none')}",
        f"timestamp: {data.get('timestamp', 'none')}",
        "---",
        "",
        f"## Core Fact",
        "",
        data.get("core_fact", "No core fact provided."),
        "",
        "## Action Items",
        "",
    ]

    items = data.get("action_items", [])
    if items:
        for item in items:
            lines.append(f"- [ ] {item}")
    else:
        lines.append("- No action items specified.")

    lines.append("")
    return "\n".join(lines)

def retry_format(raw_input: str, max_attempts: int = 3) -> Dict:
    """
    Attempt to auto-format a raw text input into the schema.
    Uses progressive strategies:
    1. Try strict JSON parse
    2. Try lenient JSON parse
    3. Structure raw text with best-effort extraction
    """
    attempt = 1
    last_result = None

    while attempt <= max_attempts:
        if attempt == 1:
            # Strict validation
            result = validate_agent_return(raw_input, strict=True)
        elif attempt == 2:
            # Lenient: allow auto-formatting of non-JSON
            result = validate_agent_return(raw_input, strict=False)
        else:
            # Final fallback: force structure
            forced = {
                "source_agent": "unknown",
                "core_fact": f"[AUTO-FORMATTED] {raw_input[:300]}",
                "action_items": ["Manual review required: original input could not be fully structured"],
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            result = validate_agent_return(forced, strict=True)

        if result["valid"]:
            result["retry_attempts"] = attempt
            return result

        last_result = result
        attempt += 1

    # All retries failed
    last_result["retry_attempts"] = max_attempts
    last_result["retry_exhausted"] = True
    return last_result

# ── Integration Hook ───────────────────────────────────────────────────────────

def on_agent_complete(agent_name: str, raw_output: Any, plan_id: str = "") -> Dict:
    """
    Hook to call when an agent completes a task.
    Validates the output, formats for Obsidian, and returns the result.

    Usage:
        result = on_agent_complete("CODY", agent_output, plan_id="PLAN-123")
        if result["valid"]:
            # Write result["formatted_for_obsidian"] to Obsidian
            pass
        else:
            # Log errors, notify SOL, trigger retry
            pass
    """
    # If raw_output is already a dict, use it directly
    if isinstance(raw_output, dict):
        payload = raw_output
    else:
        # Try to parse or auto-format
        payload = raw_output

    result = retry_format(payload if isinstance(payload, str) else json.dumps(payload))

    # Inject plan_id if provided and missing
    if plan_id and not result["data"].get("plan_id"):
        result["data"]["plan_id"] = plan_id
        # Re-format
        result["formatted_for_obsidian"] = format_for_obsidian(result["data"])

    # Log the completion
    print(f"[AGENT-COMPLETE] {agent_name} | Valid: {result['valid']} | Errors: {len(result['errors'])}", file=sys.stderr)
    if result["errors"]:
        for err in result["errors"]:
            print(f"  [ERROR] {err}", file=sys.stderr)

    return result

# ── Test / Validation Block ─────────────────────────────────────────────────

def run_tests():
    """
    Validate the schema validator with test payloads.
    """
    print("=" * 60)
    print("AGENT RETURN SCHEMA — VALIDATION TESTS")
    print("=" * 60)

    test_cases = [
        # (description, payload, strict, expected_valid)
        (
            "Valid complete payload",
            {
                "source_agent": "CODY",
                "core_fact": "Built the write guard utility successfully with path-based authorization.",
                "action_items": ["Test write guard", "Integrate into SOL workflow"],
                "plan_id": "PLAN-HUBSPOKE-001",
                "confidence": 0.95,
                "timestamp": "2026-05-30T04:20:00Z",
            },
            True,
            True,
        ),
        (
            "Missing source_agent",
            {
                "core_fact": "Something happened.",
                "action_items": ["Do something"],
            },
            True,
            False,
        ),
        (
            "Invalid confidence (out of range)",
            {
                "source_agent": "VALI",
                "core_fact": "Validation passed all checks.",
                "action_items": ["Sign off"],
                "confidence": 1.5,
            },
            True,
            False,
        ),
        (
            "Auto-format raw text (lenient)",
            "The agent completed the task successfully but returned plain text.",
            False,
            True,
        ),
        (
            "Unknown agent name",
            {
                "source_agent": "HACKER",
                "core_fact": "Malicious payload.",
                "action_items": ["Ignore this"],
            },
            True,
            False,
        ),
        (
            "Missing core_fact (too short)",
            {
                "source_agent": "CHATTY",
                "core_fact": "Hi.",
                "action_items": ["Say hello"],
            },
            True,
            False,
        ),
    ]

    passed = 0
    failed = 0

    for desc, payload, strict, expected_valid in test_cases:
        result = validate_agent_return(payload, strict=strict)
        status = "PASS" if result["valid"] == expected_valid else "FAIL"

        if status == "PASS":
            passed += 1
        else:
            failed += 1

        print(f"\n  [{status}] {desc}")
        print(f"        Expected valid: {expected_valid}")
        print(f"        Actual valid:   {result['valid']}")
        if result["errors"]:
            for err in result["errors"]:
                print(f"        Error: {err}")

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 60)

    # Show formatted output example
    print("\n--- Example Formatted Output ---\n")
    example = validate_agent_return({
        "source_agent": "CODY",
        "core_fact": "Built write guard and schema validator.",
        "action_items": ["Integrate into SOL", "Document in MEMORY.md"],
        "plan_id": "PLAN-HUBSPOKE-001",
        "confidence": 0.98,
    })
    print(example["formatted_for_obsidian"])

    if failed > 0:
        print("\n[ERROR] Validation failed. Do not deploy.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All tests passed. Schema validator is validated.")
        return True

# ── Main Entry Point ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_tests()
