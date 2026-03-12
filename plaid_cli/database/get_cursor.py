# SPEC: s1-sqlite-database-schema-and-access.md
# PURPOSE: Retrieve the sync cursor for an Item
# RESPONSIBILITIES: SELECT cursor from sync_state. Return string or None.
# NOT RESPONSIBLE FOR: Cursor interpretation, sync logic
# DEPENDENCIES: sqlite3 Connection


# --- get_cursor(conn, item_id) → str | None ---
def get_cursor(conn, item_id):
    #   --- SELECT cursor FROM sync_state WHERE item_id = ? ---
    row = conn.execute('SELECT cursor FROM sync_state WHERE item_id = ?', (item_id,)).fetchone()
    #   --- Return row['cursor'] if found, else None ---
    return row['cursor'] if row else None
