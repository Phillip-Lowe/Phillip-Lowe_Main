#!/bin/bash
# sync-site.sh — Sync Systack site files from workspace to deploy repo
# 
# Usage: ./sync-site.sh
#   or:  ./sync-site.sh --dry-run  (preview changes without applying)
#
# This script copies the current site files from the workspace
# (Phillip-Lowe_Main/Systack/content/systack-site/) to the deploy repo
# (Phillip-Lowe/systack) and pushes to GitHub.

set -euo pipefail

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "🔍 DRY RUN — no changes will be pushed"
fi

# Paths
WORKSPACE_SITE="/Users/philliplowe/.openclaw/workspaces/sol/Systack/content/systack-site"
DEPLOY_DIR="/tmp/systack-deploy-$$"
REPO_URL="https://github.com/Phillip-Lowe/systack.git"

# Files and dirs to sync
FILES=(
    index.html
    about.html
    contact.html
    discovery.html
    local-dashboard.html
    pricing.html
    private-dashboard.html
    services.html
    test-book.html
    CNAME
)
DIRS=(
    assets
    brand
    personal-agent
    services
    work
    saos
    saos-landing
    case-studies
    demos
    docs
    niches
    audit
    partners
)

echo "📦 Syncing site files to deploy repo..."
echo "   Source: $WORKSPACE_SITE"
echo "   Target: $REPO_URL"
echo ""

# Clone deploy repo
if [[ -d "$DEPLOY_DIR" ]]; then
    rm -rf "$DEPLOY_DIR"
fi
git clone --depth 1 "$REPO_URL" "$DEPLOY_DIR" >/dev/null 2>&1
cd "$DEPLOY_DIR"

echo "✅ Cloned deploy repo"

# Copy files
for file in "${FILES[@]}"; do
    src="$WORKSPACE_SITE/$file"
    if [[ -f "$src" ]]; then
        cp "$src" .
        echo "  📄 Copied: $file"
    else
        echo "  ⚠️  Missing: $file (skipped)"
    fi
done

# Copy directories
for dir in "${DIRS[@]}"; do
    src="$WORKSPACE_SITE/$dir"
    if [[ -d "$src" ]]; then
        rm -rf "$dir" 2>/dev/null || true
        cp -r "$src" .
        echo "  📁 Copied: $dir/"
    else
        echo "  ⚠️  Missing: $dir/ (skipped)"
    fi
done

echo ""

# Show git status
git add -A
echo "📊 Changes:"
git status --short

if [[ "$DRY_RUN" == true ]]; then
    echo ""
    echo "🛑 DRY RUN — changes NOT committed or pushed"
    echo "   Remove --dry-run to apply changes"
    rm -rf "$DEPLOY_DIR"
    exit 0
fi

# Commit and push
COMMIT_MSG="site: Sync from workspace ($(date +%Y-%m-%d-%H%M))

Files synced from Phillip-Lowe_Main/Systack/content/systack-site/"

git commit -m "$COMMIT_MSG" >/dev/null 2>&1
echo ""
echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Site synced! GitHub Pages will deploy in ~2 minutes."
echo "   Verify: curl -s https://systack.net | grep 'Your Business'"

# Cleanup
rm -rf "$DEPLOY_DIR"
