# SPEC: s1-sqlite-database-schema-and-access.md
# PURPOSE: Query all Items from the items table
# RESPONSIBILITIES: SELECT all items, return as list of dicts
# NOT RESPONSIBLE FOR: Filtering, display formatting
# DEPENDENCIES: sqlite3 Connection


# --- list_items(conn) → list[dict] ---
def list_items(conn):
    #   --- SELECT all items ORDER BY created_at ---
    rows = conn.execute(
        'SELECT item_id, access_token, institution_id, institution_name, created_at FROM items ORDER BY created_at'
    ).fetchall()
    #   --- Return [dict(row) for row in rows] ---
    return [dict(row) for row in rows]
