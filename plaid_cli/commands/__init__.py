# SPEC: s4-cli-command-handlers.md
# PURPOSE: Commands package — re-export all handler functions
# RESPONSIBILITIES: Provide single import point for command handlers
# NOT RESPONSIBLE FOR: Implementation details
# DEPENDENCIES: All command submodules

from plaid_cli.commands.create_link import cmd_create_link
from plaid_cli.commands.list_items import cmd_list_items
from plaid_cli.commands.list_accounts import cmd_list_accounts
from plaid_cli.commands.get_transactions import cmd_get_transactions
from plaid_cli.commands.sync_transactions import cmd_sync
from plaid_cli.commands.configure import cmd_configure

__all__ = [
    "cmd_create_link",
    "cmd_list_items",
    "cmd_list_accounts",
    "cmd_get_transactions",
    "cmd_sync",
    "cmd_configure",
]
