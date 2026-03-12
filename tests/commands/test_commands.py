# SPEC: s4-cli-command-handlers.md
# PURPOSE: Test command handlers with mocked API and real DB
# RESPONSIBILITIES: Test each handler's orchestration logic, result dict shape, edge cases
# NOT RESPONSIBLE FOR: Testing API calls directly, testing output formatting
# DEPENDENCIES: pytest, unittest.mock, tempfile, plaid_cli.commands, plaid_cli.database

import argparse
import pytest
from unittest.mock import MagicMock, patch
from plaid_cli.database.connect import get_connection
from plaid_cli.database.save_item import save_item
from plaid_cli.database.save_accounts import save_accounts
from plaid_cli.database.upsert_transactions import upsert_transactions
from plaid_cli.database.save_cursor import save_cursor
from plaid_cli.commands import (
    cmd_create_link,
    cmd_list_items,
    cmd_list_accounts,
    cmd_get_transactions,
    cmd_sync,
)

FAKE_CONFIG = {
    "client_id": "test_client_id",
    "secret": "test_secret",
    "env": "sandbox",
}

FAKE_ITEM_ID = "item_abc123"
FAKE_ACCESS_TOKEN = "access-sandbox-abc123"
FAKE_INSTITUTION_ID = "ins_109508"
FAKE_INSTITUTION_NAME = "Chase"

FAKE_ACCOUNTS = [
    {
        "account_id": "acct_001",
        "name": "Checking",
        "official_name": "Chase Total Checking",
        "type": "depository",
        "subtype": "checking",
        "mask": "0001",
    },
    {
        "account_id": "acct_002",
        "name": "Savings",
        "official_name": "Chase Savings",
        "type": "depository",
        "subtype": "savings",
        "mask": "0002",
    },
]

FAKE_TRANSACTIONS = [
    {
        "transaction_id": "txn_001",
        "account_id": "acct_001",
        "date": "2024-03-15",
        "amount": 42.50,
        "name": "Coffee Shop",
        "merchant_name": "Starbucks",
        "pending": False,
        "iso_currency_code": "USD",
        "payment_channel": "in store",
    },
    {
        "transaction_id": "txn_002",
        "account_id": "acct_001",
        "date": "2024-04-10",
        "amount": 100.00,
        "name": "Grocery Store",
        "merchant_name": "Whole Foods",
        "pending": False,
        "iso_currency_code": "USD",
        "payment_channel": "in store",
    },
]


@pytest.fixture
def db(tmp_path):
    """Create a real temporary SQLite DB with schema."""
    conn = get_connection(str(tmp_path / "sub" / "test.db"))
    yield conn
    conn.close()


@pytest.fixture
def db_with_item(db):
    """DB pre-populated with one item and its accounts."""
    save_item(db, FAKE_ITEM_ID, FAKE_ACCESS_TOKEN, FAKE_INSTITUTION_ID, FAKE_INSTITUTION_NAME)
    save_accounts(db, FAKE_ITEM_ID, FAKE_ACCOUNTS)
    return db


@pytest.fixture
def db_with_transactions(db_with_item):
    """DB pre-populated with item, accounts, and transactions."""
    upsert_transactions(db_with_item, FAKE_TRANSACTIONS)
    return db_with_item


# --- Test: cmd_create_link saves item and accounts, returns correct dict ---
def test_cmd_create_link_saves_item_and_accounts(db):
    # Arrange fake return values for each API call
    fake_client = MagicMock()
    fake_public_token = "public-sandbox-token-xyz"
    fake_institution = {"name": FAKE_INSTITUTION_NAME}

    with patch("plaid_cli.commands.create_link.get_plaid_client", return_value=fake_client) as mock_client, \
         patch("plaid_cli.commands.create_link.create_sandbox_link", return_value=fake_public_token) as mock_create, \
         patch("plaid_cli.commands.create_link.exchange_token", return_value=(FAKE_ACCESS_TOKEN, FAKE_ITEM_ID)) as mock_exchange, \
         patch("plaid_cli.commands.create_link.fetch_institution", return_value=fake_institution) as mock_institution, \
         patch("plaid_cli.commands.create_link.fetch_accounts", return_value=FAKE_ACCOUNTS) as mock_accounts:

        args = argparse.Namespace(institution=FAKE_INSTITUTION_ID)
        result = cmd_create_link(args, FAKE_CONFIG, db)

    # Verify the result dict shape and values
    assert result["item_id"] == FAKE_ITEM_ID
    assert result["institution"] == FAKE_INSTITUTION_NAME
    assert result["accounts"] == FAKE_ACCOUNTS

    # Verify the item was persisted in DB
    rows = db.execute("SELECT * FROM items WHERE item_id = ?", (FAKE_ITEM_ID,)).fetchall()
    assert len(rows) == 1
    assert rows[0]["institution_name"] == FAKE_INSTITUTION_NAME

    # Verify accounts were persisted in DB
    acct_rows = db.execute("SELECT * FROM accounts WHERE item_id = ?", (FAKE_ITEM_ID,)).fetchall()
    assert len(acct_rows) == 2


# --- Test: cmd_list_items returns count and items ---
def test_cmd_list_items_returns_count_and_items(db_with_item):
    args = argparse.Namespace()
    result = cmd_list_items(args, FAKE_CONFIG, db_with_item)

    # Result must have count and items keys
    assert "count" in result
    assert "items" in result
    assert result["count"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0]["item_id"] == FAKE_ITEM_ID
    assert result["items"][0]["institution_name"] == FAKE_INSTITUTION_NAME


# --- Test: cmd_list_items returns empty when no items ---
def test_cmd_list_items_returns_empty_when_no_items(db):
    args = argparse.Namespace()
    result = cmd_list_items(args, FAKE_CONFIG, db)

    assert result["count"] == 0
    assert result["items"] == []


# --- Test: cmd_list_accounts returns all accounts with institution ---
def test_cmd_list_accounts_returns_all_accounts_with_institution(db_with_item):
    args = argparse.Namespace(item=None)
    result = cmd_list_accounts(args, FAKE_CONFIG, db_with_item)

    assert result["count"] == 2
    assert len(result["accounts"]) == 2
    # Each account must include institution_name (joined from items)
    for acct in result["accounts"]:
        assert acct["institution_name"] == FAKE_INSTITUTION_NAME
        assert "account_id" in acct
        assert "name" in acct


# --- Test: cmd_list_accounts filters by item ---
def test_cmd_list_accounts_filters_by_item(db):
    # Insert two items with their accounts
    save_item(db, "item_A", "access-A", "ins_001", "Bank A")
    save_accounts(db, "item_A", [
        {"account_id": "acct_A1", "name": "Checking A", "type": "depository", "subtype": "checking", "mask": "1001"},
    ])
    save_item(db, "item_B", "access-B", "ins_002", "Bank B")
    save_accounts(db, "item_B", [
        {"account_id": "acct_B1", "name": "Checking B", "type": "depository", "subtype": "checking", "mask": "2001"},
        {"account_id": "acct_B2", "name": "Savings B", "type": "depository", "subtype": "savings", "mask": "2002"},
    ])

    # Filter to item_A only — should return 1 account
    args = argparse.Namespace(item="item_A")
    result = cmd_list_accounts(args, FAKE_CONFIG, db)

    assert result["count"] == 1
    assert result["accounts"][0]["account_id"] == "acct_A1"
    assert result["accounts"][0]["institution_name"] == "Bank A"


# --- Test: cmd_get_transactions filters by year ---
def test_cmd_get_transactions_filters_by_year(db_with_transactions):
    # 2024 transactions: txn_001 (March) and txn_002 (April) — both in 2024
    args = argparse.Namespace(year=2024, month=None, new=False, limit=50)
    result = cmd_get_transactions(args, FAKE_CONFIG, db_with_transactions)

    assert result["count"] == 2
    assert len(result["transactions"]) == 2
    # All returned transactions should be from 2024
    for txn in result["transactions"]:
        assert txn["date"].startswith("2024")

    # Filter to a year with no data
    args_empty = argparse.Namespace(year=2020, month=None, new=False, limit=50)
    result_empty = cmd_get_transactions(args_empty, FAKE_CONFIG, db_with_transactions)
    assert result_empty["count"] == 0
    assert result_empty["transactions"] == []


# --- Test: cmd_get_transactions with --new returns recent sync ---
def test_cmd_get_transactions_with_new_returns_recent_sync(db_with_item):
    # Save a cursor (establishes last_synced_at = T1) for existing transactions
    save_cursor(db_with_item, FAKE_ITEM_ID, "cursor_v1")

    # Insert older transactions (synced_at will be whatever upsert_transactions uses)
    old_txns = [
        {
            "transaction_id": "txn_old_001",
            "account_id": "acct_001",
            "date": "2024-01-10",
            "amount": 10.00,
            "name": "Old Coffee",
            "merchant_name": "Old Cafe",
            "pending": False,
        }
    ]
    upsert_transactions(db_with_item, old_txns)

    # Get the current last_synced_at to verify the --new logic uses it as the cutoff
    from plaid_cli.database.get_last_synced_at import get_last_synced_at
    ts = get_last_synced_at(db_with_item, FAKE_ITEM_ID)
    assert ts is not None

    # cmd_get_transactions with --new should call query_transactions with new_since=ts
    # Use a mock on query_transactions to inspect the call
    with patch("plaid_cli.commands.get_transactions.query_transactions") as mock_query:
        mock_query.return_value = []
        args = argparse.Namespace(year=None, month=None, new=True, limit=50)
        result = cmd_get_transactions(args, FAKE_CONFIG, db_with_item)

    mock_query.assert_called_once()
    call_kwargs = mock_query.call_args
    # new_since must be set to the sync timestamp
    assert call_kwargs.kwargs.get("new_since") == ts or call_kwargs.args[3] == ts


# --- Test: cmd_get_transactions with --new and no syncs returns empty ---
def test_cmd_get_transactions_with_new_and_no_syncs_returns_empty(db_with_item):
    # No cursors/sync_state rows exist — new_since should remain None
    with patch("plaid_cli.commands.get_transactions.query_transactions") as mock_query:
        mock_query.return_value = []
        args = argparse.Namespace(year=None, month=None, new=True, limit=50)
        result = cmd_get_transactions(args, FAKE_CONFIG, db_with_item)

    mock_query.assert_called_once()
    call_kwargs = mock_query.call_args
    # new_since must be None (no syncs found)
    passed_new_since = call_kwargs.kwargs.get("new_since")
    if passed_new_since is None and len(call_kwargs.args) >= 4:
        passed_new_since = call_kwargs.args[3]
    assert passed_new_since is None
    assert result["count"] == 0
    assert result["transactions"] == []


# --- Test: cmd_sync syncs all items ---
def test_cmd_sync_syncs_all_items(db_with_item):
    fake_client = MagicMock()
    fake_added = [
        {
            "transaction_id": "txn_new_001",
            "account_id": "acct_001",
            "date": "2024-05-01",
            "amount": 25.00,
            "name": "New Purchase",
            "merchant_name": "Shop",
            "pending": False,
        }
    ]
    fake_modified = []
    fake_removed = []
    fake_new_cursor = "cursor_v2"

    with patch("plaid_cli.commands.sync_transactions.get_plaid_client", return_value=fake_client), \
         patch("plaid_cli.commands.sync_transactions.sync_transactions", return_value=(fake_added, fake_modified, fake_removed, fake_new_cursor)):

        args = argparse.Namespace(item=None)
        result = cmd_sync(args, FAKE_CONFIG, db_with_item)

    assert result["items_synced"] == 1
    assert result["added"] == 1
    assert result["modified"] == 0
    assert result["removed"] == 0
    assert len(result["details"]) == 1
    assert result["details"][0]["item_id"] == FAKE_ITEM_ID
    assert "error" not in result["details"][0]

    # Transaction should be persisted in DB
    txn_rows = db_with_item.execute("SELECT * FROM transactions WHERE transaction_id = 'txn_new_001'").fetchall()
    assert len(txn_rows) == 1

    # Cursor should be updated
    cursor_row = db_with_item.execute("SELECT cursor FROM sync_state WHERE item_id = ?", (FAKE_ITEM_ID,)).fetchone()
    assert cursor_row["cursor"] == fake_new_cursor


# --- Test: cmd_sync with --item syncs one ---
def test_cmd_sync_with_item_syncs_one(db):
    # Set up two items
    save_item(db, "item_X", "access-X", "ins_001", "Bank X")
    save_accounts(db, "item_X", [{"account_id": "acct_X1", "name": "Checking X", "type": "depository", "subtype": "checking", "mask": "X001"}])
    save_item(db, "item_Y", "access-Y", "ins_002", "Bank Y")
    save_accounts(db, "item_Y", [{"account_id": "acct_Y1", "name": "Checking Y", "type": "depository", "subtype": "checking", "mask": "Y001"}])

    fake_client = MagicMock()

    with patch("plaid_cli.commands.sync_transactions.get_plaid_client", return_value=fake_client), \
         patch("plaid_cli.commands.sync_transactions.sync_transactions", return_value=([], [], [], "cursor_X_v1")) as mock_sync:

        args = argparse.Namespace(item="item_X")
        result = cmd_sync(args, FAKE_CONFIG, db)

    # Only one item synced (item_X)
    assert result["items_synced"] == 1
    assert len(result["details"]) == 1
    assert result["details"][0]["item_id"] == "item_X"

    # sync_transactions API called exactly once (not for item_Y)
    assert mock_sync.call_count == 1


# --- Test: cmd_sync with no items returns message ---
def test_cmd_sync_with_no_items_returns_message(db):
    fake_client = MagicMock()

    with patch("plaid_cli.commands.sync_transactions.get_plaid_client", return_value=fake_client):
        args = argparse.Namespace(item=None)
        result = cmd_sync(args, FAKE_CONFIG, db)

    assert result["items_synced"] == 0
    assert result["added"] == 0
    assert result["modified"] == 0
    assert result["removed"] == 0
    assert "message" in result
    assert "plaid create link" in result["message"]
    assert result["details"] == []


# --- Test: cmd_sync partial failure continues remaining ---
def test_cmd_sync_partial_failure_continues_remaining(db):
    # Set up two items
    save_item(db, "item_good", "access-good", "ins_001", "Good Bank")
    save_accounts(db, "item_good", [{"account_id": "acct_good1", "name": "Checking", "type": "depository", "subtype": "checking", "mask": "G001"}])
    save_item(db, "item_bad", "access-bad", "ins_002", "Bad Bank")
    save_accounts(db, "item_bad", [{"account_id": "acct_bad1", "name": "Checking", "type": "depository", "subtype": "checking", "mask": "B001"}])

    fake_client = MagicMock()

    import plaid

    def fake_sync(client, access_token, cursor):
        if access_token == "access-bad":
            raise plaid.ApiException(status=400, reason="ITEM_LOGIN_REQUIRED")
        return ([], [], [], "cursor_good_v1")

    with patch("plaid_cli.commands.sync_transactions.get_plaid_client", return_value=fake_client), \
         patch("plaid_cli.commands.sync_transactions.sync_transactions", side_effect=fake_sync):

        args = argparse.Namespace(item=None)
        result = cmd_sync(args, FAKE_CONFIG, db)

    # items_synced counts only successful ones
    assert result["items_synced"] == 1
    assert len(result["details"]) == 2

    # One detail has error, one does not
    errors = [d for d in result["details"] if "error" in d]
    successes = [d for d in result["details"] if "error" not in d]
    assert len(errors) == 1
    assert len(successes) == 1
    assert errors[0]["item_id"] == "item_bad"
    assert successes[0]["item_id"] == "item_good"
