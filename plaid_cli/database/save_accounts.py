# SPEC: s1-sqlite-database-schema-and-access.md
# PURPOSE: Insert or replace accounts for an Item
# RESPONSIBILITIES: INSERT OR REPLACE each account dict into accounts table. Commit.
# NOT RESPONSIBLE FOR: Fetching accounts from Plaid (S2)
# DEPENDENCIES: sqlite3 Connection


# --- save_accounts(conn, item_id, accounts: list[dict]) → None ---
def save_accounts(conn, item_id, accounts):
    #   --- For each account in accounts: ---
    for acct in accounts:
        #     --- INSERT OR REPLACE INTO accounts ---
        conn.execute(
            'INSERT OR REPLACE INTO accounts (account_id, item_id, name, official_name, type, subtype, mask) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (acct['account_id'], item_id, acct['name'], acct.get('official_name', ''),
             acct.get('type', ''), acct.get('subtype', ''), acct.get('mask', ''))
        )
    #   --- conn.commit() ---
    conn.commit()
