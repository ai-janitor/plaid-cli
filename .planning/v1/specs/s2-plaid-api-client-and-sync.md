# S2: Plaid API Client and Sync

## Purpose
Wrap the Plaid Python SDK into focused functions the CLI can call. Handle client configuration, bank connection (link), account metadata, and transaction syncing.

## Requirements Traceability
- §1: Connect multiple banks, sandbox mode, persist tokens, track profiles
- §2: /transactions/sync, cursor-based incremental, full history on first pull

## Dependencies
- S1: Stores items, accounts, transactions, cursors in SQLite

---

## Functions

### Client Configuration
- `get_plaid_client(client_id, secret, env) → PlaidApi` — Create configured Plaid client. `env` is one of: sandbox, development, production. Maps to `plaid.Environment.*`.

### Bank Connection (Link)
- `create_sandbox_link(client, institution_id="ins_109508", products=["transactions"]) → (public_token)` — Call `sandbox_public_token_create`. Returns public_token.
- `exchange_token(client, public_token) → (access_token, item_id)` — Call `item_public_token_exchange`. Returns access_token and item_id.

### Account and Institution Metadata
- `fetch_accounts(client, access_token) → list[dict]` — Call `accounts_get`. Return list of dicts with: account_id, name, official_name, type, subtype, mask.
- `fetch_institution(client, institution_id) → dict` — Call `institutions_get_by_id` with country_codes=["US"]. Return dict with: institution_id, name.

### Transaction Sync
- `sync_transactions(client, access_token, cursor=None) → (added, modified, removed, next_cursor)` — Call `transactions_sync` in a loop while `has_more`. Accumulate all added, modified, removed across pages. Return flat lists + final cursor.
  - `added`: list of dicts with transaction table fields (transaction_id, account_id, date, amount, name, merchant_name, pending, iso_currency_code, payment_channel)
  - `modified`: same shape as added
  - `removed`: list of dicts with transaction_id only
  - `next_cursor`: string to persist for next incremental sync

---

## Behavior

- `get_plaid_client()` does not read env vars or config files — it receives credentials as arguments. The CLI layer (S3/S4) handles config cascade.
- `create_sandbox_link()` is sandbox-only. In development/production, the CLI would need Plaid Link (browser flow) — out of scope for v1.
- `sync_transactions()` loops while `has_more == true`. If cursor is None, passes no cursor to get full history. If cursor is empty string from Plaid (no data ready yet), waits 2 seconds and retries up to 5 times.
- `fetch_accounts()` and `fetch_institution()` are called once at link-creation time, not on every sync.
- Transaction dicts returned by `sync_transactions()` are already flattened to match the S1 schema — the caller can pass them directly to `upsert_transactions()`.

## Edge Cases

- Plaid API error (invalid token, rate limit, server error): raise with the Plaid error message. Do not catch — let S4 handle and format.
- `sync_transactions()` with an expired or invalid cursor: Plaid returns an error. Let it propagate.
- `create_sandbox_link()` with invalid institution_id: Plaid returns error. Let it propagate.
- `fetch_institution()` — some sandbox institutions may not have all metadata fields. Return what's available, use empty strings for missing.
- `sync_transactions()` returns empty added/modified/removed on a no-change sync: valid result, not an error.
