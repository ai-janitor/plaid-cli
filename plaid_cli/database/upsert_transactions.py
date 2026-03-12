# SPEC: s1-sqlite-database-schema-and-access.md
# PURPOSE: Insert or replace transactions (handles both 'added' and 'modified' from Plaid sync)
# RESPONSIBILITIES: INSERT OR REPLACE each transaction dict. Set synced_at to current time. Commit. Return count.
# NOT RESPONSIBLE FOR: Fetching transactions from Plaid (S2), removed transactions
# DEPENDENCIES: sqlite3 Connection

from datetime import datetime, timezone


# --- upsert_transactions(conn, transactions: list[dict]) → int ---
def upsert_transactions(conn, transactions):
    #   --- synced_at = current UTC timestamp ISO 8601 ---
    synced_at = datetime.now(timezone.utc).isoformat()

    #   --- For each txn in transactions: ---
    for txn in transactions:
        #     --- INSERT OR REPLACE INTO transactions ---
        conn.execute(
            '''INSERT OR REPLACE INTO transactions
               (transaction_id, account_id, date, amount, name, merchant_name,
                pending, iso_currency_code, payment_channel, synced_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (txn['transaction_id'], txn['account_id'], str(txn['date']),
             txn['amount'], txn['name'], txn.get('merchant_name', ''),
             1 if txn.get('pending') else 0, txn.get('iso_currency_code', 'USD'),
             txn.get('payment_channel', ''), synced_at)
        )

    #   --- conn.commit() ---
    conn.commit()
    #   --- Return len(transactions) ---
    return len(transactions)
