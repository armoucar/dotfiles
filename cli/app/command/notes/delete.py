import click

from cli.app.command.notes.utils import delete_item, list_items, fzf_select_item

@click.command()
@click.option("--force", "-f", is_flag=True, help="Delete without confirmation")
def delete(force: bool):
    """Delete a note or task using fzf for selection."""
    # Get all items
    items = list_items()

    if not items:
        click.echo("No items found.")
        return

    # Use fzf to select an item
    selected_item = fzf_select_item(items, prompt="Select an item to delete:")

    if not selected_item:
        click.echo("No item selected.")
        return

    # Confirm deletion
    if not force:
        if not click.confirm(f"Are you sure you want to delete {selected_item['type']} '{selected_item['filename']}'?"):
            click.echo("Operation cancelled.")
            return

    # Delete the item
    success = delete_item(selected_item["type"], selected_item["filename"])

    if success:
        click.echo(f"{selected_item['type'].capitalize()} '{selected_item['filename']}' deleted successfully.")
    else:
        click.echo(f"Error: Could not delete {selected_item['type']} '{selected_item['filename']}'.")
