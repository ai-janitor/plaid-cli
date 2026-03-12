# SPEC: s4-cli-command-handlers.md
# PURPOSE: Handler for `plaid sync` — pull new transactions from Plaid into SQLite
# RESPONSIBILITIES: For each Item (or specified item), call Plaid sync, upsert/remove transactions,
#   save cursor. Report counts. Handle partial failures (one item fails, others continue).
# NOT RESPONSIBLE FOR: Output formatting (S3), Plaid API details (S2)
# DEPENDENCIES: plaid_cli.api (get_plaid_client, sync_transactions),
#   plaid_cli.database (list_items, get_item, get_cursor, upsert_transactions, remove_transactions, save_cursor)

import plaid
from plaid_cli.api import get_plaid_client, sync_transactions
from plaid_cli.database import list_items, get_item, get_cursor, upsert_transactions, remove_transactions, save_cursor


# --- cmd_sync(args, config, conn) → dict ---
def cmd_sync(args, config, conn):
#   --- client = get_plaid_client(config['client_id'], config['secret'], config['env']) ---
    client = get_plaid_client(config['client_id'], config['secret'], config['env'])
#   --- If args.item: items = [get_item(conn, args.item)] ---
    if getattr(args, 'item', None):
        items = [get_item(conn, args.item)]
#   --- Else: items = list_items(conn) ---
    else:
        items = list_items(conn)
#   --- If no items: return {"items_synced": 0, "added": 0, "modified": 0, "removed": 0, "message": "No items found. Run 'plaid create link' first.", "details": []} ---
    if not items:
        return {
            "items_synced": 0,
            "added": 0,
            "modified": 0,
            "removed": 0,
            "message": "No items found. Run 'plaid create link' first.",
            "details": [],
        }
#   --- total_added, total_modified, total_removed = 0, 0, 0 ---
    total_added, total_modified, total_removed = 0, 0, 0
#   --- details = [] ---
    details = []
#   --- For each item in items: ---
    for item in items:
#     --- Try: ---
        try:
#       --- cursor = get_cursor(conn, item['item_id']) ---
            cursor = get_cursor(conn, item['item_id'])
#       --- added, modified, removed, new_cursor = sync_transactions(client, item['access_token'], cursor) ---
            added, modified, removed, new_cursor = sync_transactions(client, item['access_token'], cursor)
#       --- If added or modified: upsert_transactions(conn, added + modified) ---
            if added or modified:
                upsert_transactions(conn, added + modified)
#       --- If removed: remove_transactions(conn, removed) ---
            if removed:
                remove_transactions(conn, removed)
#       --- save_cursor(conn, item['item_id'], new_cursor) ---
            save_cursor(conn, item['item_id'], new_cursor)
#       --- Track counts, append to details ---
            total_added += len(added)
            total_modified += len(modified)
            total_removed += len(removed)
            details.append({
                "item_id": item['item_id'],
                "institution": item.get('institution_name', ''),
                "added": len(added),
                "modified": len(modified),
                "removed": len(removed),
            })
#     --- Except API error: ---
        except plaid.ApiException as e:
#       --- Append error detail for this item, continue to next ---
            details.append({
                "item_id": item['item_id'],
                "institution": item.get('institution_name', ''),
                "error": str(e),
            })
            continue
#   --- Return {"items_synced": N, "added": total, "modified": total, "removed": total, "details": details} ---
    return {
        "items_synced": len([d for d in details if "error" not in d]),
        "added": total_added,
        "modified": total_modified,
        "removed": total_removed,
        "details": details,
    }
