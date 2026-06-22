#!/bin/bash
# get-email-cred.sh — Secure credential retrieval for SOL email accounts
# NEVER outputs password to stdout. Used by other scripts only.
# Requires: macOS Keychain access

ACCOUNT="$1"
if [ -z "$ACCOUNT" ]; then
    echo "Usage: get-email-cred.sh <account>" >&2
    echo "Accounts: soli.liaison@gmail.com | soli.liaison@systack.net | support@systack.net" >&2
    exit 1
fi

# Retrieve password securely from Keychain
PASS=$(security find-generic-password -s "sol-email-credentials" -a "$ACCOUNT" -w 2>/dev/null)

if [ -z "$PASS" ]; then
    echo "ERROR: Credential not found for $ACCOUNT" >&2
    exit 1
fi

echo "$PASS"
