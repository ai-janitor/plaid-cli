# SPEC: s1-sqlite-database-schema-and-access.md
# PURPOSE: Persist the sync cursor for an Item
# RESPONSIBILITIES: INSERT OR REPLACE cursor and update last_synced_at. Commit.
# NOT RESPONSIBLE FOR: Deciding when to sync, cursor logic
# DEPENDENCIES: sqlite3 Connection


# --- save_cursor(conn, item_id, cursor) → None ---
def save_cursor(conn, item_id, cursor):
    #   --- INSERT OR REPLACE INTO sync_state ---
    conn.execute(
        'INSERT OR REPLACE INTO sync_state (item_id, cursor, last_synced_at) VALUES (?, ?, CURRENT_TIMESTAMP)',
        (item_id, cursor)
    )
    #   --- conn.commit() ---
    conn.commit()
