# Decomposition — v1

## Spec Units

### S1: SQLite Database Schema and Access
- **Covers:** §3 Transaction Storage, §1 profile persistence, §2 cursor persistence
- **What:** Define and create all tables (items, accounts, transactions, sync_state). Provide functions for insert/update/delete/query on each table. Connection management.
- **Requirements traced:** §1 (persist access tokens, track profiles), §2 (persist cursor), §3 (all bullets), §4 (query by year/month/new-since)
- **Dependencies:** None — foundation layer
- **Why one unit:** All four tables are tightly coupled (foreign keys, shared connection). Query functions depend on schema. Can't test one without the others.

### S2: Plaid API Client
- **Covers:** §1 Bank Connection Management, §2 Transaction Retrieval
- **What:** Configure Plaid client from credentials. Create sandbox public tokens. Exchange tokens for access tokens. Fetch account metadata. Fetch institution info. Sync transactions (with pagination). Support sandbox/development/production environments.
- **Requirements traced:** §1 (all bullets), §2 (all bullets)
- **Dependencies:** S1 (stores results in DB)
- **Why one unit:** All Plaid API calls share the same client configuration and credential handling. Separating "link" from "sync" would split a natural API-client boundary.

### S3: CLI Command Router and Output Formatting
- **Covers:** §5 CLI Interface, §6 Code Organization
- **What:** argparse verb-noun command tree. Global flags (--json, --quiet). Output formatting (human table, JSON, quiet). Error formatting. Help at every level. Exit codes. Config cascade (flags > env > config file > defaults).
- **Requirements traced:** §5 (all bullets), §6 (Python CLI, no web framework)
- **Dependencies:** S1 (queries DB for display), S2 (calls Plaid API for create/sync commands)
- **Why one unit:** The router, flag parsing, and output formatting are one cohesive interface layer. Splitting router from formatters would create artificial boundaries — they share the --json/--quiet flag state.

### S4: CLI Command Handlers
- **Covers:** §1 (create link flow), §2 (sync flow), §4 (query flows)
- **What:** Implementation of each verb-noun command: `create link`, `list items`, `list accounts`, `get transactions`, `sync transactions`. Each handler orchestrates calls to S2 (Plaid API) and S1 (DB), then passes results to S3 (output formatting).
- **Requirements traced:** §1 (connect banks), §2 (pull transactions), §4 (query by year/month/new-since)
- **Dependencies:** S1, S2, S3
- **Why one unit:** Handlers are thin glue — each is ~20 lines calling API + DB + formatter. Too small individually, natural as a group. All share the same handler signature pattern.

---

## Dependency Graph

```
S1: Database Schema ──────────────────┐
                                      ▼
S2: Plaid API Client ──► depends on S1
                                      │
S3: CLI Router + Output ──────────────┤
                                      ▼
S4: CLI Command Handlers ──► depends on S1, S2, S3
```

## Build Order

| Wave | Spec | Rationale |
|------|------|-----------|
| A (Tier 0) | S1: Database | No dependencies. Foundation. |
| B (Tier 1) | S2: Plaid API Client | Depends on S1 for storage. |
| B (Tier 1) | S3: CLI Router + Output | Depends on S1 for queries. Can build in parallel with S2. |
| C (Tier 2) | S4: Command Handlers | Depends on all three. Glue layer. |

## Boundary Rationale

- **S1↔S2 boundary:** S2 calls S1 functions to store Items, accounts, transactions, and cursors after API calls.
- **S1↔S3 boundary:** S3 calls S1 query functions to display data.
- **S2↔S4 boundary:** S4 calls S2 functions to create links and sync transactions.
- **S1↔S4 boundary:** S4 calls S1 query functions for get/list commands.
- **S3↔S4 boundary:** S4 receives parsed args from S3 router, returns results to S3 formatters.
