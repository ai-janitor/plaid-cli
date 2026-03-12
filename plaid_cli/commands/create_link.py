# SPEC: s4-cli-command-handlers.md
# PURPOSE: Handler for `plaid create link` — connect a new bank in sandbox mode
# RESPONSIBILITIES: Create sandbox public token, exchange for access token, fetch institution
#   and account metadata, save everything to DB. Return result dict.
# NOT RESPONSIBLE FOR: Output formatting (S3), argument parsing (S3)
# DEPENDENCIES: plaid_cli.api (create_sandbox_link, exchange_token, fetch_institution, fetch_accounts, get_plaid_client),
#   plaid_cli.database (save_item, save_accounts)

from plaid_cli.api import get_plaid_client, create_sandbox_link, exchange_token, fetch_institution, fetch_accounts
from plaid_cli.database import save_item, save_accounts


# --- cmd_create_link(args, config, conn) → dict ---
def cmd_create_link(args, config, conn):
#   --- client = get_plaid_client(config['client_id'], config['secret'], config['env']) ---
    client = get_plaid_client(config['client_id'], config['secret'], config['env'])
#   --- institution_id = args.institution or "ins_109508" ---
    institution_id = getattr(args, 'institution', None) or "ins_109508"
#   --- public_token = create_sandbox_link(client, institution_id) ---
    public_token = create_sandbox_link(client, institution_id)
#   --- access_token, item_id = exchange_token(client, public_token) ---
    access_token, item_id = exchange_token(client, public_token)
#   --- institution = fetch_institution(client, institution_id) ---
    institution = fetch_institution(client, institution_id)
#   --- save_item(conn, item_id, access_token, institution_id, institution['name']) ---
    save_item(conn, item_id, access_token, institution_id, institution['name'])
#   --- accounts = fetch_accounts(client, access_token) ---
    accounts = fetch_accounts(client, access_token)
#   --- save_accounts(conn, item_id, accounts) ---
    save_accounts(conn, item_id, accounts)
#   --- Return {"item_id": item_id, "institution": institution['name'], "accounts": accounts} ---
    return {"item_id": item_id, "institution": institution['name'], "accounts": accounts}
