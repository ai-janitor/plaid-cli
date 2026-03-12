# S4: CLI Command Handlers

Covers: implementation of each verb-noun command — create link (sandbox),
list items, list accounts, get transactions (with year/month/new-since filters),
sync transactions (incremental pull from Plaid into SQLite for all Items).
Each handler orchestrates S2 (API) and S1 (DB), returns result dicts to S3 (output).

Requirements traced: §1 (connect banks), §2 (pull transactions), §4 (query filters).
Dependencies: S1, S2, S3.
