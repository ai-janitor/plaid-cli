# S4: CLI Command Handlers

## Purpose
Implement each verb-noun command. Each handler orchestrates calls to S2 (Plaid API) and S1 (database), then returns a result dict that S3 formats for output.

## Requirements Traceability
- §1: Connect banks (create link)
- §2: Pull transactions (sync)
- §4: Query by year/month/new-since (get transactions)

## Dependencies
- S1: Database functions
- S2: Plaid API functions
- S3: Router dispatches to handlers, formats output

---

## Handler Signatures

Every handler receives `(args, config, conn)`:
- `args`: argparse Namespace with parsed flags
- `config`: dict from S3 config cascade (client_id, secret, env, db_path)
- `conn`: SQLite connection from S1

Every handler returns a result dict that S3 formats. On error, handlers raise exceptions — S3 catches and formats.

---

## Commands

### cmd_create_link(args, config, conn) → dict
1. Create Plaid client from config (S2.get_plaid_client)
2. Create sandbox public token (S2.create_sandbox_link) with args.institution or default
3. Exchange for access_token + item_id (S2.exchange_token)
4. Fetch institution info (S2.fetch_institution)
5. Save item to DB (S1.save_item)
6. Fetch account metadata (S2.fetch_accounts)
7. Save accounts to DB (S1.save_accounts)
8. Return: `{"item_id": ..., "institution": ..., "accounts": [...]}`

### cmd_list_items(args, config, conn) → dict
1. Query all items from DB (S1.list_items)
2. Return: `{"count": N, "items": [{"item_id": ..., "institution_name": ..., "created_at": ...}, ...]}`

### cmd_list_accounts(args, config, conn) → dict
1. Query accounts from DB (S1.list_accounts), optionally filtered by args.item
2. Return: `{"count": N, "accounts": [{"account_id": ..., "name": ..., "type": ..., "subtype": ..., "mask": ..., "institution_name": ...}, ...]}`

### cmd_get_transactions(args, config, conn) → dict
1. Query transactions from DB (S1.query_transactions) with:
   - year=args.year
   - month=args.month (formatted as YYYY-MM with year)
   - new_since: if args.new, get the earliest last_synced_at across all items before the most recent sync
   - limit=args.limit
2. Return: `{"count": N, "transactions": [{"transaction_id": ..., "date": ..., "amount": ..., "name": ..., "merchant_name": ..., "account_name": ..., "institution_name": ..., "pending": ...}, ...]}`

### cmd_sync(args, config, conn) → dict
1. Create Plaid client from config (S2.get_plaid_client)
2. Get items to sync: if args.item, just that one. Otherwise, all items from S1.list_items.
3. For each item:
   a. Get current cursor from DB (S1.get_cursor) — None means first sync
   b. Call S2.sync_transactions(client, access_token, cursor)
   c. Upsert added + modified transactions (S1.upsert_transactions)
   d. Remove deleted transactions (S1.remove_transactions)
   e. Save new cursor (S1.save_cursor)
   f. Track counts per item
4. Return: `{"items_synced": N, "added": N, "modified": N, "removed": N, "details": [{"item_id": ..., "institution_name": ..., "added": N, "modified": N, "removed": N}, ...]}`

---

## Behavior

- `cmd_sync` syncs ALL items by default. This is the primary "pull everything new" workflow.
- `cmd_get_transactions` with `--new` flag answers "what came in on the last sync" — it uses `synced_at` timestamps, not Plaid dates.
- `cmd_create_link` is a sandbox-only flow in v1. It creates the link, fetches metadata, and stores everything in one operation.
- All handlers are stateless — they receive conn and config, do work, return results.

## Edge Cases

- `cmd_sync` with no items in DB: return `{"items_synced": 0, ...}` with a message "No items found. Run 'plaid create link' first."
- `cmd_sync` with one item failing (API error): report the error for that item, continue syncing remaining items. Return partial results with error details.
- `cmd_create_link` called multiple times with same institution: creates a new Item each time (Plaid allows multiple Items per institution). Each gets its own item_id and access_token.
- `cmd_get_transactions` with `--new` but no syncs have occurred: return empty list.
- `cmd_list_items` with no items: return `{"count": 0, "items": []}`.
- `cmd_list_accounts` with `--item` that doesn't exist: return `{"count": 0, "accounts": []}`.
