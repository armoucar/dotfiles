"""Claude Code management commands."""

import click
from .single import single
from .permissions_apply import permissions_apply


@click.group()
def claude():
    """Claude Code configuration and management commands."""
    pass


# Add commands
claude.add_command(single)
claude.add_command(permissions_apply)
