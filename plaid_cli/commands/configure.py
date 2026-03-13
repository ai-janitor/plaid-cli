# SPEC: s3-cli-router-and-output-formatting.md
# PURPOSE: Interactive config setup — prompts for credentials, writes ~/.config/plaid/.env
# RESPONSIBILITIES: Prompt for client_id and secret, show current values as defaults,
#   write to config file, verify connection with a test API call.
# NOT RESPONSIBLE FOR: Config loading logic (config/), API calls (api/)
# DEPENDENCIES: pathlib, plaid_cli.config.load_config

from pathlib import Path


# --- cmd_configure(args, config, conn) → dict ---
def cmd_configure(args, config, conn):
    config_dir = Path("~/.config/plaid").expanduser()
    config_file = config_dir / ".env"

#   --- Read existing values as defaults ---
    current_id = config.get("client_id") or ""
    current_secret = config.get("secret") or ""
    current_env = config.get("env") or "sandbox"

#   --- Prompt for each value, show current as default ---
    print("Plaid CLI configuration")
    print("Get your keys at: https://dashboard.plaid.com → Developers → Keys")
    print("")

    client_id = input(f"PLAID_CLIENT_ID [{_mask(current_id)}]: ").strip()
    if not client_id:
        client_id = current_id

    secret = input(f"PLAID_SECRET [{_mask(current_secret)}]: ").strip()
    if not secret:
        secret = current_secret

    env = input(f"PLAID_ENV [{current_env}]: ").strip()
    if not env:
        env = current_env

#   --- Write config file ---
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file.write_text(
        f"PLAID_CLIENT_ID={client_id}\n"
        f"PLAID_SECRET={secret}\n"
        f"PLAID_ENV={env}\n"
    )

    print(f"\nSaved to {config_file}")

#   --- Test connection if credentials provided ---
    if client_id and secret:
        try:
            from plaid_cli.api import get_plaid_client
            get_plaid_client(client_id, secret, env)
            print("Connection: OK")
        except Exception as e:
            print(f"Connection: FAILED ({e})")

    return {"configured": True, "config_path": str(config_file)}


def _mask(value):
    """Show last 4 chars only, like AWS CLI does."""
    if not value:
        return "None"
    if len(value) <= 4:
        return "****"
    return "****" + value[-4:]
