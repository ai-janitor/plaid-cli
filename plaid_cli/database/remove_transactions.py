# SPEC: s1-sqlite-database-schema-and-access.md
# PURPOSE: Delete transactions by ID (handles 'removed' from Plaid sync)
# RESPONSIBILITIES: DELETE each transaction_id. Commit. Return count of actually deleted rows.
# NOT RESPONSIBLE FOR: Deciding which transactions to remove (S2 tells us)
# DEPENDENCIES: sqlite3 Connection


# --- remove_transactions(conn, transaction_ids: list[str]) → int ---
def remove_transactions(conn, transaction_ids):
    #   --- count = 0 ---
    count = 0
    #   --- For each tid in transaction_ids: ---
    for tid in transaction_ids:
        #     --- DELETE FROM transactions WHERE transaction_id = ? ---
        cursor = conn.execute('DELETE FROM transactions WHERE transaction_id = ?', (tid,))
        #     --- count += cursor.rowcount ---
        count += cursor.rowcount
    #   --- conn.commit() ---
    conn.commit()
    #   --- Return count ---
    return count
