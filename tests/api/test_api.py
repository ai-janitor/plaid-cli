# SPEC: s2-plaid-api-client-and-sync.md
# PURPOSE: Test Plaid API functions against sandbox
# RESPONSIBILITIES: Test client creation, sandbox link, token exchange, account fetch,
#   institution fetch, transaction sync. Uses real sandbox API calls.
# NOT RESPONSIBLE FOR: Testing DB storage, CLI output
# DEPENDENCIES: pytest, plaid_cli.api

# --- Test: get_plaid_client returns PlaidApi instance ---
# --- Test: create_sandbox_link returns public_token ---
# --- Test: create_sandbox_link with invalid institution raises ---
# --- Test: exchange_token returns access_token and item_id ---
# --- Test: fetch_accounts returns list of account dicts ---
# --- Test: fetch_institution returns institution dict with name ---
# --- Test: sync_transactions returns added/modified/removed/cursor ---
# --- Test: sync_transactions with no changes returns empty lists ---
# --- Test: sync_transactions with invalid token raises ---
