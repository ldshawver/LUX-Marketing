#!/usr/bin/env bash

# SSH Key Setup Script for GitHub
# This script helps add SSH keys to your GitHub account

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
SSH_KEY_PATH="${HOME}/.ssh/id_ed25519_luxit.pub"
MACHINE_NAME="Mac Studio luxit"

echo "=== GitHub SSH Key Setup ==="
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed.${NC}"
    echo "Please install it from: https://cli.github.com/"
    echo ""
    echo "On macOS: brew install gh"
    echo "On Ubuntu/Debian: sudo apt install gh"
    exit 1
fi

# Check if authenticated with gh
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}You need to authenticate with GitHub CLI first.${NC}"
    echo "Run: gh auth login"
    exit 1
fi

# Allow custom SSH key path
if [ -n "$1" ]; then
    SSH_KEY_PATH="$1"
fi

# Allow custom machine name
if [ -n "$2" ]; then
    MACHINE_NAME="$2"
fi

# Check if SSH key file exists
if [ ! -f "$SSH_KEY_PATH" ]; then
    echo -e "${RED}Error: SSH key not found at ${SSH_KEY_PATH}${NC}"
    echo ""
    echo "To generate a new SSH key, run:"
    echo "  ssh-keygen -t ed25519 -C \"your_email@example.com\" -f ${SSH_KEY_PATH%.pub}"
    exit 1
fi

# Generate title with current date
CURRENT_DATE=$(date +%F)
KEY_TITLE="${MACHINE_NAME} ${CURRENT_DATE}"

echo "SSH Key Path: ${SSH_KEY_PATH}"
echo "Key Title: ${KEY_TITLE}"
echo ""

# Add SSH key to GitHub
echo "Adding SSH key to GitHub..."
if gh ssh-key add "$SSH_KEY_PATH" --title "$KEY_TITLE"; then
    echo ""
    echo -e "${GREEN}✓ SSH key successfully added to GitHub!${NC}"
    echo ""
    echo "You can view your SSH keys at: https://github.com/settings/keys"
else
    echo ""
    echo -e "${RED}✗ Failed to add SSH key to GitHub${NC}"
    exit 1
fi

echo ""
echo "=== Setup Complete ==="
