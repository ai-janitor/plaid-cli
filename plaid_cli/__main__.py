# SPEC: s3-cli-router-and-output-formatting.md
# PURPOSE: Entry point for `python -m plaid_cli`
# RESPONSIBILITIES: Call main() from the router
# NOT RESPONSIBLE FOR: Argument parsing, command dispatch
# DEPENDENCIES: plaid_cli.router

# --- Import main from router ---
from plaid_cli.router import main

# --- Call main() ---
main()
