# SPEC: s2-plaid-api-client-and-sync.md
# PURPOSE: Pull transactions from Plaid using /transactions/sync with cursor-based pagination
# RESPONSIBILITIES: Call transactions_sync in a loop while has_more. Accumulate added/modified/removed.
#   Flatten transaction objects into dicts matching S1 schema. Handle empty cursor retry (wait + poll).
# NOT RESPONSIBLE FOR: Storing results (S1), cursor persistence (S1)
# DEPENDENCIES: plaid.model.transactions_sync_request, time

import time

from plaid.model.transactions_sync_request import TransactionsSyncRequest


def _flatten_transaction(txn) -> dict:
    """Flatten a Plaid transaction object into a dict matching the S1 schema."""
    return {
        "transaction_id": txn["transaction_id"],
        "account_id": txn["account_id"],
        "date": str(txn["date"]),
        "amount": txn["amount"],
        "name": txn["name"],
        "merchant_name": txn.get("merchant_name"),
        "pending": bool(txn["pending"]),
        "iso_currency_code": txn.get("iso_currency_code"),
        "payment_channel": txn.get("payment_channel"),
    }


# --- sync_transactions(client, access_token, cursor=None) → (list[dict], list[dict], list[str], str) ---
def sync_transactions(client, access_token: str, cursor: str | None = None) -> tuple[list[dict], list[dict], list[str], str]:
    #   --- added, modified, removed = [], [], [] ---
    added, modified, removed = [], [], []

    #   --- has_more = True ---
    has_more = True
    retries = 0

    #   --- While has_more: ---
    while has_more:
        #     --- Build request kwargs: access_token=access_token ---
        kwargs = {"access_token": access_token}

        #     --- If cursor is not None: add cursor=cursor ---
        if cursor is not None:
            kwargs["cursor"] = cursor

        #     --- Build TransactionsSyncRequest(**kwargs) ---
        request = TransactionsSyncRequest(**kwargs)

        #     --- response = client.transactions_sync(request) ---
        response = client.transactions_sync(request)

        #     --- next_cursor = response['next_cursor'] ---
        next_cursor = response["next_cursor"]

        #     --- If next_cursor is empty string (no data ready): ---
        if next_cursor == "":
            #       --- Wait 2 seconds, retry up to 5 times ---
            retries += 1
            if retries > 5:
                break
            time.sleep(2)
            #       --- Continue loop ---
            continue

        # Reset retries on successful response
        retries = 0

        #     --- For each txn in response['added']: flatten to dict (transaction_id, account_id, date, amount, name, merchant_name, pending, iso_currency_code, payment_channel) ---
        #     --- Extend added with flattened dicts ---
        added.extend(_flatten_transaction(txn) for txn in response["added"])

        #     --- For each txn in response['modified']: flatten same way ---
        #     --- Extend modified with flattened dicts ---
        modified.extend(_flatten_transaction(txn) for txn in response["modified"])

        #     --- For each txn in response['removed']: extract transaction_id ---
        #     --- Extend removed with transaction_id strings ---
        removed.extend(txn["transaction_id"] for txn in response["removed"])

        #     --- cursor = next_cursor ---
        cursor = next_cursor

        #     --- has_more = response['has_more'] ---
        has_more = response["has_more"]

    #   --- Return (added, modified, removed, cursor) ---
    return (added, modified, removed, cursor)
