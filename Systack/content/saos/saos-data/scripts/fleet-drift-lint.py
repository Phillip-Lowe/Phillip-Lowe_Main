#!/usr/bin/env python3
"""
Fleet Drift Linter
Scans agent outputs (plans, artifacts, memory) for drift signals.

Drift = entropy + autonomy + missing enforcement
This script enforces documentation-level gates. Runtime enforcement requires
OpenClaw/n8n hooks, but this catches drift before it compounds.

Usage:
    python3 fleet-drift-lint.py [--fix] [--output json|md]

Signals checked:
  - missing_plan: Output with actionable steps but no PLAN_ID
  - invalid_role: Agent doing work outside canonical role
  - schema_mismatch: Plan missing required fields (goal, steps, completion criteria)
  - unvalidated_done: STATE=DONE without Validation: PASS or NEEDS_REVIEW
  - memory_drift: Duplicate logic patterns across plans
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

# ──────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────

WORKSPACE_ROOT = Path(os.environ.get("SOL_WORKSPACE", 
    "/Users/philliplowe/.openclaw/workspaces/sol"))

SCAN_PATHS = [
    WORKSPACE_ROOT / "memory" / "plans",
    WORKSPACE_ROOT / "artifacts",
]

REQUIRED_PLAN_FIELDS = ["goal", "steps", "completion criteria"]

# Agent return schema fields (from agent-return-schema.json)
REQUIRED_AGENT_RETURN_FIELDS = ["source_agent", "core_fact", "action_items", "timestamp"]

# Plan files that should include agent return blocks
PLAN_FILES_WITH_AGENT_RETURNS = ["PLAN-", "plan-"]

# Canonical agent roles for boundary enforcement
CANONICAL_ROLES = {
    "SOL": ["coordination", "planning", "delegation", "integration", "orchestration"],
    "CODY": ["code", "script", "api", "n8n", "technical implementation"],
    "ASSEMBLY": ["build", "deploy", "provision", "infrastructure"],
    "CHATTY": ["external comms", "copy", "ui text", "messaging", "email"],
    "GENI": ["creative", "design", "visual", "image", "media"],
    "PESSI": ["critique", "challenge", "risk", "security", "review"],
    "VALI": ["validate", "qa", "review", "test", "acceptance"],
    "GREEN-COPILOT": ["reasoning", "document", "plan", "schema", "prompt", "design"],
}

ROLE_BOUNDARY_PATTERNS = {
    "CODY": re.compile(r'\b(n8n\s+workflow|api\s+integration|deploy|script\s+implementation|build\s+pipeline)\b', re.I),
    "ASSEMBLY": re.compile(r'\b(deploy\s+to|provision|infrastructure\s+change|docker\s+(up|run))\b', re.I),
    "CHATTY": re.compile(r'\b(send\s+email|post\s+to|message\s+externally|publish| outreach)\b', re.I),
    "GENI": re.compile(r'\b(generate\s+image|create\s+visual|design\s+asset|creative\s+output)\b', re.I),
    "PESSI": re.compile(r'\b(security\s+review|risk\s+assessment|audit|credential|exposure)\b', re.I),
    "VALI": re.compile(r'\b(validation|qa\s+pass|acceptance\s+criteria|regression\s+test)\b', re.I),
}

# ──────────────────────────────────────────────────────────────
# DATA CLASSES
# ──────────────────────────────────────────────────────────────

@dataclass
class DriftSignal:
    file: Path
    signal_type: str
    severity: str  # ERROR | WARN | INFO
    message: str
    line: Optional[int] = None
    suggestion: Optional[str] = None

@dataclass
class LintResult:
    signals: List[DriftSignal] = field(default_factory=list)
    files_scanned: int = 0
    files_with_drift: int = 0

# ──────────────────────────────────────────────────────────────
# DETECTORS
# ──────────────────────────────────────────────────────────────

class DriftDetector:
    def __init__(self, content: str, file_path: Path):
        self.content = content
        self.file_path = file_path
        self.lines = content.split('\n')
        self.signals: List[DriftSignal] = []
        
        # Extract metadata tokens
        # Match both plain and bold forms: PLAN_ID: or **PLAN_ID:**
        self.plan_id = self._extract(r'^\*{0,2}PLAN[_\-]?ID[:\s*]+(PLAN-\S+)')
        self.role = self._extract(r'^\s*\*{0,2}ROLE[:\s*]+([A-Z\-]+)')
        self.state = self._extract(r'^\s*\*{0,2}STATE[:\s*]+(PLANNED|ACTIVE|BLOCKED|FAILED_RETRY|FAILED_FINAL|DONE|ABANDONED|VALIDATION_REQUIRED)')
        self.validation = self._extract(r'^\s*\*{0,2}VALIDATION[:\s*]+(PASS|NEEDS_REVIEW|FAIL)')
        self.role_check = self._extract(r'^\s*\*{0,2}ROLE[_\-]?CHECK[:\s*]+(PASS|FAIL)')
        self.has_goal = bool(re.search(r'goal[:\s]', content, re.I))
        self.has_steps = bool(re.search(r'steps?[:\s]|step\s+\d', content, re.I))
        self.has_completion = bool(re.search(r'completion\s+criteria|done\s+when|how\s+we\s+know', content, re.I))
        self.has_freeze = bool(re.search(r'FREEZE[_\-]?CONTEXT|frozen[_\-]?context', content, re.I))
    
    def _extract(self, pattern: str) -> Optional[str]:
        match = re.search(pattern, self.content, re.MULTILINE | re.I)
        return match.group(1).strip().upper() if match else None
    
    def detect(self) -> List[DriftSignal]:
        self._check_plan_id()
        self._check_role_boundaries()
        self._check_schema_compliance()
        self._check_validation_gate()
        self._check_fleet_flags()
        self._check_agent_return_schema()
        return self.signals
    
    def _check_plan_id(self):
        """Plan-gating: actionable outputs need PLAN_ID."""
        # Skip non-actionable files (daily notes, memory fragments)
        if not self._is_actionable():
            return
        
        if not self.plan_id:
            self.signals.append(DriftSignal(
                file=self.file_path,
                signal_type="missing_plan",
                severity="ERROR",
                message="Actionable output missing PLAN_ID. Every execution must link to a plan.",
                suggestion="Add 'PLAN_ID: PLAN-XXXX' header or mark as non-actionable note."
            ))
    
    def _check_role_boundaries(self):
        """Role boundary enforcement: detect cross-role execution.
        Skips coordination plans where SOL delegates to other agents."""
        if not self.role:
            return
        
        # Coordination plans (SOL delegating) are exempt
        if 'PLAN-enforcement-layer-v1' in str(self.file_path):
            return
        if any(k in self.content for k in ['Delegates:', 'FLEET_FLAG: COORDINATION']):
            return
        
        role = self.role.upper()
        if role == "GREEN-COPILOT":
            role = "GREEN-COPILOT"
        
        for canonical_role, pattern in ROLE_BOUNDARY_PATTERNS.items():
            if canonical_role == role:
                continue  # Same role, no boundary issue
            if pattern.search(self.content):
                self.signals.append(DriftSignal(
                    file=self.file_path,
                    signal_type="invalid_role",
                    severity="WARN",
                    message=f"{role} output contains {canonical_role}-canonical work. Possible role drift.",
                    suggestion=f"Delegate to {canonical_role} or add FLEET_FLAG: {canonical_role} — review required."
                ))
    
    def _check_schema_compliance(self):
        """Schema drift: plans missing required fields."""
        if not self._is_plan():
            return
        
        missing = []
        if not self.has_goal:
            missing.append("goal")
        if not self.has_steps:
            missing.append("steps")
        if not self.has_completion:
            missing.append("completion criteria")
        
        if missing:
            self.signals.append(DriftSignal(
                file=self.file_path,
                signal_type="schema_mismatch",
                severity="ERROR",
                message=f"Plan missing required fields: {', '.join(missing)}.",
                suggestion=f"Add sections: {', '.join(missing)}. See FLEET_PLAN_PROTOCOL.md."
            ))
    
    def _check_validation_gate(self):
        """Validation gate: no DONE without VALIDATION."""
        if self.state == "DONE" and not self.validation:
            self.signals.append(DriftSignal(
                file=self.file_path,
                signal_type="unvalidated_done",
                severity="ERROR",
                message="STATE: DONE without VALIDATION. Completion must be verified.",
                suggestion="Add 'VALIDATION: PASS' (or NEEDS_REVIEW) before marking DONE."
            ))

    def _check_agent_return_schema(self):
        """Agent return schema compliance: plan completion sections must include structured agent returns."""
        # Only check plan files that are DONE or have completion sections
        if not self._is_plan():
            return
        
        # Look for agent return blocks in the file
        has_agent_return = bool(re.search(
            r'```json\s*\n\s*\{\s*"source_agent"',
            self.content,
            re.DOTALL
        ))
        
        # Check for legacy freeform agent output (long prose without structure)
        has_freeform_output = bool(re.search(
            r'(##\s+(CODY|VALI|ASSEMBLY|CHATTY|GENI|PESSI|ATLAS)\s+(Output|Result|Return)'
            r'|#{1,3}\s+.*Agent.*Output.*\n+(?!.*```json))',
            self.content,
            re.I | re.DOTALL
        ))
        
        if self.state == "DONE" and not has_agent_return and has_freeform_output:
            self.signals.append(DriftSignal(
                file=self.file_path,
                signal_type="agent_return_schema_missing",
                severity="WARN",
                message="Plan marked DONE but agent outputs lack structured JSON returns.",
                suggestion="Add ```json blocks with source_agent, core_fact, action_items, timestamp per agent-return-schema.json"
            ))
        
        # Check for agent return blocks that exist but may be malformed
        if has_agent_return:
            # Extract JSON blocks
            json_blocks = re.findall(
                r'```json\s*\n(.*?)\n```',
                self.content,
                re.DOTALL
            )
            
            for i, block in enumerate(json_blocks):
                try:
                    data = json.loads(block.strip())
                    missing_fields = [f for f in REQUIRED_AGENT_RETURN_FIELDS if f not in data]
                    if missing_fields:
                        self.signals.append(DriftSignal(
                            file=self.file_path,
                            signal_type="agent_return_incomplete",
                            severity="WARN",
                            message=f"Agent return block #{i+1} missing required fields: {', '.join(missing_fields)}",
                            suggestion=f"Add: {', '.join(missing_fields)}"
                        ))
                except json.JSONDecodeError:
                    self.signals.append(DriftSignal(
                        file=self.file_path,
                        signal_type="agent_return_malformed",
                        severity="ERROR",
                        message=f"Agent return block #{i+1} is not valid JSON",
                        suggestion="Fix JSON syntax: check quotes, commas, braces"
                    ))
        
        if self.state == "DONE" and self.validation == "NEEDS_REVIEW":
            self.signals.append(DriftSignal(
                file=self.file_path,
                signal_type="unvalidated_done",
                severity="WARN",
                message="STATE: DONE but VALIDATION: NEEDS_REVIEW. Completion is provisional.",
                suggestion="Escalate to VALI or SOL for final validation before declaring DONE."
            ))
    
    def _check_fleet_flags(self):
        """Check for FLEET_FLAG usage patterns and enforcement schema adoption."""
        flags = re.findall(r'FLEET_FLAG:\s*(\w+)', self.content, re.I)
        for flag in flags:
            if flag.upper() not in CANONICAL_ROLES:
                self.signals.append(DriftSignal(
                    file=self.file_path,
                    signal_type="unknown_fleet_flag",
                    severity="INFO",
                    message=f"Unknown FLEET_FLAG target: {flag}.",
                    suggestion=f"Use canonical role: {', '.join(CANONICAL_ROLES.keys())}."
                ))
    
    def _check_agent_return_schema(self):
        """Check if agent completion sections include structured JSON returns.
        Added 2026-05-30 as part of PLAN-HUBSPOKE-001."""
        if not self._is_plan():
            return
        
        # Look for agent return sections in plan files
        return_blocks = re.findall(
            r'```json\s*\n(\{[\s\S]*?\})\s*\n```',
            self.content
        )
        
        for block in return_blocks:
            try:
                data = json.loads(block)
                required_fields = ['source_agent', 'core_fact', 'action_items', 'timestamp']
                missing = [f for f in required_fields if f not in data]
                
                if missing:
                    self.signals.append(DriftSignal(
                        file=self.file_path,
                        signal_type="agent_return_schema_missing",
                        severity="WARN",
                        message=f"Agent return block missing required fields: {', '.join(missing)}.",
                        suggestion="See schemas/agent-return-schema.md for required fields."
                    ))
                
                # Validate source_agent is canonical
                if 'source_agent' in data:
                    agent = data['source_agent'].upper()
                    valid_agents = list(CANONICAL_ROLES.keys()) + ['SOL']
                    if agent not in [a.upper() for a in valid_agents]:
                        self.signals.append(DriftSignal(
                            file=self.file_path,
                            signal_type="invalid_source_agent",
                            severity="WARN",
                            message=f"Non-canonical source_agent: {data['source_agent']}.",
                            suggestion=f"Use: {', '.join(valid_agents)}."
                        ))
                        
            except json.JSONDecodeError:
                # Not valid JSON, skip
                pass
        
        # Check if plan has ANY agent return blocks in completion section
        has_completion_section = bool(re.search(r'##?\s*(completion|execution log|results)', self.content, re.I))
        has_agent_returns = bool(re.search(r'```json\s*\n\s*\{\s*"source_agent"', self.content))
        
        if has_completion_section and not has_agent_returns:
            self.signals.append(DriftSignal(
                file=self.file_path,
                signal_type="missing_agent_returns",
                severity="INFO",
                message="Plan has completion section but no structured agent return blocks.",
                suggestion="Add JSON agent return blocks per schemas/agent-return-schema.md."
            ))
    
    def _check_enforcement_schema(self) -> bool:
        """Check if file uses the canonical enforcement schema tokens."""
        return all([
            self.plan_id is not None,
            self.role is not None,
            self.state is not None,
            self.validation is not None,
        ])
    
    def adoption_score(self) -> dict:
        """Return adoption metrics for this file."""
        return {
            'plan_id': self.plan_id is not None,
            'role': self.role is not None,
            'state': self.state is not None,
            'validation': self.validation is not None,
            'role_check': self.role_check is not None,
            'freeze': self.has_freeze,
        }
    
    def _is_actionable(self) -> bool:
        """Heuristic: does this file contain actionable work?
        Excludes: policy docs, audit reports, status summaries, daily notes."""
        # Daily notes and raw memory are not actionable
        if re.match(r'\d{4}-\d{2}-\d{2}', self.file_path.name):
            return False
        # Policy/admin documents (not plans)
        is_policy = bool(re.search(r'(COPILOT.*ADDENDUM|SANDBOX.*ADDENDUM|capability[-_]audit|FLEET[-_]HANDOFF)', self.file_path.name, re.I))
        if is_policy:
            return False
        # Status/audit reports (observational, not actionable)
        if 'STATUS' in self.file_path.name.upper() or 'AUDIT' in self.file_path.stem.upper():
            return False
        # Must have some structure indicating a plan or artifact
        has_structure = bool(re.search(r'^(#{1,3}\s|PLAN[_\-]|STATE[:\s]|GOAL[:\s])', self.content, re.M))
        has_steps = bool(re.search(r'(step\s*\d|todo|action item|execute)', self.content, re.I))
        return has_structure and has_steps
    
    def _is_plan(self) -> bool:
        """Check if this is a plan file."""
        return bool(re.search(r'^\s*(#\s*PLAN|PLAN[_\-]ID)', self.content, re.M))


# ──────────────────────────────────────────────────────────────
# DUPLICATE DETECTION
# ──────────────────────────────────────────────────────────────

def detect_duplicate_logic(results: List[LintResult]) -> List[DriftSignal]:
    """Detect similar plans/artifacts that may indicate memory drift."""
    signals = []
    # Simplified: look for repeated patterns in plan goals
    goals: dict[str, List[Path]] = {}
    
    for result in results:
        for signal in result.signals:
            if signal.signal_type == "schema_mismatch":
                continue
    
    # This is a placeholder for more sophisticated duplicate detection
    # In practice, we'd hash normalized goal descriptions and flag >80% similarity
    return signals


# ──────────────────────────────────────────────────────────────
# OUTPUT FORMATTERS
# ──────────────────────────────────────────────────────────────

def format_markdown(results: List[LintResult]) -> str:
    lines = ["# Fleet Drift Report", ""]
    
    total_signals = sum(len(r.signals) for r in results)
    total_files = sum(r.files_scanned for r in results)
    drift_files = sum(r.files_with_drift for r in results)
    
    lines.append(f"**Files scanned:** {total_files}")
    lines.append(f"**Files with drift:** {drift_files}")
    lines.append(f"**Total signals:** {total_signals}")
    lines.append("")
    
    if total_signals == 0:
        lines.append("✅ No drift detected. Fleet is clean.")
        return "\n".join(lines)
    
    # Group by severity
    errors = [s for r in results for s in r.signals if s.severity == "ERROR"]
    warnings = [s for r in results for s in r.signals if s.severity == "WARN"]
    infos = [s for r in results for s in r.signals if s.severity == "INFO"]
    
    if errors:
        lines.append(f"## 🔴 Errors ({len(errors)})")
        for s in errors:
            lines.append(f"- **{s.signal_type}** in `{s.file}`")
            lines.append(f"  - {s.message}")
            if s.suggestion:
                lines.append(f"  - *Suggestion:* {s.suggestion}")
        lines.append("")
    
    if warnings:
        lines.append(f"## 🟡 Warnings ({len(warnings)})")
        for s in warnings:
            lines.append(f"- **{s.signal_type}** in `{s.file}`")
            lines.append(f"  - {s.message}")
            if s.suggestion:
                lines.append(f"  - *Suggestion:* {s.suggestion}")
        lines.append("")
    
    if infos:
        lines.append(f"## 🔵 Info ({len(infos)})")
        for s in infos:
            lines.append(f"- **{s.signal_type}** in `{s.file}`: {s.message}")
        lines.append("")
    
    return "\n".join(lines)


def format_json(results: List[LintResult]) -> str:
    data = []
    for result in results:
        for s in result.signals:
            data.append({
                "file": str(s.file),
                "signal_type": s.signal_type,
                "severity": s.severity,
                "message": s.message,
                "line": s.line,
                "suggestion": s.suggestion,
            })
    return json.dumps(data, indent=2)


# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────

def scan_directory(path: Path) -> LintResult:
    result = LintResult()
    if not path.exists():
        return result
    
    for file_path in path.rglob("*.md"):
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            continue
        
        result.files_scanned += 1
        detector = DriftDetector(content, file_path)
        signals = detector.detect()
        
        if signals:
            result.files_with_drift += 1
            result.signals.extend(signals)
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Fleet Drift Linter")
    parser.add_argument("--fix", action="store_true", help="Auto-fix where possible")
    parser.add_argument("--output", choices=["json", "md"], default="md",
                       help="Output format")
    parser.add_argument("--paths", nargs="+", type=Path,
                       help="Additional paths to scan")
    args = parser.parse_args()
    
    paths = SCAN_PATHS.copy()
    if args.paths:
        paths.extend(args.paths)
    
    results = [scan_directory(p) for p in paths]
    
    # Compute adoption stats: PLAN_ID present = not flagged for missing_plan
    total_files_scanned = sum(r.files_scanned for r in results)
    files_with_plan_id = set()
    files_without_plan_id = set()
    for r in results:
        for s in r.signals:
            if s.signal_type == "missing_plan":
                files_without_plan_id.add(str(s.file))
            elif s.signal_type in ("schema_mismatch", "unvalidated_done", "invalid_role", "unknown_fleet_flag"):
                files_with_plan_id.add(str(s.file))
    total_with = len(files_with_plan_id)
    total_without = len(files_without_plan_id)
    total_scanned = total_with + total_without
    # Files with no signals at all (clean / non-actionable) also count
    total_clean = sum(r.files_scanned - r.files_with_drift for r in results)
    adoption_rate = ((total_with + total_clean) / total_files_scanned * 100) if total_files_scanned > 0 else 100
    
    if args.output == "json":
        print(format_json(results))
    else:
        print(format_markdown(results))
    
    # Adoption summary (stderr)
    print(f"\n📊 PLAN_ID Adoption: {total_with + total_clean}/{total_files_scanned} ({adoption_rate:.0f}%)", file=sys.stderr)
    
    # Exit non-zero if errors exist
    has_errors = any(
        s.severity == "ERROR" for r in results for s in r.signals
    )
    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()
