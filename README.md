# plaid-cli

CLI tool to pull personal bank transactions from multiple accounts via the Plaid API.

## Install

### Quick (recommended)

```bash
git clone https://github.com/ai-janitor/plaid-cli.git
cd plaid-cli
./setup.sh
```

Installs via `pipx` to `~/.local/bin/plaid` — isolated venv, works from anywhere, survives repo deletion.

### pipx (manual)

```bash
pipx install git+https://github.com/ai-janitor/plaid-cli.git
```

### pip (into existing venv)

```bash
pip install git+https://github.com/ai-janitor/plaid-cli.git
```

### Development

```bash
git clone https://github.com/ai-janitor/plaid-cli.git
cd plaid-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Setup

Get your Plaid sandbox credentials at [dashboard.plaid.com](https://dashboard.plaid.com) under Developers > Keys.

```bash
cp .env.example .env
# Edit .env with your client_id and sandbox secret
```

Or set environment variables:

```bash
export PLAID_CLIENT_ID=your_client_id
export PLAID_SECRET=your_sandbox_secret
```

Or create a config file at `~/.config/plaid/config.yaml`:

```yaml
client_id: your_client_id
secret: your_sandbox_secret
env: sandbox
```

Config precedence: flags > env vars > config file > defaults.

## Usage

```bash
plaid create link                       # Connect a sandbox bank
plaid sync                              # Pull transactions from Plaid
plaid get transactions                  # View transactions
plaid get transactions --year 2026      # Filter by year
plaid get transactions --month 3        # Filter by month (requires --year)
plaid get transactions --new            # Only new since last sync
plaid list items                        # Show connected banks
plaid list accounts                     # Show all accounts
```

### Output modes

```bash
plaid list items                        # Human-readable table (default)
plaid list items --json                 # JSON output
plaid list items -q                     # Quiet — IDs only, for piping
```

### Help at every level

```bash
plaid --help
plaid list --help
plaid list accounts --help
```

## Uninstall

```bash
pipx uninstall plaid-cli
```
