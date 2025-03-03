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
@click.option("--context", help="Additional context to include in the PR description generation")
def new_pr(dry_run, verbose, context):
    """Create a new PR with AI-generated title and description."""
    current_branch, commit_logs, changes_content = _get_git_info(verbose)

    git_context = f"""
    Branch: {current_branch}

    Commit Messages:
    {commit_logs}

    File Changes:
    {''.join(changes_content)}
    """

    # Include additional context if provided
    if context:
        full_context = f"""
    {git_context}

    Developer Message that contextualizes the changes:
    {context}
    """
    else:
        full_context = git_context

    click.secho("Generating PR content...", fg="green")
    title, body = _generate_pr_content(full_context)

    click.secho(f"Generated PR Title: {title}", fg="yellow")
    click.secho("Generated PR Body:", fg="yellow")
    for line in body.split("\n"):
        click.secho(line, fg="yellow")

    if dry_run:
        click.secho(
            'Dry run mode enabled. Would run: gh pr create --title "{}" --body "{}"'.format(title, body), fg="green"
        )
        return

    if verbose:
        click.secho('Running: gh pr create --title "{}" --body "{}"'.format(title, body), fg="blue")

    subprocess.check_output(["gh", "pr", "create", "--title", title, "--body", body])
    click.secho(f"PR created successfully with title: {title}", fg="green")


def _get_git_info(verbose=False):
    """Get git branch and changes information."""

    current_branch = _get_branch_name(["git", "branch", "--show-current"], verbose)

    if verbose:
        click.secho(f"Running: git log origin/main..{current_branch} --pretty=format:%s%n%b", fg="blue")
    commit_logs = (
        subprocess.check_output(["git", "log", f"origin/main..{current_branch}", "--pretty=format:%s%n%b"])
        .decode()
        .strip()
    )
    if verbose:
        click.secho(f"Commit logs:\n{commit_logs}", fg="blue")

    if verbose:
        click.secho(f"Running: git diff origin/main..{current_branch} --name-only", fg="blue")
    changed_files = (
        subprocess.check_output(["git", "diff", f"origin/main..{current_branch}", "--name-only"])
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
                click.secho(f"Running: git diff origin/main..{current_branch} -- {file}", fg="blue")
            file_diff = (
                subprocess.check_output(["git", "diff", f"origin/main..{current_branch}", "--", file]).decode().strip()
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
            model="o3-mini-2025-01-31",
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

    title = title_match.group(1).strip()
    body = body_match.group(1).strip()

    # Save title and body to tmp file
    result_file = Path(f"/tmp/pr_content_{uuid.uuid4()}.txt")
    result_file.write_text(f"TITLE:\n{title}\n\nBODY:\n{body}")
    click.secho(f"Wrote PR content to {result_file}", fg="green")

    return title, body


def _get_branch_name(args, verbose=False):
    if verbose:
        click.secho(f"Running: {' '.join(args)}", fg="blue")
    output = subprocess.check_output(args).decode().strip()
    if verbose:
        click.secho(f"Output: {output}", fg="blue")
    return output


PR_PROMPT_TMPL = """
<context_changes>
{context}
</context_changes>

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

You are a GitHub Pull Request Creator. Follow these rules:

1. Make the description is detailed
2. Use simple language and avoid fancy terms
3. Do not use adjectives
4. Always include the disclaimer message: "✨ This document was first generated with the assistance of a Large Language Model (LLM). All content has been thoroughly revised and adjusted as necessary to ensure accuracy, conciseness and clarity before being made public."

Your role is to create a PR title and description based on the <context_changes>. The description should explain what changes were made, focusing on the key modifications.

Please generate a PR title and description following the format and style of the examples above. Remember to include the disclaimer message at the start of the body:

TITLE: A single line summarizing the main changes
BODY: A few paragraphs describing the changes in detail, using markdown format
"""
