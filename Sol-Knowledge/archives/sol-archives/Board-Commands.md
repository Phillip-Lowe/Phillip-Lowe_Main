# Board Command Interface — SOL Control

Short commands for Green to control the system instantly.

## Mode Commands

| Command | Action |
|---------|--------|
| `/mode autonomy` | Switch to AUTONOMY mode |
| `/mode supervised` | Switch to SUPERVISED mode (default) |
| `/mode locked` | Switch to LOCKED mode |
| `/mode?` | Show current mode |

## Execution Commands

| Command | Action |
|---------|--------|
| `go` / `proceed` / `approved` | Approve pending action or phase |
| `stop` / `halt` / `pause` | Stop current execution |
| `skip` / `override <agent>` | Skip agent or override objection |
| `redo` / `retry` | Restart failed step |
| `status` / `where` | Show current state, phase, blockers |

## Quick Queries

| Command | Response |
|---------|----------|
| `agents?` | List active agents and their status |
| `plan?` | Show current plan with progress |
| `risks?` | Show Pessi's latest critique |
| `valid?` | Show Vali's latest validation |

## Meta Commands

| Command | Action |
|---------|--------|
| `voice on` | Enable ElevenLabs TTS for SOL responses |
| `voice off` | Disable TTS, text only |
| `brief` | Request concise output (1-2 sentences) |
| `verbose` | Request detailed output |

## Usage Rules

- Commands work anywhere in conversation
- SOL acknowledges immediately
- If command is ambiguous, SOL asks for clarification
- All commands logged to memory for audit trail

## Examples

```
Green: /mode autonomy
SOL: Mode switched to AUTONOMY. I'll execute low/medium actions without asking.

Green: go
SOL: Phase 2 approved. Proceeding to BUILD with Assembly.

Green: status
SOL: Current: Phase 2 of 4 (BUILD). Assembly building FastAPI endpoints. 2 of 5 complete. No blockers.

Green: risks?
SOL: Pessi flagged: No input validation on POST /leads. Assembly will add Pydantic schemas before completion.
```
