# Plaid Bank Transaction Puller

## Purpose
Pull personal bank transactions using the Plaid API. Python-based project using the official `plaid-python` SDK.

## Tech Stack
- Python 3.13
- `plaid-python` SDK
- SQLite for local transaction storage

## Project Structure
```
plaid/
├── CLAUDE.md
├── .env                  # Plaid credentials (NEVER commit)
├── .env.example          # Template for .env
├── .gitignore
├── requirements.txt
├── .venv/                # Python virtual environment (not committed)
├── src/
│   ├── __init__.py
│   ├── plaid_client_configuration.py      # Plaid API client setup
│   ├── link_token_creation_and_exchange.py # Link flow: create link token, exchange public token for access token
│   ├── transaction_sync_and_fetch.py       # Pull transactions via /transactions/sync
│   └── transaction_storage_sqlite.py       # Store and query transactions locally
└── scripts/
    └── run-transaction-pull.py             # Main entry point: end-to-end transaction fetch
```

## Key Flow
1. Configure Plaid client with credentials from `.env`
2. Create a link token → user connects bank via Plaid Link (or use Sandbox)
3. Exchange public_token for access_token
4. Call `/transactions/sync` to pull transactions
5. Store results in local SQLite DB

## Environment Variables (.env)
```
PLAID_CLIENT_ID=<your_client_id>
PLAID_SECRET=<your_sandbox_secret>
PLAID_ENV=sandbox
```

## Commands
- `source .venv/bin/activate` — activate virtual environment
- `pip install -r requirements.txt` — install dependencies
- `python scripts/run-transaction-pull.py` — pull transactions

## Plaid API Docs
- Transactions API: https://plaid.com/docs/api/products/transactions/
- Quickstart: https://plaid.com/docs/quickstart/
- Python SDK: https://github.com/plaid/plaid-python
