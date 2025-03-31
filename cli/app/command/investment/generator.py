import click
import os
import tempfile
import subprocess
from datetime import datetime, timedelta
from openai import OpenAI


@click.command()
@click.option("--editor", default="vim", help="Editor to use (default: vim)")
@click.option("--default-term", "-t", type=int, default=12, help="Default investment term in months if end date not specified")
def generator(editor, default_term):
    """
    Generate an investment simulation command from your notes.

    Opens an editor for you to enter investment details, then generates
    a command you can run for the 'investment simulate' tool.
    """
    # Create a temporary file for the user to edit
    temp_fd, temp_path = tempfile.mkstemp(suffix=".txt")
    try:
        # Pre-populate the file with a template
        with os.fdopen(temp_fd, 'w') as tmp:
            tmp.write(_get_template())

        # Open the editor for the user to fill in details
        click.echo(f"Opening {editor} to enter investment details...")
        click.echo("Fill in your investment details, save and close the editor when done.")

        # Run the editor and wait for it to close
        process = subprocess.run([editor, temp_path])

        if process.returncode != 0:
            click.echo(f"Error: Editor exited with code {process.returncode}")
            return

        # Read the edited content
        with open(temp_path, 'r') as tmp:
            content = tmp.read()

        # Get current date and a default end date
        today = datetime.now()
        default_end_date = today + timedelta(days=30*default_term)  # Default to X months later

        # Generate command using OpenAI with date context
        command = _generate_command(content, today, default_end_date)

        # Output the command
        click.echo("\nGenerated command:")
        click.echo(command)
        click.echo("\nCopy and run this command to simulate your investment.")

    finally:
        # Clean up the temporary file
        os.unlink(temp_path)


def _get_template():
    """Generate a template for the user to fill out"""
    return """# Investment Simulator - Command Generator
# Fill in the details below and save/close the editor to generate a command.
# Lines starting with # are comments and will be ignored.
# If dates are not specified, today's date and a default end date will be used.

Investment Type: Fixed Income CDB
Initial Amount:
Start Date:
End Date:
Annual Interest Rate:
Income Tax Rate:

# Additional notes or context (optional):

"""


def _generate_command(content, today, default_end_date):
    """Use OpenAI to generate a simulation command from the user's input"""
    try:
        client = OpenAI()

        # Format dates for the prompt
        today_str = today.strftime("%Y-%m-%d")
        default_end_str = default_end_date.strftime("%Y-%m-%d")

        # Craft the system message
        system_message = """
        You are a financial command generator assistant. Your task is to extract key parameters from user input
        and generate a CLI command for an investment simulation tool.

        Your output must be ONLY the command line, nothing else. Do not include explanations, notes, or any text
        besides the command itself.
        """

        # Craft the user prompt
        user_prompt = f"""
        Based on the following investment details, generate a CLI command using the 'dot investment simulate' tool.

        The command should have these parameters:
        -p or --principal: The initial investment amount (a number)
        -s or --start-date: Start date in YYYY-MM-DD format
        -e or --end-date: End date in YYYY-MM-DD format
        -r or --annual-rate: Annual interest rate as a percentage (a number)
        -t or --tax-rate: Tax rate as a percentage (a number)

        Context information:
        - Today's date is {today_str}
        - Default end date (if not specified) is {default_end_str}

        Use the context dates ONLY if the input doesn't specify dates. If dates are mentioned in any format in the input,
        try to extract and convert them to YYYY-MM-DD format. If a date is unclear or invalid, use the context dates.

        If any of these parameters cannot be found in the input, replace it with <placeholder> in the command.

        Here is the investment information:
        ```
        {content}
        ```

        Output ONLY the command, nothing else. The format should be:
        dot investment simulate -p <amount> -s <start-date> -e <end-date> -r <rate> -t <tax-rate>
        """

        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # Low temperature for more deterministic output
            max_tokens=100,  # Short response
        )

        # Return just the command
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error generating command: {str(e)}\nRun 'dot investment simulate --help' to see required parameters."
