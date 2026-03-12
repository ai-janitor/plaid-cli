# SPEC: s3-cli-router-and-output-formatting.md
# PURPOSE: Format command results for human, JSON, or quiet output modes
# RESPONSIBILITIES: Dispatch to human table, JSON, or quiet formatter based on flags.
#   Human: column-aligned table with headers. JSON: single-line valid JSON. Quiet: one value per line.
# NOT RESPONSIBLE FOR: Generating the data (S4 handlers do that)
# DEPENDENCIES: json

import json


# --- format_output(result: dict, command: str, json_mode: bool, quiet_mode: bool) → str ---
def format_output(result, command, json_mode=False, quiet_mode=False):
#   --- If json_mode (wins over quiet): ---
    if json_mode:
#     --- Return json.dumps(result) ---
        return json.dumps(result)

#   --- If quiet_mode: ---
    if quiet_mode:
#     --- Dispatch by command: ---
#       --- "list_items": one item_id per line ---
        if command == "list_items":
            items = result.get("items", [])
            return "\n".join(str(item.get("item_id", "")) for item in items)
#       --- "list_accounts": one account_id per line ---
        elif command == "list_accounts":
            accounts = result.get("accounts", [])
            return "\n".join(str(acct.get("account_id", "")) for acct in accounts)
#       --- "get_transactions": one transaction_id per line ---
        elif command == "get_transactions":
            transactions = result.get("transactions", [])
            return "\n".join(str(txn.get("transaction_id", "")) for txn in transactions)
#       --- "sync": "added:N modified:N removed:N" ---
        elif command == "sync":
            added = result.get("added", 0)
            modified = result.get("modified", 0)
            removed = result.get("removed", 0)
            return f"added:{added} modified:{modified} removed:{removed}"
#       --- "create_link": item_id ---
        elif command == "create_link":
            return str(result.get("item_id", ""))
        return ""

#   --- Else (human mode): ---
#     --- Dispatch by command: ---
#       --- "list_items": table with ITEM_ID, INSTITUTION, CREATED columns ---
    if command == "list_items":
        headers = ["ITEM_ID", "INSTITUTION", "CREATED"]
        rows = []
        for item in result.get("items", []):
            rows.append([
                str(item.get("item_id", "")),
                str(item.get("institution", "")),
                str(item.get("created", "")),
            ])
        return _format_table(headers, rows)

#       --- "list_accounts": table with ACCOUNT_ID, NAME, TYPE, SUBTYPE, MASK, INSTITUTION columns ---
    elif command == "list_accounts":
        headers = ["ACCOUNT_ID", "NAME", "TYPE", "SUBTYPE", "MASK", "INSTITUTION"]
        rows = []
        for acct in result.get("accounts", []):
            rows.append([
                str(acct.get("account_id", "")),
                str(acct.get("name", "")),
                str(acct.get("type", "")),
                str(acct.get("subtype", "")),
                str(acct.get("mask", "")),
                str(acct.get("institution", "")),
            ])
        return _format_table(headers, rows)

#       --- "get_transactions": table with DATE, AMOUNT, ACCOUNT, NAME columns ---
    elif command == "get_transactions":
        headers = ["DATE", "AMOUNT", "ACCOUNT", "NAME"]
        rows = []
        for txn in result.get("transactions", []):
            rows.append([
                str(txn.get("date", "")),
                str(txn.get("amount", "")),
                str(txn.get("account", "")),
                str(txn.get("name", "")),
            ])
        return _format_table(headers, rows)

#       --- "sync": summary "Synced N items: +added, ~modified, -removed" with per-item details ---
    elif command == "sync":
        added = result.get("added", 0)
        modified = result.get("modified", 0)
        removed = result.get("removed", 0)
        total = result.get("items_synced", added + modified + removed)
        lines = [f"Synced {total} items: +{added}, ~{modified}, -{removed}"]
        for detail in result.get("details", []):
            lines.append(f"  {detail}")
        return "\n".join(lines)

#       --- "create_link": "Connected to <institution>. Item ID: <id>. Accounts: ..." ---
    elif command == "create_link":
        institution = result.get("institution", "unknown")
        item_id = result.get("item_id", "unknown")
        accounts = result.get("accounts", [])
        acct_names = ", ".join(str(a.get("name", a)) if isinstance(a, dict) else str(a) for a in accounts)
        line = f"Connected to {institution}. Item ID: {item_id}."
        if acct_names:
            line += f" Accounts: {acct_names}"
        return line

    return str(result)


# --- _format_table(headers: list[str], rows: list[list[str]]) → str ---
def _format_table(headers, rows):
#   --- Calculate column widths from headers and data ---
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(cell))

#   --- Format header row with padding ---
    header_line = "  ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    lines = [header_line]

#   --- Format each data row with padding ---
    for row in rows:
        row_line = "  ".join(
            (row[i] if i < len(row) else "").ljust(col_widths[i])
            for i in range(len(headers))
        )
        lines.append(row_line)

#   --- Return joined lines ---
    return "\n".join(lines)
