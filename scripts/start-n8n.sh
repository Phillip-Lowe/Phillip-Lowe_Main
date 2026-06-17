#!/bin/bash
# Start n8n with secure cookie disabled (REQUIRED for HTTP/local access)
# This is mandatory - n8n will not work without it
export N8N_SECURE_COOKIE=false
cd ~
nohup n8n start > /tmp/n8n.log 2>&1 &
echo "n8n started with N8N_SECURE_COOKIE=false"
