#!/bin/bash

###############################################################################
# ClaudeTask Framework - Quick Install from GitHub
#
# Usage:
#   curl -fsSL YOUR_GITHUB_RAW_URL/quick-install.sh | bash
###############################################################################

set -e

REPO_URL="https://github.com/YOUR_USERNAME/claude-code-feature-framework.git"
INSTALL_DIR="claudetask-framework"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}  🚀 ClaudeTask Framework - Quick Install                 ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check git
if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install git first."
    exit 1
fi

# Clone repository
echo "📥 Cloning repository..."
if [ -d "$INSTALL_DIR" ]; then
    echo "⚠️  Directory $INSTALL_DIR already exists"
    read -p "Remove and reinstall? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
    else
        exit 0
    fi
fi

git clone "$REPO_URL" "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Run installation
echo ""
echo "🔧 Running installation..."
chmod +x install.sh
./install.sh

echo ""
echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""
echo "To start:"
echo "  cd $INSTALL_DIR"
echo "  ./start.sh"
echo ""
