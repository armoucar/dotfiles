"""Claude Code management commands."""

import click
from .single import single


@click.group()
def claude():
    """Claude Code configuration and management commands."""
    pass


# Add the single command
claude.add_command(single)
