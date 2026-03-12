# SPEC: s3-cli-router-and-output-formatting.md
# PURPOSE: Load configuration with cascade precedence: flags > env > config file > defaults
# RESPONSIBILITIES: Merge config from all sources in precedence order. Return flat dict with
#   client_id, secret, env, db_path.
# NOT RESPONSIBLE FOR: Parsing CLI args (router does that), creating the DB
# DEPENDENCIES: os, pathlib, yaml (optional, for config file)

import os
from pathlib import Path


def _load_config_file(config_path):
    """Load config from file. Try yaml first, fall back to key=value parsing."""
    if not config_path.exists():
        return {}

    text = config_path.read_text()
    if not text.strip():
        return {}

    # Try yaml first
    try:
        import yaml
        data = yaml.safe_load(text)
        if isinstance(data, dict):
            return data
        return {}
    except ImportError:
        pass

    # Fall back to simple key=value parsing
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
        elif "=" in line:
            key, _, value = line.partition("=")
        else:
            continue
        key = key.strip()
        value = value.strip()
        if value and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        if key in ("client_id", "secret", "env", "db_path"):
            result[key] = value

    return result


# --- load_config(args) → dict ---
def load_config(args):
#   --- Defaults: env="sandbox", db_path="~/.local/share/plaid/plaid.db" ---
    config = {
        "client_id": None,
        "secret": None,
        "env": "sandbox",
        "db_path": "~/.local/share/plaid/plaid.db",
    }

#   --- Config file: load ~/.config/plaid/config.yaml if it exists ---
#     --- Keys: client_id, secret, env, db_path ---
    config_path = Path("~/.config/plaid/config.yaml").expanduser()
    file_config = _load_config_file(config_path)
    for key in ("client_id", "secret", "env", "db_path"):
        if key in file_config and file_config[key] is not None:
            config[key] = file_config[key]

#   --- Env vars: PLAID_CLIENT_ID, PLAID_SECRET, PLAID_ENV, PLAID_DB_PATH ---
    env_mapping = {
        "PLAID_CLIENT_ID": "client_id",
        "PLAID_SECRET": "secret",
        "PLAID_ENV": "env",
        "PLAID_DB_PATH": "db_path",
    }
    for env_var, config_key in env_mapping.items():
        value = os.environ.get(env_var)
        if value is not None:
            config[config_key] = value

#   --- Flags: check args for any config overrides ---
    flag_mapping = {
        "client_id": "client_id",
        "secret": "secret",
        "env": "env",
        "db_path": "db_path",
    }
    for attr, config_key in flag_mapping.items():
        value = getattr(args, attr, None) if args is not None else None
        if value is not None:
            config[config_key] = value

#   --- Merge in order: defaults ← config file ← env vars ← flags ---
    # (already done above in cascade order)

#   --- Expand ~ in db_path ---
    config["db_path"] = str(Path(config["db_path"]).expanduser())

#   --- Create db_path parent directory if not exists ---
    db_parent = Path(config["db_path"]).parent
    db_parent.mkdir(parents=True, exist_ok=True)

#   --- Return {"client_id": ..., "secret": ..., "env": ..., "db_path": ...} ---
    return config
