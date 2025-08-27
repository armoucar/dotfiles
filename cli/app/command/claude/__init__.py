"""Claude Code management commands."""

import click
from .permissions import permissions
from .test_permissions import test


@click.group()
def claude():
    """Claude Code configuration and management commands."""
    pass


# Add subcommand groups
claude.add_command(permissions)
claude.add_command(test)
