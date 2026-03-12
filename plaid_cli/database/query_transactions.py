# SPEC: s1-sqlite-database-schema-and-access.md
# PURPOSE: Query transactions with optional filters (year, month, new_since) and account/institution join
# RESPONSIBILITIES: Build SELECT with dynamic WHERE clauses. Join accounts + items for account_name
#   and institution_name. Apply year, month, new_since filters. Order by date DESC. Limit results.
# NOT RESPONSIBLE FOR: Output formatting, display
# DEPENDENCIES: sqlite3 Connection


# --- query_transactions(conn, year=None, month=None, new_since=None, limit=100) → list[dict] ---
def query_transactions(conn, year=None, month=None, new_since=None, limit=100):
    #   --- Validate: if month and not year, raise ValueError ---
    if month and not year:
        raise ValueError("--month requires --year")

    #   --- Base query with JOINs ---
    query = '''
        SELECT t.transaction_id, t.account_id, t.date, t.amount, t.name, t.merchant_name,
               t.pending, t.iso_currency_code, t.payment_channel, t.synced_at,
               a.name AS account_name, i.institution_name
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        JOIN items i ON a.item_id = i.item_id
    '''

    #   --- Build WHERE clauses list + params list ---
    where_clauses = []
    params = []

    #     --- If year: WHERE strftime('%Y', t.date) = ? ---
    if year:
        where_clauses.append("strftime('%Y', t.date) = ?")
        params.append(str(year))

    #     --- If month: WHERE strftime('%m', t.date) = ? (zero-padded) ---
    if month:
        where_clauses.append("strftime('%m', t.date) = ?")
        params.append(str(month).zfill(2))

    #     --- If new_since: WHERE t.synced_at > ? ---
    if new_since:
        where_clauses.append('t.synced_at > ?')
        params.append(new_since)

    #   --- Append WHERE clauses with AND ---
    if where_clauses:
        query += ' WHERE ' + ' AND '.join(where_clauses)

    #   --- ORDER BY t.date DESC ---
    query += ' ORDER BY t.date DESC'

    #   --- LIMIT ? ---
    query += ' LIMIT ?'
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    #   --- Return [dict(row) for row in rows] ---
    return [dict(row) for row in rows]
