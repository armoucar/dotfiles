import click
import re
import subprocess
import sys
import uuid
import json
from pathlib import Path

from openai import OpenAI


@click.command(name="new-pr")
@click.option("--dry-run", is_flag=True, help="Dry run mode (don't create PR)")
@click.option("--verbose", is_flag=True, help="Print git commands and their outputs")
@click.option(
    "--context", help="Additional context to include in the PR description generation"
)
@click.option(
    "--model", default="o3-pro", help="OpenAI model to use for PR generation (default: o3-pro)"
)
def new_pr(dry_run, verbose, context, model):
    """Create a new PR with AI-generated title and description."""
    # First push the current branch to make sure it's up to date
    current_branch = _get_branch_name(["git", "branch", "--show-current"], verbose)

    # Push the current branch
    if not _push_current_branch(current_branch, verbose):
        return

    # Get full git info now that branch is pushed
    current_branch, commit_logs, changes_content = _get_git_info(verbose)

    # Check if PR already exists for this branch
    existing_pr = _check_existing_pr(current_branch, verbose)

    git_context = f"""
    <git_info>
    Branch: {current_branch}
    </git_info>

    <commit_messages>
    {commit_logs}
    </commit_messages>

    <file_changes>
    {"".join(changes_content)}
    </file_changes>
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
    title, body = _generate_pr_content(full_context, model)

    if existing_pr:
        old_title = existing_pr["title"]
        old_body = existing_pr["body"]

        click.secho(f"Found existing PR with title: {old_title}", fg="yellow")

        # Combine old and new descriptions for a final version
        click.secho("Combining existing and new PR descriptions...", fg="green")
        title, body = _combine_pr_descriptions(old_title, old_body, title, body, model)

    click.secho(f"Generated PR Title: {title}", fg="yellow")
    click.secho("Generated PR Body:", fg="yellow")
    for line in body.split("\n"):
        click.secho(line, fg="yellow")

    if dry_run:
        if existing_pr:
            click.secho(
                f'Dry run mode enabled. Would run: gh pr edit {existing_pr["number"]} --title "{title}" --body "{body}"',
                fg="green",
            )
        else:
            click.secho(
                f'Dry run mode enabled. Would run: gh pr create --title "{title}" --body "{body}"',
                fg="green",
            )
        return

    if existing_pr:
        if verbose:
            click.secho(
                f'Running: gh pr edit {existing_pr["number"]} --title "{title}" --body "{body}"',
                fg="blue",
            )
        subprocess.check_output(
            [
                "gh",
                "pr",
                "edit",
                str(existing_pr["number"]),
                "--title",
                title,
                "--body",
                body,
            ]
        )
        click.secho(f"PR updated successfully with title: {title}", fg="green")
        # Get and display PR URL
        pr_url = (
            subprocess.check_output(
                ["gh", "pr", "view", str(existing_pr["number"]), "--json", "url"]
            )
            .decode()
            .strip()
        )
        pr_url = json.loads(pr_url)["url"]
        click.secho(f"PR URL: {pr_url}", fg="green")
    else:
        if verbose:
            click.secho(
                f'Running: gh pr create --title "{title}" --body "{body}"', fg="blue"
            )
        # Capture the output to get the PR URL
        pr_output = (
            subprocess.check_output(
                ["gh", "pr", "create", "--title", title, "--body", body]
            )
            .decode()
            .strip()
        )
        click.secho(f"PR created successfully with title: {title}", fg="green")
        # Extract and display the PR URL from the output
        pr_url = pr_output.split("\n")[-1]  # The URL is typically the last line
        click.secho(f"PR URL: {pr_url}", fg="green")


def _check_existing_pr(branch, verbose=False):
    """Check if a PR already exists for the given branch."""
    try:
        if verbose:
            click.secho(
                f"Running: gh pr list --head {branch} --json number,title,body",
                fg="blue",
            )

        result = (
            subprocess.check_output(
                ["gh", "pr", "list", "--head", branch, "--json", "number,title,body"]
            )
            .decode()
            .strip()
        )

        if verbose:
            click.secho(f"PR list result: {result}", fg="blue")

        prs = json.loads(result)

        if prs and len(prs) > 0:
            return prs[0]  # Return the first PR
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        if verbose:
            click.secho(f"Error checking for existing PR: {str(e)}", fg="red")

    return None


def _combine_pr_descriptions(old_title, old_body, new_title, new_body, model="o3-pro"):
    """Combine old and new PR descriptions using OpenAI."""
    prompt = f"""
I have an existing Pull Request with this title and description:

TITLE: {old_title}

BODY:
{old_body}

I've also generated a new version of the PR with this title and description:

TITLE: {new_title}

BODY:
{new_body}

Please create a final, improved version that combines both descriptions, keeping important information from both.
The final version should follow this format:

TITLE: A concise title for the PR
BODY: A comprehensive description combining the best elements of both versions

The body should start with the disclaimer: "✨ This document was first generated with the assistance of a Large Language Model (LLM). All content has been thoroughly revised and adjusted as necessary to ensure accuracy, conciseness and clarity before being made public."
"""

    tmp_file = Path(f"/tmp/pr_combine_prompt_{uuid.uuid4()}.txt")
    tmp_file.write_text(prompt)
    click.secho(f"Wrote combine prompt to {tmp_file}", fg="green")

    response = OpenAI().responses.create(
        model=model,
        input=[
            {
                "role": "developer",
                "content": [{"type": "input_text", "text": prompt}],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={"effort": "high", "summary": "auto"},
        tools=[],
        store=True,
    )

    response_content = response.output_text

    title_match = re.search(r"TITLE:\s*(.*?)(?:\n|$)", response_content)
    body_match = re.search(r"BODY:\s*(.*)", response_content, re.DOTALL)

    if not title_match or not body_match:
        click.secho("Failed to parse AI response for combined description", fg="red")
        click.secho("Using new title and body instead", fg="yellow")
        return new_title, new_body

    final_title = title_match.group(1).strip()
    final_body = body_match.group(1).strip()

    # Save combined content to tmp file
    result_file = Path(f"/tmp/pr_combined_content_{uuid.uuid4()}.txt")
    result_file.write_text(f"TITLE:\n{final_title}\n\nBODY:\n{final_body}")
    click.secho(f"Wrote combined PR content to {result_file}", fg="green")

    return final_title, final_body


def _get_git_info(verbose=False):
    """Get git branch and changes information."""

    current_branch = _get_branch_name(["git", "branch", "--show-current"], verbose)

    if verbose:
        click.secho(
            f"Running: git log origin/main..{current_branch} --pretty=format:%s%n%b",
            fg="blue",
        )
    commit_logs = (
        subprocess.check_output(
            ["git", "log", f"origin/main..{current_branch}", "--pretty=format:%s%n%b"]
        )
        .decode()
        .strip()
    )
    if verbose:
        click.secho(f"Commit logs:\n{commit_logs}", fg="blue")

    if verbose:
        click.secho(
            f"Running: git diff origin/main..{current_branch} --name-only", fg="blue"
        )
    changed_files = (
        subprocess.check_output(
            ["git", "diff", f"origin/main..{current_branch}", "--name-only"]
        )
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
            # Check if file has been deleted
            if verbose:
                click.secho(
                    f"Running: git diff --name-status origin/main..{current_branch} -- {file}",
                    fg="blue",
                )
            file_status = (
                subprocess.check_output(
                    [
                        "git",
                        "diff",
                        "--name-status",
                        f"origin/main..{current_branch}",
                        "--",
                        file,
                    ]
                )
                .decode()
                .strip()
            )

            # If file status starts with 'D', it means the file was deleted
            if file_status.startswith("D"):
                changes_content.append(f"File {file} was deleted\n")
                if verbose:
                    click.secho(f"File {file} was deleted", fg="blue")
                continue

            if verbose:
                click.secho(
                    f"Running: git diff origin/main..{current_branch} -- {file}",
                    fg="blue",
                )
            file_diff = (
                subprocess.check_output(
                    ["git", "diff", f"origin/main..{current_branch}", "--", file]
                )
                .decode(errors="replace")
                .strip()
            )
            if file_diff:
                changes_content.append(f"<{file}>\n{file_diff}\n</{file}>\n")
                if verbose:
                    click.secho(f"Diff for {file}:\n{file_diff}", fg="blue")
        except subprocess.CalledProcessError:
            continue

    return current_branch, commit_logs, changes_content


def _generate_pr_content(context, model="o3-pro"):
    """Generate PR content using OpenAI."""
    prompt = PR_PROMPT_TMPL.format(context=context)

    tmp_file = Path(f"/tmp/pr_prompt_{uuid.uuid4()}.txt")
    tmp_file.write_text(prompt)
    click.secho(f"Wrote prompt to {tmp_file}", fg="green")

    response = OpenAI().responses.create(
        model=model,
        input=[
            {
                "role": "developer",
                "content": [{"type": "input_text", "text": prompt}],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={"effort": "high", "summary": "auto"},
        tools=[],
        store=True,
    )

    response_content = response.output_text

    title_match = re.search(r"TITLE:\s*(.*?)(?:\n|$)", response_content)
    body_match = re.search(r"BODY:\s*(.*)", response_content, re.DOTALL)

    if not title_match or not body_match:
        click.secho("Failed to parse AI response", fg="red")
        click.secho(f"Full response:\n{response_content}", fg="red")
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


def _push_current_branch(branch, verbose=False):
    """Push the current branch to remote, handling cases where the branch doesn't exist remotely yet."""
    try:
        if verbose:
            click.secho(f"Running: git push origin {branch}", fg="blue")
        subprocess.check_output(
            ["git", "push", "origin", branch], stderr=subprocess.STDOUT
        )
        if verbose:
            click.secho(f"Successfully pushed branch {branch} to remote", fg="green")
        return True
    except subprocess.CalledProcessError as e:
        if "git push --set-upstream" in e.output.decode():
            # Branch doesn't exist on remote yet, create it
            if verbose:
                click.secho(
                    f"Running: git push --set-upstream origin {branch}", fg="blue"
                )
            subprocess.check_output(["git", "push", "--set-upstream", "origin", branch])
            if verbose:
                click.secho(
                    f"Successfully pushed and set upstream for branch {branch}",
                    fg="green",
                )
            return True
        else:
            click.secho(f"Error pushing current branch: {e.output.decode()}", fg="red")
            if not click.confirm("Continue with PR creation anyway?"):
                click.secho("Aborting PR creation", fg="red")
                return False
            return True


PR_PROMPT_TMPL = """
<context_changes>
{context}
</context_changes>

<output_examples>
Example 1:
TITLE: Add user authentication endpoints
BODY:
✨ Este documento foi originalmente gerado com a assistência de um LLM. Todo o conteúdo foi revisado e ajustado para garantir precisão, concisão e clareza antes de ser disponibilizado publicamente.

- Add login/register API endpoints
- Store user tokens in Redis
- Add request validation middleware

This adds basic auth flow needed for the mobile app.

Example 2:
TITLE: Fix memory leak in background worker
BODY:
✨ Este documento foi originalmente gerado com a assistência de um LLM. Todo o conteúdo foi revisado e ajustado para garantir precisão, concisão e clareza antes de ser disponibilizado publicamente.

- Release DB connections after job completion
- Add timeout to long-running tasks
- Log failed jobs to Sentry

Resolves OOM errors reported in production.

Example 3:
TITLE: Update dependencies to latest versions
BODY:
✨ Este documento foi originalmente gerado com a assistência de um LLM. Todo o conteúdo foi revisado e ajustado para garantir precisão, concisão e clareza antes de ser disponibilizado publicamente.

- Bump pytest from 6.2.4 to 7.0.0
- Update black to 22.3.0
- Migrate deprecated API calls

Required for security patches and new features.
</output_examples>

You are a GitHub Pull Request Creator. Follow these rules:

1. Make the description is detailed
2. Use simple language and avoid fancy terms
3. Do not use adjectives
4. Always include the disclaimer message: "✨ Este documento foi originalmente gerado com a assistência de um LLM. Todo o conteúdo foi revisado e ajustado para garantir precisão, concisão e clareza antes de ser disponibilizado publicamente."
5. Write in Brazilian Portuguese

Your role is to create a PR title and description. The description should explain what changes were made, focusing on the key modifications.

If <context_changes> has content, then this should be used as the primary context for the PR. This is what I intended to update the most and this is the most important part of the PR.

Please generate a PR title and description following the format and style of the examples above. Remember to include the disclaimer message at the start of the body:

TITLE: A single line summarizing the main changes
BODY: A few paragraphs describing the changes in detail, using markdown format
"""
