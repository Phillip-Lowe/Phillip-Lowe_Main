#!/bin/bash
# n8n Environment Setup for Systack Lead Scraper
# Source this before starting n8n

export GOOGLE_MAPS_API_KEY="AIzaSyBhmoUCGTCYVIPW1Y_Dlvapv7w7H7U_T4Y"
export CRM_DB_PATH="/Users/philliplowe/.openclaw/workspaces/sol/green-systems-crm.db"
export N8N_CODE_ALLOW_EXTERNAL=sqlite3
export N8N_SECURE_COOKIE=false
export NODE_PATH="/opt/homebrew/lib/node_modules"

echo "✅ n8n env vars loaded:"
echo "  GOOGLE_MAPS_API_KEY: ${GOOGLE_MAPS_API_KEY:0:10}..."
echo "  CRM_DB_PATH: $CRM_DB_PATH"
echo "  N8N_CODE_ALLOW_EXTERNAL: $N8N_CODE_ALLOW_EXTERNAL"
echo "  N8N_SECURE_COOKIE: $N8N_SECURE_COOKIE"
