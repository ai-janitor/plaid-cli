# SPEC: s2-plaid-api-client-and-sync.md
# PURPOSE: Create a configured Plaid API client from credentials
# RESPONSIBILITIES: Map env string to plaid.Environment, build Configuration, return PlaidApi instance
# NOT RESPONSIBLE FOR: Reading env vars or config files (caller provides credentials)
# DEPENDENCIES: plaid, plaid.api.plaid_api

import plaid
from plaid.api import plaid_api


# --- get_plaid_client(client_id, secret, env="sandbox") → PlaidApi ---
def get_plaid_client(client_id: str, secret: str, env: str = "sandbox") -> plaid_api.PlaidApi:
    #   --- Map env to host: {"sandbox": Sandbox, "development": Development, "production": Production} ---
    env_map = {
        "sandbox": plaid.Environment.Sandbox,
        "production": plaid.Environment.Production,
    }
    if env not in env_map:
        raise ValueError(f"Unknown Plaid environment: {env}. Use 'sandbox' or 'production'.")
    host = env_map[env]

    #   --- Build plaid.Configuration(host=host, api_key={"clientId": client_id, "secret": secret}) ---
    configuration = plaid.Configuration(
        host=host,
        api_key={"clientId": client_id, "secret": secret},
    )

    #   --- Create ApiClient(configuration) ---
    api_client = plaid.ApiClient(configuration)

    #   --- Return PlaidApi(api_client) ---
    return plaid_api.PlaidApi(api_client)
