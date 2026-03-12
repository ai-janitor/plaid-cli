# S1: SQLite Database Schema and Access

Covers: all four tables (items, accounts, transactions, sync_state), connection
management, insert/update/delete/query functions for each table. Query helpers
for filtering transactions by year, month, and new-since-last-sync.

Requirements traced: §1 (persist access tokens, track profiles), §2 (persist cursor),
§3 (all bullets), §4 (query by year/month/new-since).
Dependencies: None — foundation layer.
