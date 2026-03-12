# Raw Requirements — Plaid Bank Transaction Puller

Captured from conversation on 2026-03-12.

---

- I want to pull my bank transactions using the Plaid API
- Use the Plaid Python SDK (plaid-python)
- CLI tool, not a web server — no Flask, no React frontend
- In sandbox mode, skip Plaid Link UI — use sandbox public token creation
- Store transactions locally (SQLite was discussed)
- Use the AI-first CLI pattern (~/.skills/ai-first-cli/):
  - Verb-noun command structure (e.g., `plaid get transactions`, `plaid create link`)
  - --json flag for structured JSON output, human-readable table/text by default, --quiet for pipe-friendly
  - --help at every level (root, verb group, subcommand)
  - No interactive prompts — works without TTY
  - Configuration cascade: flags > env (PLAID_*) > config file > defaults
  - Agent rules file so AI agents can learn the CLI from --help alone
  - Max 2 subcommand levels
  - Meaningful exit codes (0=success, 1=error, 2=usage)
- Use the AI-first design pattern (~/.skills/ai-first-design/):
  - Self-documenting noun+verb naming for files and functions
  - 1 file = 1 function, directory = domain
  - File/folder names an AI can understand from `ls` alone
- No Flask. No web framework. Just a CLI that pulls transactions.
- Save access_token locally for reuse across runs so we don't re-link every time
- Use /transactions/sync endpoint (cursor-based, incremental updates)
- Want to eventually connect real bank accounts (not just sandbox)
- Multiple bank accounts — need to auth with all of them
- Track bank account profiles (which bank, which accounts, metadata)
- Pull transactions across all connected accounts
- SQLite database to store transactions locally
- Query transactions by year, by month, or "anything new since last pull"
- Just get the data — no categorization, no export, no analysis for now
- One big list with account info, not grouped views
