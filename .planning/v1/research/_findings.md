# Research Findings Summary

## Key Takeaways

1. **No Item listing API.** Plaid has no endpoint to list all connected Items. We must track access_tokens + item_ids ourselves in SQLite. This is the core of the "profile" tracking requirement.

2. **argparse for CLI.** Zero dependencies, verb-noun pattern works cleanly, consistent with all existing skills.

3. **SQLite is right.** Single-user CLI, embedded, no server. Database-selection skill confirms.

4. **Transaction sync is cursor-based.** Store cursor per-Item in SQLite. Loop while `has_more`. First pull gets all history, subsequent pulls are incremental.

5. **Account metadata comes from /accounts/get.** Each call requires an access_token (per-Item). Returns account name, type, subtype, mask (last 4 digits). Need to call this per-Item and store results.

6. **Institution info from /institutions/get_by_id.** Get bank name, logo, URL. Call once per Item at link time, store in profile.

7. **Sandbox supports configurable history.** `days_requested` (1-730) controls how much fake transaction data is generated.

## Constraints on Design

- Multi-Item = multiple access_tokens = need a local registry (SQLite table: items)
- Cursor is per-Item, not per-account — store one cursor per item_id
- Transaction amounts are floats (Plaid returns decimals) — store as REAL in SQLite
- Plaid rate limits exist but are generous for personal use (not a v1 concern)

## What Affects Decomposition

- Need an "items" table (item_id, access_token, institution_id, institution_name, created_at)
- Need an "accounts" table (account_id, item_id, name, official_name, type, subtype, mask)
- Need a "transactions" table (transaction_id, account_id, date, amount, name, merchant_name, pending, iso_currency_code, ...)
- Need a "sync_state" table (item_id, cursor, last_synced_at)
- CLI commands map to: create link, list items, list accounts, get transactions, sync transactions
