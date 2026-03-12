# Clean Requirements — Plaid Bank Transaction Puller

Derived from REQUIREMENTS-RAW.md on 2026-03-12. v1 — no upstream feedback.

---

## 1. Bank Connection Management

- The user connects multiple bank accounts (each bank login = one Plaid Item)
- Each Item may contain multiple accounts (checking, savings, credit card)
- The system stores and tracks a profile for each connected Item: institution name, account names, account types, account IDs
- Access tokens are persisted locally so connections survive across CLI invocations
- In sandbox mode, bank connections are created without the Plaid Link UI (using sandbox public token creation)
- In development/production mode, bank connections use the standard Plaid Link flow

## 2. Transaction Retrieval

- Transactions are pulled from all connected accounts across all Items
- The system uses the Plaid `/transactions/sync` endpoint (cursor-based incremental updates)
- On first pull for an Item, all available transaction history is fetched
- On subsequent pulls, only new/modified/removed transactions since the last cursor are fetched
- The sync cursor is persisted per-Item so incremental pulls work across CLI invocations

## 3. Transaction Storage

- Transactions are stored in a local SQLite database
- Each transaction record includes the account it belongs to (flat list, not grouped)
- The database tracks added, modified, and removed transactions from the sync endpoint
- Removed transactions are deleted from the database

## 4. Transaction Querying

- Query all transactions (flat list with account info per row)
- Filter by year
- Filter by month
- Filter by "new since last pull" (transactions added in the most recent sync)
- No categorization, export, or analysis features

## 5. CLI Interface

- Verb-noun command structure (max 2 subcommand levels)
- Three output modes: human-readable table (default), `--json` (structured JSON), `--quiet` (pipe-friendly IDs/values only)
- `--help` at every level (root, verb group, subcommand)
- No interactive prompts — all input via flags and arguments
- Configuration cascade: command flags > environment variables (`PLAID_*`) > config file > defaults
- Meaningful exit codes: 0 = success, 1 = error, 2 = usage error
- Agent rules file generatable so AI agents can learn the CLI

## 6. Code Organization

- Python CLI using the `plaid-python` SDK
- No web framework (no Flask, no server)
- Self-documenting file and function naming (noun+verb, AI-readable from `ls`)
- 1 file = 1 function, directory = domain
- File/folder names understandable by an AI agent from directory listing alone

---

## Out of Scope (v1)

- Transaction categorization or tagging
- CSV/Excel export
- Spending analysis or visualizations
- Web UI or dashboard
- Multi-user support
- Real bank connections (sandbox only for v1 — architecture supports upgrade)
