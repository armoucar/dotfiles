import click

from cli.app.command.audio.md_to_speech import md_to_speech


@click.group()
def audio():
    """Commands for working with audio."""
    pass


audio.add_command(md_to_speech)
