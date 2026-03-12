# SPEC: s3-cli-router-and-output-formatting.md
# PURPOSE: Output package — re-export formatting functions
# RESPONSIBILITIES: Provide single import point for output formatting
# NOT RESPONSIBLE FOR: Implementation details
# DEPENDENCIES: All output submodules

from plaid_cli.output.format_output import format_output
from plaid_cli.output.format_error import format_error

__all__ = ["format_output", "format_error"]
