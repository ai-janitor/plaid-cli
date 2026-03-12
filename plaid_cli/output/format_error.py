# SPEC: s3-cli-router-and-output-formatting.md
# PURPOSE: Format errors for human, JSON, or quiet output modes
# RESPONSIBILITIES: Format error message to stderr (human) or stdout JSON. Include hints.
# NOT RESPONSIBLE FOR: Deciding what is an error
# DEPENDENCIES: json, sys

import json
import sys


# --- format_error(message: str, hint: str = None, json_mode: bool = False) → str ---
def format_error(message, hint=None, json_mode=False):
#   --- If json_mode: ---
    if json_mode:
#     --- Return json.dumps({"error": message}) to stdout ---
        return json.dumps({"error": message})

#   --- Else: ---
#     --- Print "Error: <message>" to stderr ---
    print(f"Error: {message}", file=sys.stderr)
#     --- If hint: print "Hint: <hint>" to stderr ---
    if hint:
        print(f"Hint: {hint}", file=sys.stderr)
#     --- Return empty string ---
    return ""
