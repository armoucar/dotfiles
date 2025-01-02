import click
import re
import subprocess
import sys
import uuid
from pathlib import Path

from openai import OpenAI


@click.command()
@click.option("--dry-run", is_flag=True, help="Dry run mode (don't create PR)")
@click.option("--verbose", is_flag=True, help="Print git commands and their outputs")
def new_pr(dry_run, verbose):
    """Create a new PR with AI-generated title and description."""
    current_branch, commit_logs, changes_content = _get_git_info(verbose)

    context = f"""
    Branch: {current_branch}

    Commit Messages:
    {commit_logs}

    File Changes:
    {''.join(changes_content)}
    """

    click.secho("Generating PR content...", fg="green")
    title, body = _generate_pr_content(context)

    click.secho(f"Generated PR Title: {title}", fg="yellow")
    click.secho("Generated PR Body:", fg="yellow")
    for line in body.split("\n"):
        click.secho(line, fg="yellow")

    if dry_run:
        click.secho("Dry run mode enabled. Skipping PR creation.", fg="green")
        return

    if verbose:
        click.secho('Running: gh pr create --title "{}" --body "{}"'.format(title, body), fg="blue")
    subprocess.check_output(["gh", "pr", "create", "--title", title, "--body", body])
    click.secho(f"PR created successfully with title: {title}", fg="green")


def _get_git_info(verbose=False):
    """Get git branch and changes information."""

    current_branch = _get_branch_name(["git", "branch", "--show-current"], verbose)

    if verbose:
        click.secho(f"Running: git log origin/{current_branch}..{current_branch} --pretty=format:%s%n%b", fg="blue")
    commit_logs = (
        subprocess.check_output(["git", "log", f"origin/{current_branch}..{current_branch}", "--pretty=format:%s%n%b"])
        .decode()
        .strip()
    )
    if verbose:
        click.secho(f"Commit logs:\n{commit_logs}", fg="blue")

    if verbose:
        click.secho(f"Running: git diff origin/{current_branch}..{current_branch} --name-only", fg="blue")
    changed_files = (
        subprocess.check_output(["git", "diff", f"origin/{current_branch}..{current_branch}", "--name-only"])
        .decode()
        .strip()
        .split("\n")
    )
    if verbose:
        click.secho(f"Changed files:\n{chr(10).join(changed_files)}", fg="blue")
    changed_files = [f for f in changed_files if not f.endswith(".yaml")]

    changes_content = []
    for file in changed_files:
        if "lock" in file.lower():
            continue

        try:
            if verbose:
                click.secho(f"Running: git diff origin/{current_branch}..{current_branch} -- {file}", fg="blue")
            file_diff = (
                subprocess.check_output(["git", "diff", f"origin/{current_branch}..{current_branch}", "--", file])
                .decode()
                .strip()
            )
            if file_diff:
                changes_content.append(f"Changes in {file}:\n{file_diff}\n")
                if verbose:
                    click.secho(f"Diff for {file}:\n{file_diff}", fg="blue")
        except subprocess.CalledProcessError:
            continue

    return current_branch, commit_logs, changes_content


def _generate_pr_content(context):
    """Generate PR content using OpenAI."""
    prompt = PR_PROMPT_TMPL.format(context=context)

    tmp_file = Path(f"/tmp/pr_prompt_{uuid.uuid4()}.txt")
    tmp_file.write_text(prompt)
    click.secho(f"Wrote prompt to {tmp_file}", fg="green")

    response = (
        OpenAI()
        .chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        .choices[0]
        .message.content
    )

    title_match = re.search(r"TITLE:\s*(.*?)(?:\n|$)", response)
    body_match = re.search(r"BODY:\s*(.*)", response, re.DOTALL)

    if not title_match or not body_match:
        click.secho("Failed to parse AI response", fg="red")
        click.secho(f"Full response:\n{response}", fg="red")
        click.secho(f"Title match: {title_match}", fg="red")
        click.secho(f"Body match: {body_match}", fg="red")
        sys.exit(1)

    return title_match.group(1).strip(), body_match.group(1).strip()


def _get_branch_name(args, verbose=False):
    if verbose:
        click.secho(f"Running: {' '.join(args)}", fg="blue")
    output = subprocess.check_output(args).decode().strip()
    if verbose:
        click.secho(f"Output: {output}", fg="blue")
    return output


PR_PROMPT_TMPL = """
I want you to act as a GitHub Pull Request Creator. Follow these rules:
1. Make the output as concise as possible
2. Use simple language and avoid fancy terms
3. Do not use adjectives
4. Always include the disclaimer message: "✨ This document was first generated with the assistance of a Large Language Model (LLM). All content has been thoroughly revised and adjusted as necessary to ensure accuracy, conciseness and clarity before being made public."

Your role is to create a PR title and description based on the changes made. The description should explain what changes were made and why, focusing on the key modifications.

<output_examples>
Example 1:
TITLE: Add user authentication endpoints
BODY:
✨ This document was first generated with the assistance of a Large Language Model (LLM). All content has been thoroughly revised and adjusted as necessary to ensure accuracy, conciseness and clarity before being made public.

- Add login/register API endpoints
- Store user tokens in Redis
- Add request validation middleware

This adds basic auth flow needed for the mobile app.

Example 2:
TITLE: Fix memory leak in background worker
BODY:
✨ This document was first generated with the assistance of a Large Language Model (LLM). All content has been thoroughly revised and adjusted as necessary to ensure accuracy, conciseness and clarity before being made public.

- Release DB connections after job completion
- Add timeout to long-running tasks
- Log failed jobs to Sentry

Resolves OOM errors reported in production.

Example 3:
TITLE: Update dependencies to latest versions
BODY:
✨ This document was first generated with the assistance of a Large Language Model (LLM). All content has been thoroughly revised and adjusted as necessary to ensure accuracy, conciseness and clarity before being made public.

- Bump pytest from 6.2.4 to 7.0.0
- Update black to 22.3.0
- Migrate deprecated API calls

Required for security patches and new features.
</output_examples>

Here are the changes made in this PR:

{context}

Please generate a PR title and description following the format and style of the examples above. Remember to include the disclaimer message at the start of the body:

TITLE: A single line summarizing the main changes
BODY: A few paragraphs describing the changes in detail, using markdown format
"""
