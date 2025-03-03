import click
from datetime import datetime
from typing import Optional
from tabulate import tabulate

from cli.app.command.notes.utils import list_items


@click.command()
@click.option("--show-content", "-c", is_flag=True, help="Show item content in listing")
@click.option("--tag", "-t", help="Filter items by tag")
@click.option("--type", type=click.Choice(["note", "task"]), help="Filter by item type")
@click.option("--completed", is_flag=True, help="Show only completed tasks")
@click.option("--pending", is_flag=True, help="Show only pending tasks")
def list_cmd(show_content: bool, tag: Optional[str], type: Optional[str], completed: bool, pending: bool):
    """List all notes and tasks (newest first)."""

    # Get all items
    items = list_items(type)

    # Filter by tag if specified
    if tag:
        items = [item for item in items if tag in item.get("tags", [])]

    # Filter tasks by completion status if requested
    if completed or pending:
        if type and type != "task":
            click.echo("Error: --completed and --pending flags can only be used with tasks")
            return

        # Filter to tasks only if not already filtered
        if not type:
            items = [item for item in items if item["type"] == "task"]

        # Then apply completion filter
        if completed:
            items = [item for item in items if item.get("completed_at") is not None]
        elif pending:
            items = [item for item in items if item.get("completed_at") is None]

    if not items:
        click.echo("No items found matching your criteria.")
        return

    # Prepare data for tabulate
    table_data = []
    for item in items:
        # Format the date
        created_date = datetime.fromisoformat(item["created_at"]).strftime("%Y-%m-%d %H:%M")

        # Format the item type
        item_type = item["type"].upper()

        # Get the title
        title = item["title"]

        # Determine the state of the item
        if item["type"] == "task":
            state = "COMPLETED" if item.get("completed_at") is not None else "PENDING"
        else:
            state = "-"  # Notes don't have a state

        # Format content preview if available
        content_preview = ""
        if "content" in item and item["content"]:
            content = item["content"].replace("\n", " ").strip()
            if len(content) > 50:
                content_preview = f"{content[:50]}..."
            else:
                content_preview = content

        # Add row to table data
        table_data.append([created_date, item_type, state, title, content_preview])

    # Display the table
    headers = ["Date", "Type", "State", "Title", "Preview"]
    click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))

    # Show full content if requested
    if show_content:
        click.echo("\nFull Content:")
        for item in items:
            if "content" in item and item["content"]:
                click.echo(f"\n[{item['title']}]")
                click.echo(f"{item['content']}")
                click.echo("---")
