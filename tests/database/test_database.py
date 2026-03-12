# SPEC: s1-sqlite-database-schema-and-access.md
# PURPOSE: Test all database functions against a temporary SQLite DB
# RESPONSIBILITIES: Test schema creation, CRUD operations, query filters, cascade delete, edge cases
# NOT RESPONSIBLE FOR: Testing Plaid API, CLI output
# DEPENDENCIES: pytest, tempfile, plaid_cli.database

import pytest
import tempfile
import os

from plaid_cli.database import (
    get_connection,
    save_item,
    list_items,
    get_item,
    delete_item,
    save_accounts,
    list_accounts,
    upsert_transactions,
    remove_transactions,
    query_transactions,
    save_cursor,
    get_cursor,
    get_last_synced_at,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def db(tmp_path):
    """Return an open connection to a temporary SQLite database."""
    db_path = str(tmp_path / "test.db")
    conn = get_connection(db_path)
    yield conn
    conn.close()


# ---------------------------------------------------------------------------
# Helpers — seed common rows so individual tests stay focused
# ---------------------------------------------------------------------------

def _item(conn, item_id="item-1", access_token="tok-1",
          institution_id="ins-1", institution_name="First Bank"):
    save_item(conn, item_id, access_token, institution_id, institution_name)


def _account(conn, account_id="acct-1", item_id="item-1",
             name="Checking", **kw):
    save_accounts(conn, item_id, [{"account_id": account_id, "name": name, **kw}])


def _txn(conn, transaction_id="txn-1", account_id="acct-1",
         date="2024-03-15", amount=42.0, name="Coffee Shop", **kw):
    upsert_transactions(conn, [{
        "transaction_id": transaction_id,
        "account_id": account_id,
        "date": date,
        "amount": amount,
        "name": name,
        **kw,
    }])


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

# --- Test: get_connection creates all tables ---
def test_get_connection_creates_all_tables(db):
    # Query sqlite_master for each expected table name
    tables = {
        row["name"]
        for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    # Assert items, accounts, transactions, sync_state all exist
    assert "items" in tables
    assert "accounts" in tables
    assert "transactions" in tables
    assert "sync_state" in tables


# --- Test: save_item inserts new item ---
def test_save_item_inserts_new_item(db):
    # Call save_item with a fresh item_id
    save_item(db, "item-A", "tok-A", "ins-A", "Alpha Bank")
    # Query items table directly and assert one row exists with correct fields
    row = db.execute("SELECT * FROM items WHERE item_id = 'item-A'").fetchone()
    assert row is not None
    assert row["access_token"] == "tok-A"
    assert row["institution_id"] == "ins-A"
    assert row["institution_name"] == "Alpha Bank"


# --- Test: save_item replaces existing item ---
def test_save_item_replaces_existing_item(db):
    # Insert an item, then call save_item again with the same item_id but different values
    save_item(db, "item-A", "tok-A", "ins-A", "Alpha Bank")
    save_item(db, "item-A", "tok-A-new", "ins-A", "Alpha Bank Updated")
    # Assert only one row exists and it has the updated values
    rows = db.execute("SELECT * FROM items WHERE item_id = 'item-A'").fetchall()
    assert len(rows) == 1
    assert rows[0]["access_token"] == "tok-A-new"
    assert rows[0]["institution_name"] == "Alpha Bank Updated"


# --- Test: list_items returns all items ---
def test_list_items_returns_all_items(db):
    # Insert two items
    save_item(db, "item-1", "tok-1", "ins-1", "First Bank")
    save_item(db, "item-2", "tok-2", "ins-2", "Second Bank")
    # Call list_items and assert result has length 2 and correct item_ids
    items = list_items(db)
    assert len(items) == 2
    ids = {i["item_id"] for i in items}
    assert ids == {"item-1", "item-2"}


# --- Test: list_items returns empty list when no items ---
def test_list_items_returns_empty_list_when_no_items(db):
    # Call list_items on empty DB
    items = list_items(db)
    # Assert result is an empty list
    assert items == []


# --- Test: get_item returns item by id ---
def test_get_item_returns_item_by_id(db):
    # Insert an item, call get_item with its id
    save_item(db, "item-1", "tok-1", "ins-1", "First Bank")
    item = get_item(db, "item-1")
    # Assert result is a dict with the correct item_id and access_token
    assert item is not None
    assert item["item_id"] == "item-1"
    assert item["access_token"] == "tok-1"


# --- Test: get_item returns None for missing id ---
def test_get_item_returns_none_for_missing_id(db):
    # Call get_item with a non-existent item_id
    result = get_item(db, "does-not-exist")
    # Assert result is None
    assert result is None


# --- Test: delete_item cascades to accounts, transactions, sync_state ---
def test_delete_item_cascades(db):
    # Insert item → account → transaction → cursor
    _item(db)
    _account(db)
    _txn(db)
    save_cursor(db, "item-1", "cursor-abc")

    # Call delete_item
    delete_item(db, "item-1")

    # Assert items table has no row for item-1
    assert db.execute("SELECT * FROM items WHERE item_id='item-1'").fetchone() is None
    # Assert accounts table has no rows for item-1
    assert db.execute("SELECT * FROM accounts WHERE item_id='item-1'").fetchone() is None
    # Assert transactions table has no rows for the account
    assert db.execute("SELECT * FROM transactions WHERE account_id='acct-1'").fetchone() is None
    # Assert sync_state table has no row for item-1
    assert db.execute("SELECT * FROM sync_state WHERE item_id='item-1'").fetchone() is None


# --- Test: save_accounts inserts accounts ---
def test_save_accounts_inserts_accounts(db):
    # Insert parent item first
    _item(db)
    # Call save_accounts with two account dicts
    save_accounts(db, "item-1", [
        {"account_id": "acct-1", "name": "Checking", "type": "depository"},
        {"account_id": "acct-2", "name": "Savings", "type": "depository"},
    ])
    # Query accounts table and assert both rows exist
    rows = db.execute("SELECT * FROM accounts WHERE item_id='item-1'").fetchall()
    assert len(rows) == 2
    names = {r["name"] for r in rows}
    assert names == {"Checking", "Savings"}


# --- Test: list_accounts returns all with institution_name ---
def test_list_accounts_returns_all_with_institution_name(db):
    # Insert item and accounts
    _item(db)
    _account(db)
    # Call list_accounts without filter
    accounts = list_accounts(db)
    # Assert result includes institution_name from the joined items row
    assert len(accounts) == 1
    assert accounts[0]["institution_name"] == "First Bank"
    assert accounts[0]["account_id"] == "acct-1"


# --- Test: list_accounts filters by item_id ---
def test_list_accounts_filters_by_item_id(db):
    # Insert two items and one account each
    save_item(db, "item-1", "tok-1", "ins-1", "First Bank")
    save_item(db, "item-2", "tok-2", "ins-2", "Second Bank")
    save_accounts(db, "item-1", [{"account_id": "acct-1", "name": "Checking"}])
    save_accounts(db, "item-2", [{"account_id": "acct-2", "name": "Savings"}])
    # Call list_accounts(item_id="item-1") and assert only item-1's account appears
    result = list_accounts(db, item_id="item-1")
    assert len(result) == 1
    assert result[0]["account_id"] == "acct-1"


# --- Test: upsert_transactions inserts new ---
def test_upsert_transactions_inserts_new(db):
    # Set up item and account
    _item(db)
    _account(db)
    # Call upsert_transactions with one new transaction dict
    count = upsert_transactions(db, [{
        "transaction_id": "txn-1",
        "account_id": "acct-1",
        "date": "2024-03-15",
        "amount": 9.99,
        "name": "Latte",
    }])
    # Assert return value is 1
    assert count == 1
    # Assert the row exists in the transactions table
    row = db.execute("SELECT * FROM transactions WHERE transaction_id='txn-1'").fetchone()
    assert row is not None
    assert row["amount"] == 9.99
    assert row["name"] == "Latte"


# --- Test: upsert_transactions updates existing ---
def test_upsert_transactions_updates_existing(db):
    # Insert item, account, and an initial transaction
    _item(db)
    _account(db)
    _txn(db, transaction_id="txn-1", amount=5.00, name="Old Name")
    # Call upsert_transactions with the same transaction_id but different amount/name
    upsert_transactions(db, [{
        "transaction_id": "txn-1",
        "account_id": "acct-1",
        "date": "2024-03-15",
        "amount": 99.99,
        "name": "New Name",
    }])
    # Assert only one row exists and it has the updated values
    rows = db.execute("SELECT * FROM transactions WHERE transaction_id='txn-1'").fetchall()
    assert len(rows) == 1
    assert rows[0]["amount"] == 99.99
    assert rows[0]["name"] == "New Name"


# --- Test: remove_transactions deletes by id ---
def test_remove_transactions_deletes_by_id(db):
    # Insert item, account, and two transactions
    _item(db)
    _account(db)
    _txn(db, transaction_id="txn-1")
    _txn(db, transaction_id="txn-2", amount=7.00, name="Tea")
    # Call remove_transactions with one id
    count = remove_transactions(db, ["txn-1"])
    # Assert return value is 1
    assert count == 1
    # Assert that transaction is gone and the other still exists
    assert db.execute("SELECT * FROM transactions WHERE transaction_id='txn-1'").fetchone() is None
    assert db.execute("SELECT * FROM transactions WHERE transaction_id='txn-2'").fetchone() is not None


# --- Test: remove_transactions no-ops on missing id ---
def test_remove_transactions_noops_on_missing_id(db):
    # Call remove_transactions with an id that was never inserted
    count = remove_transactions(db, ["nonexistent-txn"])
    # Assert return value is 0 and no error raised
    assert count == 0


# --- Test: query_transactions filters by year ---
def test_query_transactions_filters_by_year(db):
    # Insert item, account, and transactions in two different years
    _item(db)
    _account(db)
    _txn(db, transaction_id="txn-2024", date="2024-06-01", amount=1.0, name="2024 Txn")
    _txn(db, transaction_id="txn-2023", date="2023-06-01", amount=2.0, name="2023 Txn")
    # Call query_transactions(year=2024)
    results = query_transactions(db, year=2024)
    # Assert only the 2024 transaction is returned
    assert len(results) == 1
    assert results[0]["transaction_id"] == "txn-2024"


# --- Test: query_transactions filters by year+month ---
def test_query_transactions_filters_by_year_and_month(db):
    # Insert item, account, and transactions in different months of the same year
    _item(db)
    _account(db)
    _txn(db, transaction_id="txn-mar", date="2024-03-10", amount=1.0, name="March")
    _txn(db, transaction_id="txn-jul", date="2024-07-20", amount=2.0, name="July")
    # Call query_transactions(year=2024, month=3)
    results = query_transactions(db, year=2024, month=3)
    # Assert only the March transaction is returned
    assert len(results) == 1
    assert results[0]["transaction_id"] == "txn-mar"


# --- Test: query_transactions raises on month without year ---
def test_query_transactions_raises_on_month_without_year(db):
    # Call query_transactions(month=3) without year
    # Assert ValueError is raised
    with pytest.raises(ValueError):
        query_transactions(db, month=3)


# --- Test: query_transactions filters by new_since ---
def test_query_transactions_filters_by_new_since(db):
    # Insert item, account, and a transaction
    _item(db)
    _account(db)
    _txn(db, transaction_id="txn-1", date="2024-01-01", amount=5.0, name="Old")
    # Capture the synced_at of that transaction
    row = db.execute("SELECT synced_at FROM transactions WHERE transaction_id='txn-1'").fetchone()
    first_synced_at = row["synced_at"]

    # Insert a second transaction after a brief moment (ensure synced_at differs)
    import time
    time.sleep(0.01)
    _txn(db, transaction_id="txn-2", date="2024-01-02", amount=6.0, name="New")

    # Call query_transactions(new_since=first_synced_at)
    results = query_transactions(db, new_since=first_synced_at)
    # Assert only the newer transaction is returned
    ids = {r["transaction_id"] for r in results}
    assert "txn-2" in ids
    assert "txn-1" not in ids


# --- Test: query_transactions returns empty on empty db ---
def test_query_transactions_returns_empty_on_empty_db(db):
    # Call query_transactions on an empty database
    results = query_transactions(db)
    # Assert result is an empty list
    assert results == []


# --- Test: query_transactions respects limit ---
def test_query_transactions_respects_limit(db):
    # Insert item, account, and 5 transactions
    _item(db)
    _account(db)
    for i in range(5):
        _txn(db, transaction_id=f"txn-{i}", date=f"2024-01-{i+1:02d}",
             amount=float(i), name=f"Txn {i}")
    # Call query_transactions(limit=3)
    results = query_transactions(db, limit=3)
    # Assert result has exactly 3 items
    assert len(results) == 3


# --- Test: save_cursor and get_cursor round-trip ---
def test_save_cursor_and_get_cursor_round_trip(db):
    # Insert parent item
    _item(db)
    # Call save_cursor with a known cursor string
    save_cursor(db, "item-1", "cursor-xyz-123")
    # Call get_cursor and assert it returns the same string
    result = get_cursor(db, "item-1")
    assert result == "cursor-xyz-123"


# --- Test: get_cursor returns None for missing item ---
def test_get_cursor_returns_none_for_missing_item(db):
    # Call get_cursor with an item_id that has no sync_state row
    result = get_cursor(db, "nonexistent-item")
    # Assert result is None
    assert result is None


# --- Test: get_last_synced_at returns timestamp ---
def test_get_last_synced_at_returns_timestamp(db):
    # Insert item and save a cursor (which sets last_synced_at)
    _item(db)
    save_cursor(db, "item-1", "some-cursor")
    # Call get_last_synced_at and assert it returns a non-None string
    result = get_last_synced_at(db, "item-1")
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0
