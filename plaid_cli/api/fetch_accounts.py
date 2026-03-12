# SPEC: s2-plaid-api-client-and-sync.md
# PURPOSE: Fetch account metadata for an Item from Plaid
# RESPONSIBILITIES: Call accounts_get, flatten response into list of dicts matching S1 schema
# NOT RESPONSIBLE FOR: Storing accounts (S1)
# DEPENDENCIES: plaid.model.accounts_get_request

from plaid.model.accounts_get_request import AccountsGetRequest


# --- fetch_accounts(client, access_token) → list[dict] ---
def fetch_accounts(client, access_token: str) -> list[dict]:
    #   --- Build AccountsGetRequest(access_token=access_token) ---
    request = AccountsGetRequest(access_token=access_token)

    #   --- response = client.accounts_get(request) ---
    response = client.accounts_get(request)

    #   --- For each account in response['accounts']: ---
    #     --- Extract: account_id, name, official_name, type (str), subtype (str), mask ---
    accounts = []
    for account in response["accounts"]:
        accounts.append({
            "account_id": account["account_id"],
            "name": account["name"],
            "official_name": account.get("official_name"),
            "type": str(account["type"]),
            "subtype": str(account["subtype"]) if account.get("subtype") else None,
            "mask": account.get("mask"),
        })

    #   --- Return list of dicts ---
    return accounts
