import click
from datetime import datetime

from cli.app.command.notes.utils import update_item, list_tasks_by_status, fzf_select_item

@click.command()
def incomplete():
    """Mark a task as incomplete using fzf for selection."""
    # Get all completed tasks
    tasks = list_tasks_by_status(completed=True)

    if not tasks:
        click.echo("No completed tasks found.")
        return

    # Use fzf to select a task
    selected_task = fzf_select_item(tasks, prompt="Select a task to mark as incomplete:")

    if not selected_task:
        click.echo("No task selected.")
        return

    # Update task status - only set completed_at to None
    updates = {"completed_at": None}

    updated_task = update_item("task", selected_task["filename"], updates)
    click.echo(f"Task '{selected_task['filename']}' marked as incomplete.")
