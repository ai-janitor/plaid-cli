# SPEC: s2-plaid-api-client-and-sync.md
# PURPOSE: API package — re-export all public functions
# RESPONSIBILITIES: Provide single import point for Plaid API functions
# NOT RESPONSIBLE FOR: Implementation details
# DEPENDENCIES: All api submodules

from plaid_cli.api.get_plaid_client import get_plaid_client
from plaid_cli.api.create_sandbox_link import create_sandbox_link
from plaid_cli.api.exchange_token import exchange_token
from plaid_cli.api.fetch_accounts import fetch_accounts
from plaid_cli.api.fetch_institution import fetch_institution
from plaid_cli.api.sync_transactions import sync_transactions

__all__ = [
    "get_plaid_client",
    "create_sandbox_link",
    "exchange_token",
    "fetch_accounts",
    "fetch_institution",
    "sync_transactions",
]
