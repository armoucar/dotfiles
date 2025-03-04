import click
from typing import List, Optional

from cli.app.command.notes.utils import update_item, load_item

@click.group()
def update():
    """Update an existing note, task, or memory."""
    pass

@update.command()
@click.argument("filename")
@click.option("--content", "-c", help="New content for the note")
@click.option("--add-tags", "-a", multiple=True, help="Add tags to the note")
@click.option("--remove-tags", "-r", multiple=True, help="Remove tags from the note")
def note(filename: str, content: Optional[str],
         add_tags: List[str], remove_tags: List[str]):
    """Update an existing note."""
    try:
        # Load the current note
        note_data = load_item("note", filename)

        # Build update dictionary
        updates = {}
        if content:
            updates["content"] = content

        # Process tags
        if add_tags or remove_tags:
            current_tags = set(note_data.get("tags", []))
            # Add new tags
            for tag in add_tags:
                current_tags.add(tag)
            # Remove specified tags
            for tag in remove_tags:
                current_tags.discard(tag)
            updates["tags"] = list(current_tags)

        # Update the note
        updated_note = update_item("note", filename, updates)
        click.echo(f"Note '{filename}' updated successfully.")

    except FileNotFoundError:
        click.echo(f"Error: Note '{filename}' not found.")
    except Exception as e:
        click.echo(f"Error updating note: {e}")

@update.command()
@click.argument("filename")
@click.option("--content", "-c", help="New content for the task")
@click.option("--add-tags", "-a", multiple=True, help="Add tags to the task")
@click.option("--remove-tags", "-r", multiple=True, help="Remove tags from the task")
def task(filename: str, content: Optional[str],
         add_tags: List[str], remove_tags: List[str]):
    """Update an existing task."""
    try:
        # Load the current task
        task_data = load_item("task", filename)

        # Build update dictionary
        updates = {}
        if content:
            updates["content"] = content

        # Process tags
        if add_tags or remove_tags:
            current_tags = set(task_data.get("tags", []))
            # Add new tags
            for tag in add_tags:
                current_tags.add(tag)
            # Remove specified tags
            for tag in remove_tags:
                current_tags.discard(tag)
            updates["tags"] = list(current_tags)

        # Update the task
        updated_task = update_item("task", filename, updates)
        click.echo(f"Task '{filename}' updated successfully.")

    except FileNotFoundError:
        click.echo(f"Error: Task '{filename}' not found.")
    except Exception as e:
        click.echo(f"Error updating task: {e}")

@update.command()
@click.argument("filename")
@click.option("--content", "-c", help="New content for the memory")
@click.option("--add-tags", "-a", multiple=True, help="Add tags to the memory")
@click.option("--remove-tags", "-r", multiple=True, help="Remove tags from the memory")
def memory(filename: str, content: Optional[str],
           add_tags: List[str], remove_tags: List[str]):
    """Update an existing memory."""
    try:
        # Load the current memory
        memory_data = load_item("memory", filename)

        # Build update dictionary
        updates = {}
        if content:
            updates["content"] = content

        # Process tags
        if add_tags or remove_tags:
            current_tags = set(memory_data.get("tags", []))
            # Add new tags
            for tag in add_tags:
                current_tags.add(tag)
            # Remove specified tags
            for tag in remove_tags:
                current_tags.discard(tag)
            updates["tags"] = list(current_tags)

        # Update the memory
        updated_memory = update_item("memory", filename, updates)
        click.echo(f"Memory '{filename}' updated successfully.")

    except FileNotFoundError:
        click.echo(f"Error: Memory '{filename}' not found.")
    except Exception as e:
        click.echo(f"Error updating memory: {e}")
