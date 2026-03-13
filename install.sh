#!/usr/bin/env bash
set -e

REPO="https://github.com/ai-janitor/plaid-cli.git"
INSTALL_DIR="${PLAID_INSTALL_DIR:-$HOME/.local/share/plaid-cli}"

echo "Installing plaid-cli..."

# Check for pipx, install if missing
if ! command -v pipx &> /dev/null; then
    if command -v brew &> /dev/null; then
        echo "Installing pipx via brew..."
        brew install pipx --quiet
    elif command -v apt-get &> /dev/null; then
        echo "Installing pipx via apt..."
        sudo apt-get install -y pipx --quiet
    else
        echo "Error: pipx not found. Install it first: https://pipx.pypa.io"
        exit 1
    fi
    pipx ensurepath --quiet 2>/dev/null || true
fi

# Clone or update
if [ -d "$INSTALL_DIR" ]; then
    echo "Updating existing install..."
    git -C "$INSTALL_DIR" pull --quiet
else
    echo "Cloning plaid-cli..."
    git clone --quiet "$REPO" "$INSTALL_DIR"
fi

# Install via pipx
pipx install "$INSTALL_DIR" --force --quiet
echo ""
echo "Installed plaid-cli to ~/.local/bin/plaid"

# Create config dir and .env if needed
CONFIG_DIR="$HOME/.config/plaid"
if [ ! -f "$CONFIG_DIR/.env" ]; then
    mkdir -p "$CONFIG_DIR"
    cp "$INSTALL_DIR/.env.example" "$CONFIG_DIR/.env"
    echo ""
    echo "Edit your credentials:"
    echo "  \$EDITOR $CONFIG_DIR/.env"
    echo ""
    echo "Get keys at: https://dashboard.plaid.com → Developers → Keys"
fi

echo ""
echo "Run:"
echo "  plaid create link"
echo "  plaid sync"
echo "  plaid get transactions"
