import os
import yaml
import subprocess
import tempfile
import json
from datetime import datetime
from typing import Dict, List, Optional, Literal, Tuple, Any, Set

# Define paths
NOTES_DIR = os.path.expanduser("~/.oh-my-zsh/custom/.notes")
NOTES_PATH = os.path.join(NOTES_DIR, "notes")
TASKS_PATH = os.path.join(NOTES_DIR, "tasks")
ARGS_PATH = os.path.join(NOTES_DIR, "args.json")

# Define types
NoteType = Literal["note", "task"]


def ensure_directories_exist():
    """Ensure all necessary directories exist."""
    for path in [NOTES_PATH, TASKS_PATH]:
        os.makedirs(path, exist_ok=True)


def get_path_for_type(item_type: NoteType) -> str:
    """Get the appropriate directory path for the given item type."""
    if item_type == "note":
        return NOTES_PATH
    elif item_type == "task":
        return TASKS_PATH
    else:
        raise ValueError(f"Unknown item type: {item_type}")


def generate_filename(title: str) -> str:
    """Generate a filename with timestamp and title."""
    # Get current timestamp in yyyy-MM-dd-HH-mm-ss format
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    # Process title: replace spaces with underscores and remove special characters
    safe_title = "".join(c if c.isalnum() or c == " " else "_" for c in title)
    safe_title = safe_title.replace(" ", "_").lower()

    # Combine timestamp and title
    return f"{timestamp}_{safe_title}.yaml"


def save_item(item_type: NoteType, title: str, content: str, tags: Optional[List[str]] = None) -> str:
    """Save a new item to the filesystem."""
    ensure_directories_exist()

    directory = get_path_for_type(item_type)
    filename = generate_filename(title)
    filepath = os.path.join(directory, filename)

    # Create the item data structure
    item_data = {
        "title": title,
        "content": content,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "tags": tags or [],
    }

    # Add task-specific fields
    if item_type == "task":
        item_data["completed_at"] = None

    # Save to file
    with open(filepath, "w") as f:
        yaml.dump(item_data, f, default_flow_style=False)

    # Update tags in args.json
    if tags:
        update_args_tags(tags)

    return filepath


def load_item(item_type: NoteType, filename: str) -> Dict:
    """Load an item from the filesystem."""
    directory = get_path_for_type(item_type)
    filepath = os.path.join(directory, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No {item_type} found with filename {filename}")

    with open(filepath, "r") as f:
        return yaml.safe_load(f)


def update_item(item_type: NoteType, filename: str, updates: Dict) -> Dict:
    """Update an existing item."""
    directory = get_path_for_type(item_type)
    filepath = os.path.join(directory, filename)

    # Load existing data
    item_data = load_item(item_type, filename)

    # Check if we're updating tags
    if "tags" in updates and updates["tags"]:
        update_args_tags(updates["tags"])

    # Update fields
    for key, value in updates.items():
        item_data[key] = value

    # Always update the updated_at timestamp
    item_data["updated_at"] = datetime.now().isoformat()

    # Save back to file
    with open(filepath, "w") as f:
        yaml.dump(item_data, f, default_flow_style=False)

    return item_data


def list_items(item_type: Optional[NoteType] = None) -> List[Dict]:
    """
    List all items, optionally filtered by type.
    Returns items sorted by creation date (newest first).
    """
    ensure_directories_exist()

    items = []

    # Determine which directories to scan
    if item_type:
        directories = [(item_type, get_path_for_type(item_type))]
    else:
        directories = [("note", NOTES_PATH), ("task", TASKS_PATH)]

    # Collect items from each directory
    for type_name, directory in directories:
        for filename in os.listdir(directory):
            if filename.endswith(".yaml"):
                try:
                    item_data = load_item(type_name, filename)
                    item_data["filename"] = filename
                    item_data["type"] = type_name
                    item_data["filepath"] = os.path.join(directory, filename)
                    items.append(item_data)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

    # Sort by creation date (newest first)
    items.sort(key=lambda x: x["created_at"], reverse=True)

    return items


def list_tasks_by_status(completed: bool = False) -> List[Dict]:
    """List tasks filtered by completion status."""
    tasks = list_items("task")
    return [task for task in tasks if (task.get("completed_at") is not None) == completed]


def delete_item(item_type: NoteType, filename: str) -> bool:
    """Delete an item."""
    directory = get_path_for_type(item_type)
    filepath = os.path.join(directory, filename)

    if not os.path.exists(filepath):
        return False

    os.remove(filepath)
    return True


def complete_task(filename: str) -> Dict:
    """Mark a task as completed."""
    task_data = load_item("task", filename)

    # Update task status
    task_data["completed_at"] = datetime.now().isoformat()

    # Save changes
    with open(os.path.join(TASKS_PATH, filename), "w") as f:
        yaml.dump(task_data, f, default_flow_style=False)

    return task_data


def _format_item_for_display(item: Dict) -> str:
    """Format an item for display in fzf."""
    created = datetime.fromisoformat(item["created_at"]).strftime("%Y-%m-%d %H:%M")

    # Start with type and title
    result = f"[{item['type'].upper()}] {item['title']} [Created: {created}]"

    # Add tags if any
    if item.get("tags"):
        result += f" Tags: {', '.join(item['tags'])}"

    # Add task-specific info
    if "completed" in item:
        status = "✓" if item["completed"] else "○"
        result = f"{status} {result}"

        if item["completed"] and item["completed_at"]:
            completed = datetime.fromisoformat(item["completed_at"]).strftime("%Y-%m-%d %H:%M")
            result += f" [Completed: {completed}]"

    return result


def fzf_select_item(items: List[Dict], prompt: str = "Select an item:") -> Optional[Dict]:
    """Use fzf to select an item from a list."""
    if not items:
        return None

    # Format items for fzf
    fzf_input = []
    for i, item in enumerate(items):
        fzf_input.append(f"{_format_item_for_display(item)}")

    # Run fzf
    try:
        fzf_process = subprocess.Popen(
            ["fzf", "--ansi", "--prompt", prompt, "--height", "40%"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )

        input_str = "\n".join(fzf_input)
        stdout, _ = fzf_process.communicate(input=input_str)

        if fzf_process.returncode == 0 and stdout.strip():
            # Find the selected item
            selected_line = stdout.strip()
            for i, line in enumerate(fzf_input):
                if line == selected_line:
                    return items[i]

        return None
    except FileNotFoundError:
        print("Error: fzf is not installed. Please install it first.")
        return None


def edit_item_in_editor(item: Dict) -> bool:
    """Open an item in vim editor and track if changes were made."""
    item_type = item["type"]
    filename = item["filename"]
    filepath = os.path.join(get_path_for_type(item_type), filename)

    try:
        # Get file modification time before editing
        mod_time_before = os.path.getmtime(filepath)

        # Read the file content before editing
        with open(filepath, "r") as f:
            content_before = f.read()

        # Always use vim as the editor
        subprocess.run(["vim", filepath], check=True)

        # Check if the file was modified
        mod_time_after = os.path.getmtime(filepath)

        # Read the file content after editing
        with open(filepath, "r") as f:
            content_after = f.read()

        # Check if content changed
        if content_before != content_after:
            # Update tags in args.json if needed
            try:
                updated_data = yaml.safe_load(content_after)
                if "tags" in updated_data and updated_data["tags"]:
                    update_args_tags(updated_data["tags"])
            except Exception as e:
                print(f"Warning: Could not update tags: {e}")

            return True
        else:
            # No changes were made
            return False

    except Exception as e:
        print(f"Error editing item: {e}")
        return False


def get_all_tags() -> Set[str]:
    """Get all unique tags from all notes and tasks."""
    all_items = list_items()
    all_tags = set()

    for item in all_items:
        if "tags" in item and item["tags"]:
            all_tags.update(item["tags"])

    return all_tags


def update_args_tags(new_tags: List[str]) -> None:
    """Update the args.json file with new tags."""
    ensure_directories_exist()

    # Default args data
    args_data = {
        "types": ["note", "task"],
        "tags": ["work", "personal", "important", "urgent", "idea", "meeting", "project", "reminder"],
    }

    # Try to read existing args file
    if os.path.exists(ARGS_PATH):
        try:
            with open(ARGS_PATH, "r") as f:
                args_data = json.load(f)
        except Exception:
            pass

    # Update tags from the given new tags
    if "tags" not in args_data:
        args_data["tags"] = []

    for tag in new_tags:
        if tag and tag not in args_data["tags"]:
            args_data["tags"].append(tag)

    # Ensure types are correct
    args_data["types"] = ["note", "task"]

    # Write back to file
    with open(ARGS_PATH, "w") as f:
        json.dump(args_data, f, indent=2)
