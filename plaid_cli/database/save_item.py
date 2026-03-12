# SPEC: s1-sqlite-database-schema-and-access.md
# PURPOSE: Insert or replace an Item (bank connection) in the items table
# RESPONSIBILITIES: INSERT OR REPLACE into items table. Commit.
# NOT RESPONSIBLE FOR: Fetching item data from Plaid (S2), account storage
# DEPENDENCIES: sqlite3 Connection


# --- save_item(conn, item_id, access_token, institution_id, institution_name) → None ---
def save_item(conn, item_id, access_token, institution_id, institution_name):
    #   --- INSERT OR REPLACE INTO items ---
    conn.execute(
        'INSERT OR REPLACE INTO items (item_id, access_token, institution_id, institution_name) VALUES (?, ?, ?, ?)',
        (item_id, access_token, institution_id, institution_name)
    )
    #   --- conn.commit() ---
    conn.commit()
