# SPEC: s3-cli-router-and-output-formatting.md
# PURPOSE: Test config cascade loading
# RESPONSIBILITIES: Test precedence: flags > env > config file > defaults
# NOT RESPONSIBLE FOR: Testing CLI routing
# DEPENDENCIES: pytest, os, tempfile, plaid_cli.config

import os
import tempfile
from pathlib import Path
import argparse
import pytest
from unittest import mock
from plaid_cli.config import load_config

# --- Test: defaults used when no config exists ---
def test_defaults_used_when_no_config_exists(monkeypatch, tmp_path):
    # Arrange: ensure no env vars are set for plaid config keys
    monkeypatch.delenv("PLAID_CLIENT_ID", raising=False)
    monkeypatch.delenv("PLAID_SECRET", raising=False)
    monkeypatch.delenv("PLAID_ENV", raising=False)
    monkeypatch.delenv("PLAID_DB_PATH", raising=False)
    # Arrange: point config file to a nonexistent path so no file is loaded
    fake_config = tmp_path / "nonexistent_config.yaml"
    # Patch _load_config_file to return empty dict (simulate no config file)
    with mock.patch("plaid_cli.config.load_config._load_config_file", return_value={}):
        # Arrange: args with no config overrides
        args = argparse.Namespace(client_id=None, secret=None, env=None, db_path=None)
        # Act: load config
        config = load_config(args)
    # Assert: defaults are used — env=sandbox, db_path expanded
    assert config["env"] == "sandbox"
    assert config["client_id"] is None
    assert config["secret"] is None
    assert "plaid.db" in config["db_path"]
    # Assert: db_path has ~ expanded (no tilde in result)
    assert "~" not in config["db_path"]

# --- Test: env vars override defaults ---
def test_env_vars_override_defaults(monkeypatch, tmp_path):
    # Arrange: set env vars for plaid config
    monkeypatch.setenv("PLAID_CLIENT_ID", "env-client-id")
    monkeypatch.setenv("PLAID_SECRET", "env-secret")
    monkeypatch.setenv("PLAID_ENV", "development")
    monkeypatch.delenv("PLAID_DB_PATH", raising=False)
    # Patch config file to return empty (no file)
    with mock.patch("plaid_cli.config.load_config._load_config_file", return_value={}):
        # Arrange: args with no overrides
        args = argparse.Namespace(client_id=None, secret=None, env=None, db_path=None)
        # Act: load config
        config = load_config(args)
    # Assert: env vars override the defaults
    assert config["client_id"] == "env-client-id"
    assert config["secret"] == "env-secret"
    assert config["env"] == "development"

# --- Test: config file overrides defaults ---
def test_config_file_overrides_defaults(monkeypatch, tmp_path):
    # Arrange: clear all plaid env vars
    monkeypatch.delenv("PLAID_CLIENT_ID", raising=False)
    monkeypatch.delenv("PLAID_SECRET", raising=False)
    monkeypatch.delenv("PLAID_ENV", raising=False)
    monkeypatch.delenv("PLAID_DB_PATH", raising=False)
    # Arrange: simulate a config file returning specific values
    file_values = {
        "client_id": "file-client-id",
        "secret": "file-secret",
        "env": "production",
    }
    with mock.patch("plaid_cli.config.load_config._load_config_file", return_value=file_values):
        # Arrange: args with no overrides
        args = argparse.Namespace(client_id=None, secret=None, env=None, db_path=None)
        # Act: load config
        config = load_config(args)
    # Assert: config file values override defaults
    assert config["client_id"] == "file-client-id"
    assert config["secret"] == "file-secret"
    assert config["env"] == "production"

# --- Test: env vars override config file ---
def test_env_vars_override_config_file(monkeypatch, tmp_path):
    # Arrange: set conflicting env var (should win over config file)
    monkeypatch.setenv("PLAID_CLIENT_ID", "env-wins-client-id")
    monkeypatch.setenv("PLAID_ENV", "sandbox")
    monkeypatch.delenv("PLAID_SECRET", raising=False)
    monkeypatch.delenv("PLAID_DB_PATH", raising=False)
    # Arrange: config file also has client_id (should be overridden by env var)
    file_values = {
        "client_id": "file-client-id",
        "secret": "file-secret",
        "env": "production",
    }
    with mock.patch("plaid_cli.config.load_config._load_config_file", return_value=file_values):
        # Arrange: args with no overrides
        args = argparse.Namespace(client_id=None, secret=None, env=None, db_path=None)
        # Act: load config
        config = load_config(args)
    # Assert: env var wins over config file for client_id
    assert config["client_id"] == "env-wins-client-id"
    # Assert: config file value is used for secret (no env var set for it)
    assert config["secret"] == "file-secret"
    # Assert: env var wins for env
    assert config["env"] == "sandbox"

# --- Test: missing credentials returns error ---
def test_flags_override_env_and_config_file(monkeypatch, tmp_path):
    # Arrange: set env var that should be overridden by a flag
    monkeypatch.setenv("PLAID_CLIENT_ID", "env-client-id")
    monkeypatch.setenv("PLAID_ENV", "development")
    monkeypatch.delenv("PLAID_SECRET", raising=False)
    monkeypatch.delenv("PLAID_DB_PATH", raising=False)
    # Arrange: config file values (lower precedence than env and flags)
    file_values = {
        "client_id": "file-client-id",
        "secret": "file-secret",
        "env": "production",
    }
    with mock.patch("plaid_cli.config.load_config._load_config_file", return_value=file_values):
        # Arrange: args with flag overrides — flags win over everything
        args = argparse.Namespace(
            client_id="flag-client-id",
            secret=None,
            env="sandbox",
            db_path=None,
        )
        # Act: load config
        config = load_config(args)
    # Assert: flag wins over env var for client_id
    assert config["client_id"] == "flag-client-id"
    # Assert: config file value used for secret (no env var or flag set)
    assert config["secret"] == "file-secret"
    # Assert: flag wins over env var for env
    assert config["env"] == "sandbox"
