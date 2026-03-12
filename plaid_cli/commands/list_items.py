# SPEC: s4-cli-command-handlers.md
# PURPOSE: Handler for `plaid list items` — show all connected banks
# RESPONSIBILITIES: Query items from DB, return result dict
# NOT RESPONSIBLE FOR: Output formatting (S3)
# DEPENDENCIES: plaid_cli.database (list_items)

from plaid_cli.database import list_items


# --- cmd_list_items(args, config, conn) → dict ---
def cmd_list_items(args, config, conn):
#   --- items = list_items(conn) ---
    items = list_items(conn)
#   --- Return {"count": len(items), "items": items} ---
    return {"count": len(items), "items": items}
