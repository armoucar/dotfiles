import click
import os
import tempfile
import subprocess
from typing import List, Optional

from cli.app.command.notes.utils import save_item

@click.command()
@click.argument("type", type=click.Choice(["note", "task"]))
@click.option("--content", "-c", required=False, help="Content of the item")
@click.option("--tags", "-g", multiple=True, help="Tags for the item")
def create(type: str, content: Optional[str], tags: List[str]):
    """Create a new note or task."""

    # If content is not provided, open vim editor to get content
    if content is None:
        content = get_content_from_editor()
        if not content:
            click.echo("Aborted: No content provided.")
            return

    filepath = save_item(type, content, list(tags))
    click.echo(f"{type.capitalize()} created successfully: {os.path.basename(filepath)}")

def get_content_from_editor() -> Optional[str]:
    """Open vim editor and get content from it."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp:
        temp_path = temp.name

    try:
        # Open vim with the temporary file
        subprocess.run(["vim", temp_path], check=True)

        # Read content from the temporary file
        with open(temp_path, 'r') as f:
            content = f.read().strip()

        # Return None if the content is empty
        if not content:
            return None

        return content
    except subprocess.CalledProcessError:
        # User aborted vim
        return None
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
