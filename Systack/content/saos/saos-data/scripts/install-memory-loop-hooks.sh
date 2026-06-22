#!/bin/bash
# Wire memory loop to system events
# Run once to install hooks

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_LOOP="$HOME/.openclaw/workspaces/sol/scripts/memory-loop.py"

# Make sure memory-loop.py exists and is executable
if [ ! -f "$MEMORY_LOOP" ]; then
    echo "ERROR: memory-loop.py not found at $MEMORY_LOOP"
    exit 1
fi

# Install plan completion hook
# This watches for plan state changes and logs them
PLAN_HOOK_DIR="$HOME/.openclaw/workspaces/sol/scripts/hooks"
mkdir -p "$PLAN_HOOK_DIR"

cat > "$PLAN_HOOK_DIR/plan-state-change.sh" <> '$1'
PLAN_FILE="$2"
OLD_STATE="$3"
NEW_STATE="$4"

MEMORY_LOOP="$HOME/.openclaw/workspaces/sol/scripts/memory-loop.py"

# Source Python to call the function
python3 -c "
import sys
sys.path.insert(0, '$HOME/.openclaw/workspaces/sol/scripts')
from memory_loop import on_plan_state_change
on_plan_state_change('$PLAN_ID', '$OLD_STATE', '$NEW_STATE')
" 2>> "$HOME/Documents/SOL-System/05-Logs/memory-loop.log"
EOF
chmod +x "$PLAN_HOOK_DIR/plan-state-change.sh"

# Install agent completion hook
cat > "$PLAN_HOOK_DIR/agent-completion.sh" <> '$1'
AGENT="$2"
TASK="$3"
RESULT="$4"
ERRORS="$5"

python3 -c "
import sys
sys.path.insert(0, '$HOME/.openclaw/workspaces/sol/scripts')
from memory_loop import on_agent_completion
on_agent_completion('$AGENT', '$TASK', '$RESULT', '$ERRORS')
" 2>> "$HOME/Documents/SOL-System/05-Logs/memory-loop.log"
EOF
chmod +x "$PLAN_HOOK_DIR/agent-completion.sh"

# Install n8n webhook wrapper
cat > "$PLAN_HOOK_DIR/n8n-webhook.sh" <> '$1'
WORKFLOW="$2"
EXEC_ID="$3"
STATUS="$4"
OUTPUT="$5"
ERROR="$6"

curl -s -X POST http://localhost:8080/api/memory-loop \
  -H "Content-Type: application/json" \
  -d "{
    \"category\": \"workflow\",
    \"source\": \"n8n\",
    \"event\": \"workflow_$STATUS\",
    \"detail\": {
      \"workflow\": \"$WORKFLOW\",
      \"execution_id\": \"$EXEC_ID\",
      \"output\": \"$OUTPUT\",
      \"error\": \"$ERROR\"
    },
    \"leverage\": \"$([ -n \"$ERROR\" ] && echo 'high' || echo 'low')\",
    \"status\": \"$([ -n \"$ERROR\" ] && echo 'failure' || echo 'success')\"
  }" 2>> "$HOME/Documents/SOL-System/05-Logs/memory-loop.log"
EOF
chmod +x "$PLAN_HOOK_DIR/n8n-webhook.sh"

echo "✅ Memory loop hooks installed:"
echo "  Plan changes:    $PLAN_HOOK_DIR/plan-state-change.sh"
echo "  Agent completion: $PLAN_HOOK_DIR/agent-completion.sh"
echo "  n8n webhook:     $PLAN_HOOK_DIR/n8n-webhook.sh"
echo ""
echo "Usage examples:"
echo "  $PLAN_HOOK_DIR/plan-state-change.sh PLAN-001 ACTIVE DONE"
echo "  $PLAN_HOOK_DIR/agent-completion.sh CODY 'Build feature' 'Success' ''"
echo "  $PLAN_HOOK_DIR/n8n-webhook.sh 'Utopia Deli' exec_123 success '2 orders' ''"
