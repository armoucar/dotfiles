import click
from typing import Optional

from cli.app.command.notes.utils import list_items, fzf_select_item, edit_item_in_editor

@click.command()
@click.option("--type", type=click.Choice(["note", "task"]), help="Filter by item type")
@click.option("--tag", "-t", help="Filter items by tag")
def edit(type: Optional[str], tag: Optional[str]):
    """Edit a note or task using fzf for selection."""
    # Get filtered items
    items = list_items(type)

    # Filter by tag if specified
    if tag:
        items = [item for item in items if tag in item.get("tags", [])]

    if not items:
        click.echo("No items found matching your criteria.")
        return

    # Use fzf to select an item
    selected_item = fzf_select_item(items, prompt="Select an item to edit:")

    if not selected_item:
        click.echo("No item selected.")
        return

    # Edit the selected item
    success = edit_item_in_editor(selected_item)

    if success:
        click.echo(f"Successfully edited {selected_item['type']}: {selected_item['filename']}")
    else:
        click.echo("Edit operation cancelled or failed.")
