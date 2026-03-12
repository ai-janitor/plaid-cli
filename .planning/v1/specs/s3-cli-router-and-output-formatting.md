# S3: CLI Router and Output Formatting

## Purpose
Define the CLI entry point, verb-noun command tree, global flags, output formatting, config loading, and error handling. This is the interface layer that users and AI agents interact with.

## Requirements Traceability
- §5: Verb-noun, --json/--quiet, --help, no prompts, config cascade, exit codes, agent rules
- §6: Python CLI, no web framework, AI-first naming

## Dependencies
- S1: Queries DB for display
- S2: API calls for create/sync commands (via S4 handlers)

---

## Command Tree

```
plaid --help
plaid --json
plaid --quiet / -q

plaid create link [--institution <id>]
plaid list items
plaid list accounts [--item <item_id>]
plaid get transactions [--year <YYYY>] [--month <MM>] [--new] [--limit <N>]
plaid sync [--item <item_id>]
```

### Commands

| Command | Verb | Noun | Description |
|---------|------|------|-------------|
| `create link` | create | link | Connect a new bank (sandbox) |
| `list items` | list | items | Show all connected banks |
| `list accounts` | list | accounts | Show all accounts across banks |
| `get transactions` | get | transactions | Query stored transactions |
| `sync` | sync | (all items) | Pull new transactions from Plaid |

### Global Flags
| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `--json` | | bool | false | Output as JSON |
| `--quiet` | `-q` | bool | false | Output IDs/values only, pipe-friendly |
| `--help` | `-h` | | | Show help at current level |

### Command-Specific Flags

**create link:**
| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--institution` | str | ins_109508 | Sandbox institution ID |

**list accounts:**
| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--item` | str | (all) | Filter by item_id |

**get transactions:**
| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--year` | int | (all) | Filter by year |
| `--month` | int | (none) | Filter by month (requires --year) |
| `--new` | bool | false | Show only transactions from last sync |
| `--limit` | int | 50 | Max rows to return |

**sync:**
| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--item` | str | (all) | Sync only this item (default: all items) |

---

## Config Cascade

Precedence (highest to lowest):
1. Command-line flags
2. Environment variables: `PLAID_CLIENT_ID`, `PLAID_SECRET`, `PLAID_ENV`
3. Config file: `~/.config/plaid/config.yaml` (keys: client_id, secret, env, db_path)
4. Defaults: env=sandbox, db_path=~/.local/share/plaid/plaid.db

Config loading function: `load_config(args) → dict` — merges all layers, returns flat dict with: client_id, secret, env, db_path.

---

## Output Formatting

### Human Mode (default)
Table format with column headers. Example for `get transactions`:
```
DATE        AMOUNT    ACCOUNT          NAME
2026-03-10  -42.50    Chase Checking   Starbucks
2026-03-09  -150.00   BofA Savings     Transfer Out
```

### JSON Mode (--json)
Single-line valid JSON. Same data as human mode.
```json
{"count": 2, "transactions": [{"date": "2026-03-10", "amount": -42.50, "account": "Chase Checking", "name": "Starbucks"}, ...]}
```

### Quiet Mode (--quiet)
One value per line, pipe-friendly. For transactions: transaction_id per line.
```
txn_abc123
txn_def456
```

### Error Output
Human mode: `Error: <message>` to stderr with hint.
JSON mode: `{"error": "<message>"}` to stdout.
Quiet mode: exit code only, no output.

---

## Exit Codes
- 0: success
- 1: runtime error (API failure, DB error)
- 2: usage error (bad flags, missing required args)

---

## Behavior

- The entry point is a single `main()` function in the CLI module.
- argparse handles --help automatically at every level.
- Global flags (--json, --quiet) are parsed at the root parser and available to all handlers via `args`.
- The router dispatches to S4 handler functions via `set_defaults(func=...)`.
- If no verb is given, print help and exit 2.
- If verb is given but no noun (where required), print verb-level help and exit 2.

## Edge Cases

- `--json` and `--quiet` both set: `--json` wins.
- `--month` without `--year`: print error "Error: --month requires --year" and exit 2.
- No `PLAID_CLIENT_ID` or `PLAID_SECRET` configured: print error with hint "Set PLAID_CLIENT_ID and PLAID_SECRET environment variables or create ~/.config/plaid/config.yaml" and exit 1.
- DB file directory doesn't exist: create it on first use.
