# S1: SQLite Database Schema and Access

## Purpose
Define the SQLite schema and provide all data access functions. This is the foundation layer — every other spec depends on it for persistence.

## Requirements Traceability
- §1: Persist access tokens, track profiles (institution, accounts)
- §2: Persist sync cursor per-Item
- §3: Store transactions in SQLite, handle add/modify/remove
- §4: Query by year, month, new-since-last-pull

## Dependencies
None.

---

## Schema

### Table: items
| Column | Type | Constraints |
|--------|------|-------------|
| item_id | TEXT | PRIMARY KEY |
| access_token | TEXT | NOT NULL |
| institution_id | TEXT | |
| institution_name | TEXT | |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP |

### Table: accounts
| Column | Type | Constraints |
|--------|------|-------------|
| account_id | TEXT | PRIMARY KEY |
| item_id | TEXT | NOT NULL, FK → items.item_id |
| name | TEXT | NOT NULL |
| official_name | TEXT | |
| type | TEXT | |
| subtype | TEXT | |
| mask | TEXT | |

### Table: transactions
| Column | Type | Constraints |
|--------|------|-------------|
| transaction_id | TEXT | PRIMARY KEY |
| account_id | TEXT | NOT NULL, FK → accounts.account_id |
| date | TEXT | NOT NULL (ISO 8601: YYYY-MM-DD) |
| amount | REAL | NOT NULL |
| name | TEXT | NOT NULL |
| merchant_name | TEXT | |
| pending | INTEGER | NOT NULL DEFAULT 0 |
| iso_currency_code | TEXT | DEFAULT 'USD' |
| payment_channel | TEXT | |
| synced_at | TEXT | DEFAULT CURRENT_TIMESTAMP |

### Table: sync_state
| Column | Type | Constraints |
|--------|------|-------------|
| item_id | TEXT | PRIMARY KEY, FK → items.item_id |
| cursor | TEXT | NOT NULL |
| last_synced_at | TEXT | DEFAULT CURRENT_TIMESTAMP |

---

## Functions

### Connection
- `get_connection(db_path) → Connection` — Open SQLite connection with row_factory=Row, WAL mode. Create all tables if not exist.

### Items
- `save_item(conn, item_id, access_token, institution_id, institution_name) → None` — INSERT OR REPLACE into items.
- `list_items(conn) → list[dict]` — SELECT all items.
- `get_item(conn, item_id) → dict | None` — SELECT one item by ID.
- `delete_item(conn, item_id) → None` — DELETE item and cascade (accounts, transactions, sync_state).

### Accounts
- `save_accounts(conn, item_id, accounts: list[dict]) → None` — INSERT OR REPLACE each account. Each dict has: account_id, name, official_name, type, subtype, mask.
- `list_accounts(conn, item_id=None) → list[dict]` — SELECT all accounts, optionally filtered by item_id. Join items table to include institution_name.

### Transactions
- `upsert_transactions(conn, transactions: list[dict]) → int` — INSERT OR REPLACE. Return count. Each dict has all transaction table columns.
- `remove_transactions(conn, transaction_ids: list[str]) → int` — DELETE by transaction_id. Return count.
- `query_transactions(conn, year=None, month=None, new_since=None, limit=100) → list[dict]` — SELECT with optional filters. Join accounts to include account name and institution. Order by date DESC.
  - `year`: filter WHERE strftime('%Y', date) = year
  - `month`: filter WHERE strftime('%Y-%m', date) = year-month (requires year)
  - `new_since`: filter WHERE synced_at > new_since timestamp
  - When no filters: return most recent `limit` transactions

### Sync State
- `save_cursor(conn, item_id, cursor) → None` — INSERT OR REPLACE cursor and update last_synced_at.
- `get_cursor(conn, item_id) → str | None` — SELECT cursor for item.
- `get_last_synced_at(conn, item_id) → str | None` — SELECT last_synced_at for item.

---

## Behavior

- All write operations commit immediately (autocommit per function call).
- `get_connection()` enables WAL mode for concurrent read safety.
- `delete_item()` cascades: deletes related accounts, transactions, and sync_state.
- `query_transactions()` with `new_since` uses the `synced_at` column, not the Plaid `date` — this answers "what came in on the last sync."
- All dates stored as ISO 8601 strings (TEXT), not SQLite date types.

## Edge Cases

- `save_item()` with an existing item_id: overwrites (REPLACE). Access token rotation is supported.
- `upsert_transactions()` with an existing transaction_id: overwrites (modified transaction from Plaid).
- `remove_transactions()` with a transaction_id not in DB: no error, no-op.
- `query_transactions()` with no filters and empty DB: returns empty list.
- `query_transactions()` with month but no year: return error — month requires year.
- `get_cursor()` for an item with no sync history: returns None — caller does initial full sync.
- DB file does not exist: `get_connection()` creates it and all tables.
