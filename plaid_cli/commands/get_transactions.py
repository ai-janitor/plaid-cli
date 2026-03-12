# SPEC: s4-cli-command-handlers.md
# PURPOSE: Handler for `plaid get transactions` — query stored transactions with filters
# RESPONSIBILITIES: Build query params from args, call query_transactions, return result dict.
#   Handle --new flag by finding the earliest last_synced_at before most recent sync.
# NOT RESPONSIBLE FOR: Output formatting (S3), pulling from Plaid (that's sync)
# DEPENDENCIES: plaid_cli.database (query_transactions, list_items, get_last_synced_at)

from plaid_cli.database import query_transactions, list_items, get_last_synced_at


# --- cmd_get_transactions(args, config, conn) → dict ---
def cmd_get_transactions(args, config, conn):
#   --- year = getattr(args, 'year', None) ---
    year = getattr(args, 'year', None)
#   --- month = getattr(args, 'month', None) ---
    month = getattr(args, 'month', None)
#   --- new_since = None ---
    new_since = None
#   --- If getattr(args, 'new', False): ---
    if getattr(args, 'new', False):
#     --- Get all items from DB ---
        items = list_items(conn)
#     --- Find the minimum last_synced_at across all items (the sync before the most recent) ---
        synced_times = []
        for item in items:
            ts = get_last_synced_at(conn, item['item_id'])
            if ts is not None:
                synced_times.append(ts)
#     --- If found: new_since = that timestamp ---
        if synced_times:
            new_since = min(synced_times)
#   --- If month: format as zero-padded string ---
    if month:
        month = str(month).zfill(2)
#   --- limit = getattr(args, 'limit', 50) ---
    limit = getattr(args, 'limit', 50)
#   --- transactions = query_transactions(conn, year=year, month=month, new_since=new_since, limit=limit) ---
    transactions = query_transactions(conn, year=year, month=month, new_since=new_since, limit=limit)
#   --- Return {"count": len(transactions), "transactions": transactions} ---
    return {"count": len(transactions), "transactions": transactions}
