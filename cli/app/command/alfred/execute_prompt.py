import os
import json
import tempfile
import subprocess
import click
import time
from openai import OpenAI
from pathlib import Path
from datetime import datetime

# Configuration
HOME = os.path.expanduser("~")

# Available OpenAI models
OPENAI_MODELS = [
    "o3-mini-2025-01-31",
    "gpt-4o-2024-08-06",
    "gpt-4.5-preview-2025-02-27",
    "gpt-4o-mini-2024-07-18",
    "gpt-3.5-turbo-0125"
]

# Directories to ignore when selecting files with fzf
IGNORED_DIRS = [
    "__pycache__",
    "node_modules",
    ".git",
    "venv",
    ".venv",
    "env",
    ".env",
    "dist",
    "build",
    ".idea",
    ".vscode",
]

PROMPTS_DIRS = [
    os.path.join(
        HOME,
        "Documents",
        "Alfred.alfredpreferences",
        "snippets",
        "0110--coding-prompts",
    ),
    os.path.join(
        HOME,
        "Documents",
        "Alfred.alfredpreferences",
        "snippets",
        "0120--reasoning-prompts",
    ),
]


@click.command()
@click.option("--execute", is_flag=True, help="Execute with OpenAI API instead of copying to clipboard")
@click.option("--files", help="Comma-separated list of files to include")
@click.option("--prompt-id", help="ID of the prompt to use")
@click.option("--context", help="Additional context to include")
@click.option("--model", help="OpenAI model to use")
def execute_prompt(execute, files, prompt_id, context, model):
    """Execute a prompt with selected files as context."""
    try:
        # Step 0: Select a model if executing with OpenAI
        selected_model = model
        if execute and not selected_model:
            selected_model = _select_model_with_fzf()
            if not selected_model:
                click.echo("No model selected. Exiting.")
                return
            click.echo(f"Selected model: {selected_model}")

        # Step 1: Select files if not provided
        selected_files = []
        if files:
            selected_files = files.split(",")
        else:
            selected_files = _select_files_with_fzf()

        if not selected_files:
            click.echo("No files selected. Exiting.")
            return

        click.echo(f"Selected {len(selected_files)} files as context.")

        # Step 2: Get file contents
        file_contents = _get_file_contents(selected_files)

        # Step 3: List and select a prompt if not provided
        prompt_text = ""
        if prompt_id:
            prompt_text = _get_prompt_by_id(prompt_id)
        else:
            prompts = _list_prompts()
            if not prompts:
                click.echo("No prompts found. Exiting.")
                return

            selected_prompt = _select_prompt_with_fzf(prompts)
            if not selected_prompt:
                click.echo("No prompt selected. Exiting.")
                return

            prompt_text = selected_prompt["prompt"]
            click.echo(f"Selected prompt: {selected_prompt['name']}")

        # Step 4: Get additional context if not provided
        additional_context = context
        if not additional_context:
            additional_context = _get_additional_context()
            if additional_context is None:
                click.echo("Additional context process was aborted. Exiting.")
                return

        # Step 5: Compose the full prompt
        full_prompt = _compose_full_prompt(file_contents, prompt_text, additional_context)

        # Step 6: Either copy to clipboard or execute with OpenAI
        if execute:
            # Save full prompt to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
                tmp.write(full_prompt)
                tmp_path = tmp.name

            click.echo(f"Full prompt saved to temporary file: {tmp_path}")

            # Execute with OpenAI
            click.echo("Sending request to OpenAI...")
            response = _execute_with_openai(full_prompt, selected_model)

            # Copy response to clipboard
            _copy_to_clipboard(response)

            click.echo("Response copied to clipboard.")
        else:
            # Copy full prompt to clipboard
            _copy_to_clipboard(full_prompt)
            click.echo("Full prompt has been copied to clipboard.")

    except Exception as e:
        click.echo(f"❌ Error executing prompt: {str(e)}")


def _select_files_with_fzf():
    """Select files using fzf."""
    try:
        # Base find command
        find_cmd = ["find", ".", "-type", "f", "-not", "-path", "*/\\.*"]

        # Add exclusions for each directory in IGNORED_DIRS
        for ignored_dir in IGNORED_DIRS:
            find_cmd.extend(["-not", "-path", f"*/{ignored_dir}/*"])

        fzf_cmd = ["fzf", "--multi"]

        find_process = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
        fzf_process = subprocess.Popen(fzf_cmd, stdin=find_process.stdout, stdout=subprocess.PIPE, text=True)
        find_process.stdout.close()

        output, _ = fzf_process.communicate()

        if fzf_process.returncode != 0:
            return []

        selected_files = [file.strip() for file in output.strip().split("\n") if file.strip()]
        return selected_files
    except Exception as e:
        click.echo(f"Error selecting files: {str(e)}")
        return []


def _get_file_contents(file_paths):
    """Get the contents of the selected files formatted as requested."""
    formatted_contents = []

    for file_path in file_paths:
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            formatted_content = f"<{file_path}>\n{content}\n</{file_path}>\n"
            formatted_contents.append(formatted_content)
        except Exception as e:
            click.echo(f"Error reading file {file_path}: {str(e)}")

    return "\n".join(formatted_contents)


def _list_prompts():
    """List all available prompts from Alfred snippets directories."""
    all_prompts = []

    for prompts_dir in PROMPTS_DIRS:
        if not os.path.exists(prompts_dir):
            continue

        for filename in os.listdir(prompts_dir):
            if filename.endswith('.json'):
                try:
                    file_path = os.path.join(prompts_dir, filename)
                    with open(file_path, 'r') as f:
                        data = json.load(f)

                    if 'alfredsnippet' in data and 'snippet' in data['alfredsnippet']:
                        name = data['alfredsnippet'].get('name', filename)
                        prompt = data['alfredsnippet']['snippet']
                        uid = data['alfredsnippet'].get('uid', '')

                        all_prompts.append({
                            'id': uid,
                            'name': name,
                            'prompt': prompt,
                            'path': file_path
                        })
                except Exception as e:
                    click.echo(f"Error reading prompt file {filename}: {str(e)}")

    return all_prompts


def _get_prompt_by_id(prompt_id):
    """Get a prompt by its ID."""
    prompts = _list_prompts()
    for prompt in prompts:
        if prompt['id'] == prompt_id:
            return prompt['prompt']

    raise ValueError(f"Prompt with ID {prompt_id} not found")


def _select_prompt_with_fzf(prompts):
    """Select a prompt using fzf."""
    try:
        # Create a temporary file with prompt names
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            for i, prompt in enumerate(prompts):
                tmp.write(f"{i}: {prompt['name']}\n")
            tmp_path = tmp.name

        # Use fzf to select a prompt
        fzf_cmd = ["fzf", "--height", "40%", "--reverse"]

        with open(tmp_path, 'r') as tmp_file:
            fzf_process = subprocess.Popen(fzf_cmd, stdin=tmp_file, stdout=subprocess.PIPE, text=True)
            output, _ = fzf_process.communicate()

        # Clean up the temporary file
        os.unlink(tmp_path)

        if fzf_process.returncode != 0 or not output.strip():
            return None

        # Parse the selected prompt index
        selected_index = int(output.split(':', 1)[0])
        return prompts[selected_index]
    except Exception as e:
        click.echo(f"Error selecting prompt: {str(e)}")
        return None


def _get_additional_context():
    """Get additional context using vim."""
    try:
        # Create a temporary file for editing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write("# Enter your additional context here\n# Save and exit when done\n\n")
            tmp_path = tmp.name

        # Record the modification time before opening vim
        before_mtime = os.path.getmtime(tmp_path)

        # Force vim as the editor, regardless of EDITOR environment variable
        vim_process = subprocess.run(['vim', tmp_path])

        # Check if vim exited normally (user saved and quit with :wq or similar)
        if vim_process.returncode != 0:
            click.echo("Vim was closed without saving. Aborting.")
            os.unlink(tmp_path)
            return None

        # Check if the file was modified (saved)
        after_mtime = os.path.getmtime(tmp_path)
        if before_mtime == after_mtime:
            click.echo("No changes were saved. Aborting.")
            os.unlink(tmp_path)
            return None

        # Read the edited content
        with open(tmp_path, 'r') as f:
            content = f.read()

        # Clean up
        os.unlink(tmp_path)

        # Remove the comment lines
        lines = content.split('\n')
        cleaned_lines = [line for line in lines if not line.startswith('#')]

        return '\n'.join(cleaned_lines).strip()
    except Exception as e:
        click.echo(f"Error getting additional context: {str(e)}")
        return None


def _compose_full_prompt(file_contents, prompt_text, additional_context):
    """Compose the full prompt with file contents, prompt text, and additional context."""
    parts = []

    # Add file contents
    if file_contents:
        parts.append("# Selected Files\n")
        parts.append(file_contents)
        parts.append("\n")

    # Add prompt
    parts.append("# Prompt\n")
    parts.append(prompt_text)
    parts.append("\n")

    # Add additional context
    if additional_context:
        parts.append("# Additional Context\n")
        parts.append(additional_context)

    return "\n".join(parts)


def _copy_to_clipboard(text):
    """Copy text to clipboard using pbcopy (macOS)."""
    try:
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(text.encode())
    except Exception as e:
        click.echo(f"Error copying to clipboard: {str(e)}")


def _select_model_with_fzf():
    """Select an OpenAI model using fzf."""
    try:
        # Create a temporary file with model names
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            for model in OPENAI_MODELS:
                tmp.write(f"{model}\n")
            tmp_path = tmp.name

        # Use fzf to select a model
        fzf_cmd = ["fzf", "--height", "40%", "--reverse"]

        with open(tmp_path, 'r') as tmp_file:
            fzf_process = subprocess.Popen(fzf_cmd, stdin=tmp_file, stdout=subprocess.PIPE, text=True)
            output, _ = fzf_process.communicate()

        # Clean up the temporary file
        os.unlink(tmp_path)

        if fzf_process.returncode != 0 or not output.strip():
            return None

        # Return the selected model
        return output.strip()
    except Exception as e:
        click.echo(f"Error selecting model: {str(e)}")
        return None


def _execute_with_openai(prompt, model="gpt-4o"):
    """Execute the prompt with OpenAI API."""
    try:
        client = OpenAI()

        start_time = time.time()

        # Display a timer during the API call
        timer_thread_running = True

        def display_timer():
            start = time.time()
            while timer_thread_running:
                elapsed = time.time() - start
                minutes = int(elapsed // 60)
                seconds = int(elapsed % 60)
                click.echo(f"\rWaiting for OpenAI response... {minutes:02d}:{seconds:02d}", nl=False)
                time.sleep(0.5)

        # Start the timer in a separate thread
        import threading
        timer_thread = threading.Thread(target=display_timer)
        timer_thread.daemon = True
        timer_thread.start()

        # Make the API call
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )

        # Stop the timer thread
        timer_thread_running = False
        timer_thread.join(timeout=1.0)

        # Clear the timer line
        click.echo("\r" + " " * 50 + "\r", nl=False)

        # Calculate and display elapsed time
        elapsed_time = time.time() - start_time
        click.echo(f"Response received in {elapsed_time:.2f} seconds.")

        return response.choices[0].message.content
    except Exception as e:
        click.echo(f"Error executing with OpenAI: {str(e)}")
        return f"Error: {str(e)}"


if __name__ == "__main__":
    execute_prompt()
