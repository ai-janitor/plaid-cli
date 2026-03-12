# SPEC: s1-sqlite-database-schema-and-access.md
# PURPOSE: Query accounts, optionally filtered by item_id, with institution name joined
# RESPONSIBILITIES: SELECT accounts JOIN items for institution_name. Optional item_id filter.
# NOT RESPONSIBLE FOR: Display formatting
# DEPENDENCIES: sqlite3 Connection


# --- list_accounts(conn, item_id=None) → list[dict] ---
def list_accounts(conn, item_id=None):
    #   --- Base query with JOIN ---
    query = '''
        SELECT a.account_id, a.item_id, a.name, a.official_name, a.type, a.subtype, a.mask,
               i.institution_name
        FROM accounts a
        JOIN items i ON a.item_id = i.item_id
    '''
    params = []

    #   --- If item_id: add WHERE filter ---
    if item_id:
        query += ' WHERE a.item_id = ?'
        params.append(item_id)

    #   --- ORDER BY institution_name, name ---
    query += ' ORDER BY i.institution_name, a.name'

    rows = conn.execute(query, params).fetchall()
    #   --- Return [dict(row) for row in rows] ---
    return [dict(row) for row in rows]
