import click
import subprocess
import os
import tempfile
import sys
import re
import uuid
from textwrap import dedent
from openai import OpenAI


def generate_filename(client, user_objectives):
    """Generate a descriptive filename using OpenAI API based on user objectives"""
    prompt = f"""Based on the following refactoring objectives, generate ONLY a descriptive filename in snake_case format.

{user_objectives}

Requirements:
- snake_case format (lowercase with underscores)
- descriptive of the refactoring goals
- suitable for a file
- concise but informative
- NO file extension
- NO extra text, explanations, or quotes

Output ONLY the filename. Example: refactor_user_authentication"""

    max_retries = 3
    for attempt in range(max_retries):
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
        )

        filename = completion.choices[0].message.content.strip()

        if is_valid_filename(filename):
            return f"{filename}.md"

        if attempt < max_retries - 1:
            # Modify prompt for retry
            prompt += f"\n\nPrevious invalid attempt: '{filename}'\nTry again with a valid snake_case filename:"

    # Fallback if all retries fail
    return "refactor_plan.md"


def is_valid_filename(filename):
    """Check if filename is valid for filesystem"""
    if not filename or len(filename) > 200:
        return False

    # Check for invalid characters
    if re.search(r'[<>:"/\\|?*\x00-\x1f]', filename):
        return False

    # Check if it's properly snake_case (lowercase letters, numbers, underscores only)
    if not re.match(r"^[a-z0-9_]+$", filename):
        return False

    # Check for reserved names
    reserved_names = {"con", "prn", "aux", "nul"}
    if filename.lower() in reserved_names:
        return False

    return True


CODE_PLAN_INSTRUCTIONS = """
First: write the list of files that are going to be created/updated. Untouched files should not be added to the list.

Second: come with a short description describing what you're going to do.

Third: You should create a detailed list of steps on how to update the code above to achieve the objectives below. Be descriptive in text, do not write any code, and make sure that you write only a direct list of steps about the changes needed to achieve the objectives.

Objectives:

1."""

DEVELOP_INSTRUCTIONS = """
Given the files above, write the code necessary to achieve the objectives below. You can make changes to files, create new files, or delete files.

Objectives:

1."""


def get_user_input():
    """Open vim for user input with git commit-like behavior"""
    # Create comment template
    comment_template = dedent("""
        # Please enter your refactoring objectives and instructions.
        # Lines starting with '#' will be ignored.
        # An empty message aborts the operation.
        #
        # Describe what you want to accomplish with the selected files:
        # - What should be refactored?
        # - What are the specific goals?
        # - Any constraints or requirements?
        #
    """).strip()

    # Create temporary file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False
    ) as temp_file:
        temp_file.write(comment_template)
        temp_file_path = temp_file.name

    try:
        # Open vim with the temporary file
        result = subprocess.run(["vim", temp_file_path])

        # Check if vim exited successfully
        if result.returncode != 0:
            click.secho("Editor was cancelled. Aborting operation.", fg="red")
            sys.exit(1)

        # Read the file and process content
        with open(temp_file_path, "r") as f:
            content = f.read()

        # Remove comment lines (lines starting with #)
        lines = content.split("\n")
        non_comment_lines = [line for line in lines if not line.strip().startswith("#")]
        processed_content = "\n".join(non_comment_lines).strip()

        # Check if there's any actual content
        if not processed_content:
            click.secho("Aborting due to empty message.", fg="red")
            sys.exit(1)

        return processed_content

    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except OSError:
            pass


def edit_final_prompt(prompt_content):
    """Open vim to edit the final prompt before submission"""
    # Create temporary file with the complete prompt
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False
    ) as temp_file:
        temp_file.write(prompt_content)
        temp_file_path = temp_file.name

    try:
        # Open vim with the temporary file
        result = subprocess.run(["vim", temp_file_path])

        # Check if vim exited successfully
        if result.returncode != 0:
            click.secho("Editor was cancelled. Using original prompt.", fg="yellow")
            return prompt_content

        # Read the edited content
        with open(temp_file_path, "r") as f:
            edited_content = f.read()

        return edited_content

    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except OSError:
            pass


@click.command(name="code")
@click.option(
    "--output-dir",
    default="tmp",
    help="Directory to save the generated output (default: tmp)",
)
@click.option(
    "--type",
    "code_type",
    default="code-plan",
    type=click.Choice(["code-plan", "develop"]),
    help="Type of code generation (default: code-plan)",
)
@click.option(
    "-e",
    "--edit",
    is_flag=True,
    help="Edit the final prompt before submitting to LLM",
)
@click.option(
    "-f",
    "--file",
    "prompt_file",
    type=click.Path(exists=True, readable=True),
    help="Use a prompt file instead of interactive mode",
)
def code(output_dir, code_type, edit, prompt_file):
    """Generate code output using LLM based on selected files or prompt file.

    This command allows you to:
    1. Select files interactively using fzf (default)
    2. Enter objectives using vim editor (default)
    3. OR use a prompt file directly with -f/--file
    4. Generate output using OpenAI o3-pro (plan or code)
    5. Save the output to a descriptively named file

    Types:
    - code-plan: Generate refactoring plan with steps
    - develop: Generate actual code changes
    """
    try:
        # Initialize OpenAI client
        client = OpenAI()
        click.secho("🤖 Initializing OpenAI client...", fg="green")

        # Handle prompt file mode vs interactive mode
        if prompt_file:
            # Prompt file mode: read the file directly
            click.secho(f"📄 Reading prompt from file: {prompt_file}", fg="blue")
            try:
                with open(prompt_file, "r") as f:
                    files_content = f.read()
                # Use the file content for filename generation (first 500 chars)
                user_objectives = (
                    files_content[500:] + "..."
                    if len(files_content) > 500
                    else files_content
                )
                # Set files list for consistent messaging
                files = [prompt_file]
            except Exception as e:
                click.secho(f"Error reading prompt file: {e}", fg="red")
                sys.exit(1)
        else:
            # Interactive mode: original workflow
            # Get files from fzf
            click.secho("📁 Select files to analyze...", fg="blue")
            try:
                files = subprocess.check_output(
                    ["fzf", "--multi"], text=True
                ).splitlines()
            except subprocess.CalledProcessError:
                click.secho("File selection cancelled. Aborting operation.", fg="red")
                sys.exit(1)

            if not files:
                click.secho("No files selected. Aborting operation.", fg="red")
                sys.exit(1)

            click.secho(f"Selected {len(files)} file(s)", fg="green")

            # Build the content string for both filename generation and main processing
            files_content = ""
            for file in files:
                try:
                    files_content += f"<{file}>\n"
                    files_content += subprocess.check_output(["cat", file], text=True)
                    files_content += f"</{file}>\n"
                except subprocess.CalledProcessError:
                    click.secho(f"Warning: Could not read file {file}", fg="yellow")
                    continue

            # Choose instructions based on type
            if code_type == "develop":
                instructions = DEVELOP_INSTRUCTIONS
            else:
                instructions = CODE_PLAN_INSTRUCTIONS

            files_content = files_content + instructions

            # Get user input via vim
            click.secho("📝 Opening editor for objectives...", fg="blue")
            user_objectives = get_user_input()
            files_content = files_content + user_objectives

        # Generate filename using OpenAI based on user objectives
        click.secho("🎯 Generating descriptive filename...", fg="blue")
        filename = generate_filename(client, user_objectives)

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Allow editing the final prompt if -e flag is set
        if edit:
            click.secho("✏️  Opening editor for final prompt...", fg="blue")
            files_content = edit_final_prompt(files_content)

        # Save the o3 prompt to /tmp for debugging
        prompt_uuid = str(uuid.uuid4())
        prompt_file_path = f"/tmp/{prompt_uuid}.txt"
        with open(prompt_file_path, "w") as f:
            f.write(files_content)
        click.secho(f"💾 Prompt saved to: {prompt_file_path}", fg="cyan")

        # Generate the main content using OpenAI API directly
        action = "plan" if code_type == "code-plan" else "code"
        click.secho(f"🚀 Generating {action} with o3-pro...", fg="blue")
        try:
            response = client.responses.create(
                model="o3-pro",
                input=[
                    {
                        "role": "developer",
                        "content": [{"type": "input_text", "text": files_content}],
                    }
                ],
                text={"format": {"type": "text"}},
                reasoning={"effort": "high", "summary": "auto"},
                tools=[],
                store=True,
            )
            result = response.output_text
        except Exception as e:
            click.secho(f"Error generating plan with OpenAI API: {e}", fg="red")
            sys.exit(1)

        # Save to generated filename in output folder
        output_path = os.path.join(output_dir, filename)
        with open(output_path, "w") as f:
            f.write(result)

        click.secho(f"✅ Output saved to: {output_path}", fg="green")
        click.secho(f"📊 Generated {action} for {len(files)} files", fg="blue")

    except KeyboardInterrupt:
        click.secho("\n⚠️  Operation cancelled by user.", fg="yellow")
        sys.exit(1)
    except Exception as e:
        click.secho(f"❌ Unexpected error: {e}", fg="red")
        sys.exit(1)
