# SPEC: s4-cli-command-handlers.md
# PURPOSE: Handler for `plaid list accounts` — show all accounts across banks
# RESPONSIBILITIES: Query accounts from DB with optional item_id filter, return result dict
# NOT RESPONSIBLE FOR: Output formatting (S3)
# DEPENDENCIES: plaid_cli.database (list_accounts)

from plaid_cli.database import list_accounts


# --- cmd_list_accounts(args, config, conn) → dict ---
def cmd_list_accounts(args, config, conn):
#   --- item_id = getattr(args, 'item', None) ---
    item_id = getattr(args, 'item', None)
#   --- accounts = list_accounts(conn, item_id=item_id) ---
    accounts = list_accounts(conn, item_id=item_id)
#   --- Return {"count": len(accounts), "accounts": accounts} ---
    return {"count": len(accounts), "accounts": accounts}
