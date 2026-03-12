# SPEC: s2-plaid-api-client-and-sync.md
# PURPOSE: Exchange a public_token for an access_token and item_id
# RESPONSIBILITIES: Call item_public_token_exchange, return (access_token, item_id)
# NOT RESPONSIBLE FOR: Storing the token (S1), creating the public token
# DEPENDENCIES: plaid.model.item_public_token_exchange_request

from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest


# --- exchange_token(client, public_token) → (str, str) ---
def exchange_token(client, public_token: str) -> tuple[str, str]:
    #   --- Build ItemPublicTokenExchangeRequest(public_token=public_token) ---
    request = ItemPublicTokenExchangeRequest(public_token=public_token)

    #   --- response = client.item_public_token_exchange(request) ---
    response = client.item_public_token_exchange(request)

    #   --- Return (response['access_token'], response['item_id']) ---
    return (response["access_token"], response["item_id"])
