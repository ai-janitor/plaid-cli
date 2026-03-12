# CLI Framework Selection

## Decision: argparse (stdlib)

### Why
- Zero dependencies — comes with Python 3.6+
- Every CLI in ~/.skills/ uses argparse (ai-first-api, reference-integrity, skill-registry-guide, life-center)
- Supports 2-level verb-noun subcommands natively via nested add_subparsers()
- Global flags (--json, --quiet) parsed at root level, inherited by all commands

### Verb-Noun Pattern
```
parser = ArgumentParser()
parser.add_argument("--json", action="store_true")
parser.add_argument("--quiet", "-q", action="store_true")

subparsers = parser.add_subparsers(dest="verb")

# verb group
get_group = subparsers.add_parser("get")
get_nouns = get_group.add_subparsers(dest="noun")

# verb + noun
get_trans = get_nouns.add_parser("transactions")
get_trans.add_argument("--year", type=int)
get_trans.set_defaults(func=cmd_get_transactions)
```

### Why NOT click/typer
- Extra dependency for no added value at this scale
- Not used anywhere in the existing skills codebase
- argparse handles the verb-noun pattern cleanly
