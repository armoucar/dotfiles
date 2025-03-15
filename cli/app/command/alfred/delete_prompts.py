import os
import json
import subprocess
import click
import tempfile
from concurrent.futures import ThreadPoolExecutor

# Configuration
HOME = os.path.expanduser("~")
PROMPTS_DIRS = [
    os.path.join(HOME, "Documents", "Alfred.alfredpreferences", "snippets", "0110--coding-prompts"),
    os.path.join(HOME, "Documents", "Alfred.alfredpreferences", "snippets", "0120--reasoning-prompts"),
]


def get_snippet_info(filepath):
    """Extract snippet information from a JSON file."""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            snippet = data.get("alfredsnippet", {})
            name = snippet.get("name", "Unknown")
            content = snippet.get("snippet", "")
            return {"name": name, "content": content, "path": filepath}
    except Exception:
        return {"name": "Error", "content": "Could not read file", "path": filepath}


def collect_prompts():
    """Collect all prompts from the configured directories."""
    prompts = []

    for dir_path in PROMPTS_DIRS:
        if os.path.exists(dir_path):
            with ThreadPoolExecutor() as executor:
                futures = []
                for filename in os.listdir(dir_path):
                    if filename.endswith(".json"):
                        filepath = os.path.join(dir_path, filename)
                        futures.append(executor.submit(get_snippet_info, filepath))

                for future in futures:
                    prompts.append(future.result())

    return prompts


def format_for_fzf(prompts):
    """Format prompt information for fzf preview."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w")

    for prompt in prompts:
        # Skip prompts with empty content or name
        if not prompt["name"].strip() or not prompt["content"].strip():
            continue

        # Get filename from path
        filename = os.path.basename(prompt["path"])
        # Create a preview-friendly format without blank lines
        preview = f"{prompt['name']}: {prompt['content']}".replace("\n", " ")
        # Write to temp file with the path as identifier and filename as the search term
        temp_file.write(f"{prompt['path']}\t{filename}\t{preview}\n")

    temp_file.close()
    return temp_file.name


def select_prompts_with_fzf(formatted_file):
    """Open fzf to select prompts to delete."""
    try:
        # Create FZF command with preview window, filtering only by filename
        cmd = [
            "fzf",
            "--multi",
            "--delimiter=\\t",
            "--with-nth=2",
            "--preview",
            "echo {3}",
            "--preview-window=right:50%:wrap",
            "--height=80%",
        ]

        # Run fzf as a subprocess
        process = subprocess.Popen(cmd, stdin=open(formatted_file, "r"), stdout=subprocess.PIPE, text=True)

        stdout, _ = process.communicate()

        # Extract selected file paths, carefully handling blank lines
        selected_paths = []
        if stdout.strip():  # Check if there's any output at all
            for line in stdout.strip().split("\n"):
                if line and line.strip():  # Double-check for blank lines
                    parts = line.split("\t")
                    if parts and len(parts) > 0:
                        path = parts[0]
                        if path and path.strip():
                            selected_paths.append(path)

        return selected_paths

    except Exception as e:
        click.echo(f"Error running fzf: {str(e)}")
        return []
    finally:
        # Clean up the temporary file
        os.unlink(formatted_file)


def delete_selected_prompts(selected_paths, dry_run=False):
    """Delete the selected prompt files."""
    for path in selected_paths:
        try:
            filename = os.path.basename(path)
            if dry_run:
                click.echo(f"Would delete: {filename}")
            else:
                os.remove(path)
                click.echo(f"Deleted: {filename}")
        except Exception as e:
            click.echo(f"Error deleting {filename}: {str(e)}")


@click.command()
@click.option("--dry-run", is_flag=True, help="Show what would be deleted without actually deleting")
def delete_prompts(dry_run):
    """Delete Alfred prompts using interactive selection with fzf."""
    click.echo("Collecting prompts...")
    prompts = collect_prompts()

    if not prompts:
        click.echo("No prompts found in the configured directories.")
        return

    click.echo(f"Found {len(prompts)} prompts. Opening selector...")
    formatted_file = format_for_fzf(prompts)

    selected_paths = select_prompts_with_fzf(formatted_file)

    if not selected_paths:
        click.echo("No prompts selected for deletion.")
        return

    if dry_run:
        click.echo(f"Selected {len(selected_paths)} prompts for deletion (dry run):")
    else:
        confirmation = click.confirm(f"Delete {len(selected_paths)} selected prompts?")
        if not confirmation:
            click.echo("Operation cancelled.")
            return

    delete_selected_prompts(selected_paths, dry_run)

    if not dry_run:
        click.echo(f"Successfully deleted {len(selected_paths)} prompts.")


if __name__ == "__main__":
    delete_prompts()
