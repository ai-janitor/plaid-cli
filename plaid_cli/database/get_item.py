# SPEC: s1-sqlite-database-schema-and-access.md
# PURPOSE: Query a single Item by item_id
# RESPONSIBILITIES: SELECT one item, return as dict or None
# NOT RESPONSIBLE FOR: Listing all items, item creation
# DEPENDENCIES: sqlite3 Connection


# --- get_item(conn, item_id) → dict | None ---
def get_item(conn, item_id):
    #   --- SELECT * FROM items WHERE item_id = ? ---
    row = conn.execute('SELECT * FROM items WHERE item_id = ?', (item_id,)).fetchone()
    #   --- Return dict(row) if found, else None ---
    return dict(row) if row else None
