#!/bin/bash
# SAOS Daily Revenue Tracker
# Usage: ./track-revenue.sh "leads_added=5" "emails_sent=5" "replies=1"

LOG_FILE="$HOME/.openclaw/workspaces/sol/revenue-pipeline/daily-log.txt"
DATE=$(date +"%Y-%m-%d")

# Create log if it doesn't exist
if [ ! -f "$LOG_FILE" ]; then
    echo "# SAOS Daily Revenue Log" > "$LOG_FILE"
    echo "# Started: $DATE" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
fi

# Append today's entry
echo "---" >> "$LOG_FILE"
echo "Date: $DATE" >> "$LOG_FILE"
echo "Time: $(date +"%H:%M")" >> "$LOG_FILE"

# Parse arguments
for arg in "$@"; do
    echo "$arg" | sed 's/=/: /' >> "$LOG_FILE"
done

echo "" >> "$LOG_FILE"

# Show running totals
echo "Logged: $*"
echo ""
echo "=== Running Totals ==="
echo "Total leads added: $(grep -c 'leads_added=' "$LOG_FILE" 2>/dev/null || echo 0)"
echo "Total emails sent: $(grep -c 'emails_sent=' "$LOG_FILE" 2>/dev/null || echo 0)"
echo "Total replies: $(grep -c 'replies=' "$LOG_FILE" 2>/dev/null || echo 0)"
echo "Total meetings: $(grep -c 'meetings=' "$LOG_FILE" 2>/dev/null || echo 0)"
echo "Total demos: $(grep -c 'demos=' "$LOG_FILE" 2>/dev/null || echo 0)"
echo "Total proposals: $(grep -c 'proposals=' "$LOG_FILE" 2>/dev/null || echo 0)"
echo "Total closed: $(grep -c 'closed=' "$LOG_FILE" 2>/dev/null || echo 0)"
echo "Total revenue: \$(grep 'revenue=' "$LOG_FILE" 2>/dev/null | sed 's/.*=//' | awk '{sum+=\$1} END {print sum}')"
