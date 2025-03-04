import click
import os
from typing import List

from cli.app.command.notes.utils import save_item

@click.command()
@click.argument("type", type=click.Choice(["note", "task"]))
@click.option("--content", "-c", required=True, help="Content of the item")
@click.option("--tags", "-g", multiple=True, help="Tags for the item")
def create(type: str, content: str, tags: List[str]):
    """Create a new note or task."""
    filepath = save_item(type, content, list(tags))
    click.echo(f"{type.capitalize()} created successfully: {os.path.basename(filepath)}")
