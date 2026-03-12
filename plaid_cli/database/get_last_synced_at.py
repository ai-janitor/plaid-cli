# SPEC: s1-sqlite-database-schema-and-access.md
# PURPOSE: Retrieve the last sync timestamp for an Item
# RESPONSIBILITIES: SELECT last_synced_at from sync_state. Return string or None.
# NOT RESPONSIBLE FOR: Sync logic, cursor management
# DEPENDENCIES: sqlite3 Connection


# --- get_last_synced_at(conn, item_id) → str | None ---
def get_last_synced_at(conn, item_id):
    #   --- SELECT last_synced_at FROM sync_state WHERE item_id = ? ---
    row = conn.execute('SELECT last_synced_at FROM sync_state WHERE item_id = ?', (item_id,)).fetchone()
    #   --- Return row['last_synced_at'] if found, else None ---
    return row['last_synced_at'] if row else None
