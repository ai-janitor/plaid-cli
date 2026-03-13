#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Setting up plaid-cli..."

# Check for pipx, install if missing
if ! command -v pipx &> /dev/null; then
    if command -v brew &> /dev/null; then
        echo "pipx not found — installing via brew..."
        brew install pipx --quiet
        pipx ensurepath --quiet 2>/dev/null || true
    else
        echo "pipx not found — installing via pip..."
        python3 -m pip install --user pipx --quiet 2>/dev/null \
            || python3 -m pip install --user --break-system-packages pipx --quiet
        python3 -m pipx ensurepath --quiet 2>/dev/null || true
    fi
    echo "Installed pipx. You may need to restart your shell for PATH changes."
fi

# Install via pipx
pipx install "$SCRIPT_DIR" --force --quiet
echo "Installed plaid-cli via pipx"

# Show install location
PLAID_BIN=$(command -v plaid 2>/dev/null || echo "~/.local/bin/plaid")
echo "Installed to: $PLAID_BIN"

# Create .env from example if it doesn't exist
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo ""
    echo "Created .env from template — edit it with your Plaid credentials:"
    echo "  PLAID_CLIENT_ID=your_client_id"
    echo "  PLAID_SECRET=your_sandbox_secret"
    echo ""
    echo "Get your keys at: https://dashboard.plaid.com → Developers → Keys"
else
    echo ".env already exists, skipping"
fi

echo ""
echo "Setup complete. Run from anywhere:"
echo "  plaid create link"
echo "  plaid sync"
echo "  plaid get transactions"
