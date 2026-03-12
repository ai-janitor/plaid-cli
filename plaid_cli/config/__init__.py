# SPEC: s3-cli-router-and-output-formatting.md
# PURPOSE: Config package
# RESPONSIBILITIES: Provide single import point for config loading
# NOT RESPONSIBLE FOR: Implementation details
# DEPENDENCIES: config.load_config

from plaid_cli.config.load_config import load_config

__all__ = ["load_config"]
