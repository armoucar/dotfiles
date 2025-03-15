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


def select_prompt_with_fzf(formatted_file):
    """Open fzf to select a prompt to edit."""
    try:
        # Create FZF command with preview window, filtering only by filename
        cmd = [
            "fzf",
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

        # Extract selected file path
        if stdout.strip():  # Check if there's any output at all
            parts = stdout.strip().split("\t")
            if parts and len(parts) > 0:
                path = parts[0]
                if path and path.strip():
                    return path

        return None

    except Exception as e:
        click.echo(f"Error running fzf: {str(e)}")
        return None
    finally:
        # Clean up the temporary file
        os.unlink(formatted_file)


def edit_prompt_in_vim(file_path):
    """Open the selected prompt file in vim for editing."""
    if not file_path or not os.path.exists(file_path):
        click.echo("Invalid file path.")
        return False

    try:
        # Run vim with the selected file
        click.echo(f"Opening {os.path.basename(file_path)} in vim...")
        subprocess.run(["vim", file_path])
        click.echo(f"Finished editing: {os.path.basename(file_path)}")
        return True
    except Exception as e:
        click.echo(f"Error opening vim: {str(e)}")
        return False


@click.command()
def edit_prompts():
    """Edit Alfred prompts using interactive selection with fzf and vim."""
    click.echo("Collecting prompts...")
    prompts = collect_prompts()

    if not prompts:
        click.echo("No prompts found in the configured directories.")
        return

    click.echo(f"Found {len(prompts)} prompts. Opening selector...")
    formatted_file = format_for_fzf(prompts)

    selected_path = select_prompt_with_fzf(formatted_file)

    if not selected_path:
        click.echo("No prompt selected for editing.")
        return

    edit_prompt_in_vim(selected_path)


if __name__ == "__main__":
    edit_prompts()
