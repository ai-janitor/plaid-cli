# SPEC: s1-sqlite-database-schema-and-access.md
# PURPOSE: SQLite connection management and schema creation
# RESPONSIBILITIES: Open connection with WAL mode and row_factory=Row.
#   Create all 4 tables (items, accounts, transactions, sync_state) if not exist.
# NOT RESPONSIBLE FOR: Data access (handled by other database modules)
# DEPENDENCIES: sqlite3

import sqlite3
import os


# --- get_connection(db_path) → Connection ---
def get_connection(db_path):
    #   --- Create parent directory if needed ---
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    #   --- Connect to db_path with row_factory = sqlite3.Row ---
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    #   --- Enable WAL mode: PRAGMA journal_mode=WAL ---
    conn.execute('PRAGMA journal_mode=WAL')

    #   --- Enable foreign keys: PRAGMA foreign_keys=ON ---
    conn.execute('PRAGMA foreign_keys=ON')

    #   --- CREATE TABLE IF NOT EXISTS items ---
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            item_id TEXT PRIMARY KEY,
            access_token TEXT NOT NULL,
            institution_id TEXT,
            institution_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    #   --- CREATE TABLE IF NOT EXISTS accounts ---
    conn.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            account_id TEXT PRIMARY KEY,
            item_id TEXT NOT NULL REFERENCES items(item_id),
            name TEXT NOT NULL,
            official_name TEXT,
            type TEXT,
            subtype TEXT,
            mask TEXT
        )
    ''')

    #   --- CREATE TABLE IF NOT EXISTS transactions ---
    conn.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL REFERENCES accounts(account_id),
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            name TEXT NOT NULL,
            merchant_name TEXT,
            pending INTEGER NOT NULL DEFAULT 0,
            iso_currency_code TEXT DEFAULT 'USD',
            payment_channel TEXT,
            synced_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    #   --- CREATE TABLE IF NOT EXISTS sync_state ---
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sync_state (
            item_id TEXT PRIMARY KEY REFERENCES items(item_id),
            cursor TEXT NOT NULL,
            last_synced_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    #   --- Commit and return connection ---
    conn.commit()
    return conn
