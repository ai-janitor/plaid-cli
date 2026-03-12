# SPEC: s3-cli-router-and-output-formatting.md
# PURPOSE: CLI entry point — argparse verb-noun command tree, global flag parsing, dispatch
# RESPONSIBILITIES: Build argument parser with verb-noun subcommands (create, list, get, sync).
#   Parse global flags (--json, --quiet). Load config. Open DB connection. Dispatch to
#   command handlers. Catch errors and format output. Set exit codes.
# NOT RESPONSIBLE FOR: Command logic (S4), output formatting (output/), API calls (S2), DB queries (S1)
# DEPENDENCIES: plaid_cli.config.load_config, plaid_cli.commands.*, plaid_cli.output.format_output,
#   plaid_cli.output.format_error, plaid_cli.database.connect

import argparse
import sys

import plaid

from plaid_cli.config import load_config
from plaid_cli.commands import cmd_create_link, cmd_list_items, cmd_list_accounts, cmd_get_transactions, cmd_sync
from plaid_cli.output import format_output, format_error
from plaid_cli.database import get_connection


# --- Build root parser with --json, --quiet, --help ---
def _build_parser():
    parser = argparse.ArgumentParser(prog="plaid", description="Plaid CLI — manage bank connections and transactions. Use --json or -q/--quiet on any subcommand.")

    subparsers = parser.add_subparsers(dest="verb")

#   --- Shared parent parser for global flags (--json, --quiet) inherited by all leaf parsers ---
    global_flags = argparse.ArgumentParser(add_help=False)
    global_flags.add_argument("--json", action="store_true", default=False, help="Output as JSON")
    global_flags.add_argument("-q", "--quiet", action="store_true", default=False, help="Quiet output (IDs only)")

# --- Add 'create' verb subparser ---
    create_parser = subparsers.add_parser("create", help="Create resources")
    create_sub = create_parser.add_subparsers(dest="noun")
#   --- Add 'link' noun with --institution flag ---
    link_parser = create_sub.add_parser("link", help="Connect a new bank in sandbox mode", parents=[global_flags])
    link_parser.add_argument("--institution", default=None, help="Institution ID (default: ins_109508)")
    link_parser.set_defaults(func=cmd_create_link, command="create_link")

# --- Add 'list' verb subparser ---
    list_parser = subparsers.add_parser("list", help="List resources")
    list_sub = list_parser.add_subparsers(dest="noun")
#   --- Add 'items' noun ---
    items_parser = list_sub.add_parser("items", help="Show all connected banks", parents=[global_flags])
    items_parser.set_defaults(func=cmd_list_items, command="list_items")
#   --- Add 'accounts' noun with --item flag ---
    accounts_parser = list_sub.add_parser("accounts", help="Show all accounts", parents=[global_flags])
    accounts_parser.add_argument("--item", default=None, help="Filter by item ID")
    accounts_parser.set_defaults(func=cmd_list_accounts, command="list_accounts")

# --- Add 'get' verb subparser ---
    get_parser = subparsers.add_parser("get", help="Get resources")
    get_sub = get_parser.add_subparsers(dest="noun")
#   --- Add 'transactions' noun with --year, --month, --new, --limit flags ---
    txn_parser = get_sub.add_parser("transactions", help="Query stored transactions", parents=[global_flags])
    txn_parser.add_argument("--year", type=int, default=None, help="Filter by year")
    txn_parser.add_argument("--month", type=int, default=None, help="Filter by month (requires --year)")
    txn_parser.add_argument("--new", action="store_true", default=False, help="Show only transactions from latest sync")
    txn_parser.add_argument("--limit", type=int, default=50, help="Max results (default: 50)")
    txn_parser.set_defaults(func=cmd_get_transactions, command="get_transactions")

# --- Add 'sync' verb subparser with --item flag ---
    sync_parser = subparsers.add_parser("sync", help="Pull new transactions from Plaid", parents=[global_flags])
    sync_parser.add_argument("--item", default=None, help="Sync specific item ID only")
    sync_parser.set_defaults(func=cmd_sync, command="sync")

    return parser


def main():
    parser = _build_parser()

# --- Parse args ---
    args = parser.parse_args()

# --- If no verb: print help, exit 2 ---
    if not args.verb:
        parser.print_help()
        sys.exit(2)

    json_mode = getattr(args, "json", False)
    quiet_mode = getattr(args, "quiet", False)

# --- If verb but no noun (where required): print verb help, exit 2 ---
    if args.verb in ("create", "list", "get") and not getattr(args, "noun", None):
        # Find the verb subparser and print its help
        parser.parse_args([args.verb, "--help"])
        sys.exit(2)

# --- Load config via cascade: args > env > config file > defaults ---
    config = load_config(args)

    # --- Missing credentials: format error with hint, exit 1 ---
    if not config.get("client_id") or not config.get("secret"):
        output = format_error(
            "Missing Plaid credentials.",
            hint="Set PLAID_CLIENT_ID and PLAID_SECRET environment variables, or add them to ~/.config/plaid/config.yaml",
            json_mode=json_mode,
        )
        if output:
            print(output)
        sys.exit(1)

# --- Open DB connection ---
    conn = None
    try:
        conn = get_connection(config["db_path"])

# --- Try: dispatch to handler via args.func(args, config, conn) ---
        result = args.func(args, config, conn)

# --- Format result via output module (human/json/quiet based on flags) ---
        command = getattr(args, "command", "")
        output = format_output(result, command, json_mode=json_mode, quiet_mode=quiet_mode)
        if output:
            print(output)

# --- Except usage error: format error, exit 2 ---
    except ValueError as e:
        output = format_error(str(e), json_mode=json_mode)
        if output:
            print(output)
        sys.exit(2)

# --- Except runtime error: format error, exit 1 ---
    except plaid.ApiException as e:
        output = format_error(str(e), json_mode=json_mode)
        if output:
            print(output)
        sys.exit(1)

# --- Finally: close DB connection ---
    finally:
        if conn:
            conn.close()
