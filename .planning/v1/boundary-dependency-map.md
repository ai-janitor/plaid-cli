# Boundary Dependency Map — v1

## Boundary: S1 Database ↔ S2 Plaid API Client
- Contract type: function call (S2 calls S1 insert/update/delete functions)
- Status: [pending]
- Edges: S2 stores Items, accounts, transactions, sync cursors via S1 functions

## Boundary: S1 Database ↔ S3 CLI Router + Output
- Contract type: function call (S3 calls S1 query functions)
- Status: [pending]
- Edges: S3 calls S1 to list items, list accounts, query transactions for display

## Boundary: S1 Database ↔ S4 Command Handlers
- Contract type: function call (S4 calls S1 query functions for get/list commands)
- Status: [pending]
- Edges: S4 calls S1 for query-by-year, query-by-month, query-new-since

## Boundary: S2 Plaid API Client ↔ S4 Command Handlers
- Contract type: function call (S4 calls S2 to create links and sync transactions)
- Status: [pending]
- Edges: S4 invokes S2.create_sandbox_link(), S2.sync_transactions()

## Boundary: S3 CLI Router ↔ S4 Command Handlers
- Contract type: function signature (S3 routes to S4 handler functions via argparse set_defaults)
- Status: [pending]
- Edges: S3 parser sets `func=cmd_create_link`, `func=cmd_sync_transactions`, etc. S4 handlers accept `args` namespace, return result dicts. S3 formats output.
