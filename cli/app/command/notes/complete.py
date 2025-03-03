import click
from datetime import datetime

from cli.app.command.notes.utils import load_item, update_item, list_tasks_by_status, fzf_select_item


@click.group()
def task():
    """Manage task completion status."""
    pass


@task.command()
@click.argument("filename")
def complete(filename: str):
    """Mark a task as completed."""
    try:
        # Load the task
        task_data = load_item("task", filename)

        # Check if already completed
        if task_data.get("completed_at") is not None:
            click.echo(f"Task '{filename}' is already marked as completed.")
            return

        # Update task status
        updates = {"completed_at": datetime.now().isoformat()}

        updated_task = update_item("task", filename, updates)
        click.echo(f"Task '{filename}' marked as completed.")

    except FileNotFoundError:
        click.echo(f"Error: Task '{filename}' not found.")
    except Exception as e:
        click.echo(f"Error updating task: {e}")


@task.command()
@click.argument("filename")
def incomplete(filename: str):
    """Mark a task as incomplete."""
    try:
        # Load the task
        task_data = load_item("task", filename)

        # Check if already incomplete
        if task_data.get("completed_at") is None:
            click.echo(f"Task '{filename}' is already marked as incomplete.")
            return

        # Update task status
        updates = {"completed_at": None}

        updated_task = update_item("task", filename, updates)
        click.echo(f"Task '{filename}' marked as incomplete.")

    except FileNotFoundError:
        click.echo(f"Error: Task '{filename}' not found.")
    except Exception as e:
        click.echo(f"Error updating task: {e}")


@click.command()
def complete():
    """Mark a task as completed using fzf for selection."""
    # Get all incomplete tasks
    tasks = list_tasks_by_status(completed=False)

    if not tasks:
        click.echo("No incomplete tasks found.")
        return

    # Use fzf to select a task
    selected_task = fzf_select_item(tasks, prompt="Select a task to mark as completed:")

    if not selected_task:
        click.echo("No task selected.")
        return

    # Update task status - only set the completed_at timestamp
    updates = {"completed_at": datetime.now().isoformat()}

    updated_task = update_item("task", selected_task["filename"], updates)
    click.echo(f"Task '{selected_task['filename']}' marked as completed.")
