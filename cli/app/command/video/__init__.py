import click

from cli.app.command.video.chat import chat


@click.group()
def video():
    """Commands for working with video content."""
    pass


video.add_command(chat)
