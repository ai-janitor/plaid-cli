# Test Contracts — v1

## S1: Database

| Function | Input/Precondition | Expected Output/Postcondition |
|----------|-------------------|-------------------------------|
| get_connection | db_path to non-existent file | Creates file, all 4 tables exist |
| get_connection | db_path to existing DB | Returns connection, tables unchanged |
| save_item | new item_id | Row inserted in items table |
| save_item | existing item_id | Row replaced (access_token updated) |
| list_items | 3 items in DB | Returns list of 3 dicts |
| list_items | empty DB | Returns empty list |
| get_item | existing item_id | Returns dict with all fields |
| get_item | non-existent item_id | Returns None |
| delete_item | existing item_id with accounts + transactions | Item, accounts, transactions, sync_state all deleted |
| save_accounts | list of 2 accounts | 2 rows in accounts table |
| list_accounts | no filter | All accounts with institution_name joined |
| list_accounts | item_id filter | Only accounts for that item |
| upsert_transactions | 5 new transactions | 5 rows inserted, returns 5 |
| upsert_transactions | 2 modified (existing IDs) | Rows updated, returns 2 |
| remove_transactions | 2 valid IDs | 2 rows deleted, returns 2 |
| remove_transactions | 1 invalid ID | No error, returns 0 |
| query_transactions | year=2026 | Only 2026 transactions returned |
| query_transactions | year=2026, month=3 | Only March 2026 transactions |
| query_transactions | month=3, no year | Raises error |
| query_transactions | new_since=timestamp | Only transactions with synced_at > timestamp |
| query_transactions | no filters, limit=10 | Most recent 10 by date DESC |
| query_transactions | empty DB | Returns empty list |
| save_cursor | new item_id | Row inserted with cursor and last_synced_at |
| save_cursor | existing item_id | Cursor and last_synced_at updated |
| get_cursor | existing item_id | Returns cursor string |
| get_cursor | non-existent item_id | Returns None |

## S2: Plaid API Client

| Function | Input/Precondition | Expected Output/Postcondition |
|----------|-------------------|-------------------------------|
| get_plaid_client | valid client_id, secret, "sandbox" | Returns PlaidApi instance |
| create_sandbox_link | valid client, default institution | Returns public_token string |
| create_sandbox_link | valid client, invalid institution_id | Raises Plaid API error |
| exchange_token | valid public_token | Returns (access_token, item_id) |
| fetch_accounts | valid access_token | Returns list of dicts with account fields |
| fetch_institution | valid institution_id | Returns dict with institution_id, name |
| sync_transactions | valid access_token, cursor=None | Returns (added[], modified[], removed[], next_cursor) |
| sync_transactions | valid access_token, valid cursor, no changes | Returns ([], [], [], cursor) |
| sync_transactions | invalid access_token | Raises Plaid API error |

## S3: CLI Router and Output

| Scenario | Input | Expected |
|----------|-------|----------|
| No args | `plaid` | Print help, exit 2 |
| Verb only | `plaid list` | Print list help, exit 2 |
| Valid command | `plaid list items` | Exit 0, human table output |
| --json flag | `plaid list items --json` | Valid JSON on stdout |
| --quiet flag | `plaid list items -q` | One ID per line |
| --json + --quiet | `plaid list items --json -q` | JSON wins |
| --month no --year | `plaid get transactions --month 3` | Error message, exit 2 |
| Missing credentials | no PLAID_* env, no config | Error with hint, exit 1 |
| --help at root | `plaid --help` | Shows all verbs |
| --help at verb | `plaid get --help` | Shows get nouns |
| --help at noun | `plaid get transactions --help` | Shows transaction flags |

## S4: Command Handlers

| Handler | Input/Precondition | Expected Output/Postcondition |
|---------|-------------------|-------------------------------|
| cmd_create_link | valid config | Item + accounts saved to DB, returns item_id + accounts |
| cmd_list_items | 2 items in DB | Returns count=2 with item details |
| cmd_list_items | empty DB | Returns count=0, empty list |
| cmd_list_accounts | 3 accounts across 2 items | Returns count=3 with institution_name |
| cmd_list_accounts | --item filter | Returns only that item's accounts |
| cmd_get_transactions | --year 2026 | Returns only 2026 transactions |
| cmd_get_transactions | --new, recent sync exists | Returns transactions from last sync |
| cmd_get_transactions | --new, no syncs | Returns empty list |
| cmd_sync | 2 items, both have new transactions | Syncs both, returns combined counts |
| cmd_sync | --item specific | Syncs only that item |
| cmd_sync | no items in DB | Returns items_synced=0 with message |
| cmd_sync | one item fails, one succeeds | Reports error for failed, returns partial results |
