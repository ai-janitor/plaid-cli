#!/usr/bin/env bash
set -e

echo "Setting up plaid-cli..."

# Create virtual environment
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Created virtual environment"
fi

# Install package
.venv/bin/pip install -e . --quiet
echo "Installed plaid-cli"

# Create .env from example if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
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
echo "Setup complete. To get started:"
echo "  source .venv/bin/activate"
echo "  plaid create link"
echo "  plaid sync"
echo "  plaid get transactions"
