import os
import json
import uuid
import click
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Configuration
HOME = os.path.expanduser("~")
SOURCE_DIR = os.path.join(HOME, "Documents", "Alfred.alfredpreferences", "snippets", "0110--coding-prompts")
DEST_DIR = os.path.join(HOME, "Documents", "Alfred.alfredpreferences", "snippets", "0120--reasoning-prompts")


def generate_uid():
    """Generate a new uppercase UUID."""
    return str(uuid.uuid4()).upper()


def transform_prompt_with_openai(original_prompt):
    """Use OpenAI to transform a coding prompt into a reasoning prompt."""
    try:
        client = OpenAI()

        # Define the system message and user prompt
        system_message = """
        You are an expert at transforming instructional prompts into reasoning prompts.
        A reasoning prompt should be concise, direct to the point, and avoid direct instructions or explicit reasoning steps.
        """

        user_prompt = f"""
        Please transform the following instructional prompt into a reasoning prompt:

        Original prompt:
        ```
        {original_prompt}
        ```

        Guidelines for the transformation:
        1. Make it concise and direct to the point
        2. Remove any direct instructions or explicit reasoning steps
        3. Focus on the core intent of the prompt
        4. Maintain the same domain expertise but simplify the framing
        5. The result should be cleaner and more focused
        6. New prompts start with "You are a <domain expert>..."
        7. The prompt should ask guidance on how to do something, not a question
        8. The prompt should finish with ":"

        Return ONLY the transformed prompt text, nothing else.
        """

        # Make the API call
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_message}, {"role": "user", "content": user_prompt}],
            temperature=0,
        )

        transformed_prompt = response.choices[0].message.content.strip()
        return transformed_prompt

    except Exception as e:
        click.echo(f"Error transforming prompt with OpenAI: {str(e)}")
        return original_prompt


def get_destination_filename(original_name):
    """Generate the destination filename based on the original name."""
    if not original_name.startswith("reason-"):
        return f"reason-{original_name}"
    return original_name


def prompt_already_exists(new_name):
    """Check if a prompt with the given name already exists in the destination folder."""
    for file in os.listdir(DEST_DIR):
        # Check if the file follows the naming pattern and extract the snippet name
        if file.endswith(".json"):
            file_name_parts = file.split(" [")
            if len(file_name_parts) > 0 and file_name_parts[0] == new_name:
                return True
    return False


def process_file(filename, dry_run=False, verbose=False):
    """Process a single file for migration."""
    result = {"status": "skipped", "original_name": None, "new_name": None, "error": None}

    source_path = os.path.join(SOURCE_DIR, filename)

    try:
        # Read the source JSON file
        with open(source_path, "r") as file:
            data = json.load(file)

        # Extract the snippet data
        snippet_data = data.get("alfredsnippet", {})
        original_snippet = snippet_data.get("snippet", "")
        original_name = snippet_data.get("name", "")
        original_keyword = snippet_data.get("keyword", "")

        result["original_name"] = original_name

        # Generate new name
        new_name = get_destination_filename(original_name)
        result["new_name"] = new_name

        # Check if this prompt already exists
        if prompt_already_exists(new_name):
            return result

        # Generate a new UID
        new_uid = generate_uid()

        # Transform the prompt using OpenAI
        if verbose:
            click.echo(f"Transforming prompt: {original_name}")

        if not dry_run:
            new_snippet = transform_prompt_with_openai(original_snippet)
        else:
            new_snippet = "[Dry run - transformation would happen here]"

        # Create new JSON data
        new_data = {
            "alfredsnippet": {
                "snippet": f"{new_snippet}\n\n",
                "uid": new_uid,
                "name": new_name,
                "keyword": original_keyword,
            }
        }

        # Create the destination filename
        dest_filename = f"{new_name} [{new_uid}].json"
        dest_path = os.path.join(DEST_DIR, dest_filename)

        if verbose:
            click.echo(f"Creating new file: {dest_path}")

        # Write the new file
        if not dry_run:
            with open(dest_path, "w") as file:
                json.dump(new_data, file, indent=2)

        result["status"] = "processed"
        return result

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        return result


@click.command()
@click.option("--sample-amount", type=int, default=10, help="Number of prompts to sample")
@click.option("--dry-run", is_flag=True, help="Show what would be done without making any changes")
@click.option("--verbose", is_flag=True, help="Show verbose output")
@click.option("--workers", type=int, default=5, help="Number of parallel workers (default: 5)")
def migrate_prompts(sample_amount, dry_run, verbose, workers):
    """Migrate Alfred coding prompts to reasoning prompts format."""
    # Ensure destination directory exists
    os.makedirs(DEST_DIR, exist_ok=True)

    if not os.path.exists(SOURCE_DIR):
        click.echo(f"Source directory not found: {SOURCE_DIR}")
        return

    # Get list of JSON files to process
    json_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".json")]

    # Limit to sample amount if specified
    if len(json_files) > sample_amount:
        json_files = json_files[:sample_amount]

    click.echo(f"Found {len(json_files)} JSON files to process")

    files_processed = 0
    files_skipped = 0
    files_errored = 0

    # Process files in parallel
    with ThreadPoolExecutor(max_workers=min(workers, len(json_files))) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(process_file, filename, dry_run, verbose): filename for filename in json_files
        }

        # Setup progress bar if not in verbose mode
        if not verbose:
            pbar = tqdm(total=len(json_files), desc="Processing prompts")

        # Process results as they complete
        for future in as_completed(future_to_file):
            filename = future_to_file[future]
            try:
                result = future.result()
                if result["status"] == "processed":
                    files_processed += 1
                    if verbose:
                        click.echo(f"Processed: {result['original_name']} → {result['new_name']}")
                elif result["status"] == "skipped":
                    files_skipped += 1
                    if verbose and result["original_name"]:
                        click.echo(f"Skipping {result['original_name']} - already exists in destination")
                else:
                    files_errored += 1
                    click.echo(f"Error processing file {filename}: {result['error']}")
            except Exception as exc:
                files_errored += 1
                click.echo(f"Error processing file {filename}: {exc}")

            # Update progress bar
            if not verbose:
                pbar.update(1)

        # Close progress bar
        if not verbose:
            pbar.close()

    click.echo(
        f"Migration complete: {files_processed} files processed, {files_skipped} files skipped, {files_errored} files errored"
    )


if __name__ == "__main__":
    migrate_prompts()
