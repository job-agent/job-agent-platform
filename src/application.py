"""Application entry point - maintains backwards compatibility.

This module serves as the main application entry point and delegates to
the CLI interface. For the actual CLI implementation, see interfaces/cli/main.py.
"""

from interfaces.cli.main import run_cli_application

# Alias for backwards compatibility
run_application = run_cli_application

if __name__ == "__main__":
    run_application()