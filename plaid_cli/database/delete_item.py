# SPEC: s1-sqlite-database-schema-and-access.md
# PURPOSE: Delete an Item and cascade to accounts, transactions, sync_state
# RESPONSIBILITIES: Delete item and all related data in correct order. Commit.
# NOT RESPONSIBLE FOR: Revoking Plaid access token (API concern)
# DEPENDENCIES: sqlite3 Connection


# --- delete_item(conn, item_id) → None ---
def delete_item(conn, item_id):
    #   --- DELETE FROM transactions WHERE account_id IN (SELECT account_id FROM accounts WHERE item_id = ?) ---
    conn.execute(
        'DELETE FROM transactions WHERE account_id IN (SELECT account_id FROM accounts WHERE item_id = ?)',
        (item_id,)
    )
    #   --- DELETE FROM accounts WHERE item_id = ? ---
    conn.execute('DELETE FROM accounts WHERE item_id = ?', (item_id,))
    #   --- DELETE FROM sync_state WHERE item_id = ? ---
    conn.execute('DELETE FROM sync_state WHERE item_id = ?', (item_id,))
    #   --- DELETE FROM items WHERE item_id = ? ---
    conn.execute('DELETE FROM items WHERE item_id = ?', (item_id,))
    #   --- conn.commit() ---
    conn.commit()
