# Raw-to-Clean Traceability — v1

| Raw Item | Clean Section | Notes |
|----------|---------------|-------|
| Pull bank transactions using Plaid API | §2 Transaction Retrieval | — |
| Use Plaid Python SDK | §6 Code Organization | — |
| CLI tool, no web server, no Flask | §5 CLI Interface, §6 Code Org | Repeated twice in raw, merged |
| Sandbox: skip Link UI | §1 Bank Connection Mgmt | — |
| Store transactions locally (SQLite) | §3 Transaction Storage | — |
| AI-first CLI: verb-noun, --json, --help, no prompts, config cascade, agent rules, exit codes | §5 CLI Interface | All sub-bullets mapped |
| AI-first design: naming, 1 file = 1 function, directory = domain | §6 Code Organization | — |
| Save access_token for reuse | §1 Bank Connection Mgmt | — |
| /transactions/sync (cursor-based) | §2 Transaction Retrieval | — |
| Eventually connect real banks | §1 Bank Connection Mgmt + Out of Scope | Architecture supports it, sandbox-only for v1 |
| Multiple bank accounts, auth with all | §1 Bank Connection Mgmt | — |
| Track bank account profiles | §1 Bank Connection Mgmt | — |
| Pull across all connected accounts | §2 Transaction Retrieval | — |
| SQLite database | §3 Transaction Storage | Duplicate of "store locally", merged |
| Query by year, month, new since | §4 Transaction Querying | — |
| Just get data, no categorization/export | §4 Querying + Out of Scope | — |
| One big list with account info | §4 Transaction Querying | — |

**Coverage:** All 16 raw items mapped. Zero omissions.
