"""Kubectl command package."""

import click

from cli.app.command.kubectl.watch_gugelmin import watch_gugelmin
from cli.app.command.kubectl.pod_interact import pod_interact


@click.group()
def kubectl():
    """Kubernetes (kubectl) commands."""
    pass


# Add all commands to the kubectl group
kubectl.add_command(watch_gugelmin)
kubectl.add_command(pod_interact)
