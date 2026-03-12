# S3: CLI Router and Output Formatting

Covers: argparse verb-noun command tree (create, list, get, sync), global flags
(--json, --quiet), human table / JSON / quiet output formatting, error formatting
with hints, help at every level, config cascade (flags > env PLAID_* > config
file > defaults), meaningful exit codes (0/1/2).

Requirements traced: §5 (all bullets), §6 (Python CLI, no web framework).
Dependencies: S1 (queries DB for display), S2 (API calls for create/sync).
