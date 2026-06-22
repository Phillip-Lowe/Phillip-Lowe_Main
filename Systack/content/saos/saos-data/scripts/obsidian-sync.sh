#!/usr/bin/env bash
# obsidian-sync.sh — Sync SOL memory files to iCloud Obsidian vault
# Created: 2026-05-30 as part of PLAN-HUBSPOKE-001
# Frequency: Hourly via cron
# Direction: One-way (SOL workspace → iCloud vault)

set -euo pipefail

# Paths
SOL_MEMORY="$HOME/.openclaw/workspaces/sol/memory"
SOL_SCHEMAS="$HOME/.openclaw/workspaces/sol/schemas"
SOL_SCRIPTS="$HOME/.openclaw/workspaces/sol/scripts"
ICLOUD_VAULT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/My vault"
VAULT_MEMORY="$ICLOUD_VAULT/02-Memory"
VAULT_SYSTEM="$ICLOUD_VAULT/09-SOL-System"
VAULT_SCHEMAS="$ICLOUD_VAULT/09-SOL-System/schemas"
VAULT_SCRIPTS="$ICLOUD_VAULT/09-SOL-System/scripts"

# Ensure vault directories exist
mkdir -p "$VAULT_MEMORY"
mkdir -p "$VAULT_MEMORY/Daily-Logs"
mkdir -p "$VAULT_MEMORY/Plans"
mkdir -p "$VAULT_SYSTEM"
mkdir -p "$VAULT_SCHEMAS"
mkdir -p "$VAULT_SCRIPTS"

# Sync memory files
if [ -d "$SOL_MEMORY" ]; then
    # Daily logs
    rsync -av --delete "$SOL_MEMORY/"*.md "$VAULT_MEMORY/Daily-Logs/" 2>/dev/null || true
    
    # Plans
    if [ -d "$SOL_MEMORY/plans" ]; then
        rsync -av --delete "$SOL_MEMORY/plans/" "$VAULT_MEMORY/Plans/"
    fi
    
    # Root memory files
    for file in MEMORY.md plan-registry.md; do
        if [ -f "$SOL_MEMORY/../$file" ]; then
            cp "$SOL_MEMORY/../$file" "$VAULT_MEMORY/$file"
        fi
    done
fi

# Sync schemas
if [ -d "$SOL_SCHEMAS" ]; then
    rsync -av --delete "$SOL_SCHEMAS/" "$VAULT_SCHEMAS/"
fi

# Sync key scripts (write-guard)
if [ -f "$SOL_SCRIPTS/write-guard.py" ]; then
    cp "$SOL_SCRIPTS/write-guard.py" "$VAULT_SCRIPTS/write-guard.py"
fi

# Sync system files
for file in AGENTS.md SOUL.md IDENTITY.md USER.md TOOLS.md HEARTBEAT.md; do
    src="$HOME/.openclaw/workspaces/sol/$file"
    if [ -f "$src" ]; then
        cp "$src" "$VAULT_SYSTEM/$file"
    fi
done

echo "[$(date -Iseconds)] Obsidian sync complete"
