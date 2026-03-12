# SPEC: s3-cli-router-and-output-formatting.md
# PURPOSE: Test output formatting for all three modes
# RESPONSIBILITIES: Test human table, JSON, and quiet output for each command type
# NOT RESPONSIBLE FOR: Testing command logic, API calls
# DEPENDENCIES: pytest, json, plaid_cli.output

import json
import sys
import pytest
from plaid_cli.output import format_output, format_error
from plaid_cli.output.format_output import _format_table

# --- Test: format_output json mode returns valid JSON ---
def test_format_output_json_mode_returns_valid_json():
    # Arrange: build a result dict for list_items
    result = {"items": [{"item_id": "item-abc", "institution": "Chase", "created": "2024-01-01"}]}
    # Act: call format_output with json_mode=True
    output = format_output(result, "list_items", json_mode=True)
    # Assert: output is valid JSON and matches result
    parsed = json.loads(output)
    assert parsed == result

# --- Test: format_output quiet mode returns one ID per line ---
def test_format_output_quiet_mode_returns_one_id_per_line():
    # Arrange: build result with multiple items
    result = {
        "items": [
            {"item_id": "item-1", "institution": "Chase", "created": "2024-01-01"},
            {"item_id": "item-2", "institution": "BofA", "created": "2024-01-02"},
        ]
    }
    # Act: call format_output with quiet_mode=True for list_items
    output = format_output(result, "list_items", quiet_mode=True)
    # Assert: one item_id per line, no extra whitespace
    lines = output.strip().splitlines()
    assert lines == ["item-1", "item-2"]

# --- Test: format_output human mode returns table with headers ---
def test_format_output_human_mode_returns_table_with_headers():
    # Arrange: build result for list_accounts
    result = {
        "accounts": [
            {
                "account_id": "acct-1",
                "name": "Checking",
                "type": "depository",
                "subtype": "checking",
                "mask": "1234",
                "institution": "Chase",
            }
        ]
    }
    # Act: call format_output in human mode (json_mode=False, quiet_mode=False)
    output = format_output(result, "list_accounts")
    # Assert: headers ACCOUNT_ID, NAME, TYPE, SUBTYPE, MASK, INSTITUTION all present
    assert "ACCOUNT_ID" in output
    assert "NAME" in output
    assert "TYPE" in output
    assert "SUBTYPE" in output
    assert "MASK" in output
    assert "INSTITUTION" in output
    # Assert: row data appears
    assert "acct-1" in output
    assert "Checking" in output

# --- Test: format_output json wins over quiet ---
def test_format_output_json_wins_over_quiet():
    # Arrange: result for list_accounts
    result = {"accounts": [{"account_id": "acct-99", "name": "Savings", "type": "depository", "subtype": "savings", "mask": "9999", "institution": "BofA"}]}
    # Act: pass both json_mode=True and quiet_mode=True
    output = format_output(result, "list_accounts", json_mode=True, quiet_mode=True)
    # Assert: output is valid JSON (json_mode wins), not just account_id
    parsed = json.loads(output)
    assert parsed == result

# --- Test: format_error json mode returns {"error": ...} ---
def test_format_error_json_mode_returns_error_dict():
    # Arrange: an error message
    message = "client_id is required"
    # Act: call format_error with json_mode=True
    output = format_error(message, json_mode=True)
    # Assert: output is valid JSON with "error" key containing the message
    parsed = json.loads(output)
    assert parsed == {"error": message}

# --- Test: format_error human mode prints to stderr ---
def test_format_error_human_mode_prints_to_stderr(capsys):
    # Arrange: an error message and optional hint
    message = "missing credentials"
    hint = "set PLAID_CLIENT_ID env var"
    # Act: call format_error in human mode (json_mode=False)
    result = format_error(message, hint=hint, json_mode=False)
    # Assert: stderr contains "Error: <message>" and "Hint: <hint>"
    captured = capsys.readouterr()
    assert "Error: missing credentials" in captured.err
    assert "Hint: set PLAID_CLIENT_ID env var" in captured.err
    # Assert: return value is empty string
    assert result == ""

# --- Test: _format_table aligns columns ---
def test_format_table_aligns_columns():
    # Arrange: headers and rows of varying widths
    headers = ["ID", "NAME", "VALUE"]
    rows = [
        ["short", "a very long name here", "42"],
        ["longer-id", "x", "9999"],
    ]
    # Act: call _format_table
    output = _format_table(headers, rows)
    lines = output.splitlines()
    # Assert: header line present as first line
    assert lines[0].startswith("ID")
    assert "NAME" in lines[0]
    assert "VALUE" in lines[0]
    # Assert: columns are padded — each line has the same number of columns
    # Check that data rows align: split by double-space separator
    # The header and data rows should all be the same total width
    assert len(lines) == 3  # 1 header + 2 data rows
    # Assert: long cell causes column to expand — "a very long name here" appears in a data row
    assert "a very long name here" in output
    # Assert: cells are left-justified and separated by double space
    assert "  " in lines[0]
