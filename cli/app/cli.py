import click
import logging
import re
import subprocess
import sys
import uuid
import tempfile

from openai import OpenAI


class CustomFormatter(logging.Formatter):
    green = "\x1b[32;20m"
    light_blue = "\x1b[94;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(message)s"

    FORMATS = {
        logging.DEBUG: light_blue + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger("pr_script")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(CustomFormatter())

logger.addHandler(handler)


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


@click.group()
def cli():
    """CLI application with GitHub commands."""
    pass


@cli.group()
def gh():
    """GitHub related commands."""
    pass


@gh.command()
def check_prs():
    """List open PRs from specified repositories."""
    # List of repositories to check
    repos = [
        "neon/cros-chnls.hermes",
        "neon/neon.gugelmin-chat-front",
        "neon/neon.gugelmin-ingestion-pipeline-worker",
        "neon/neon.gugelmin",
        "neon/neon.neo-bff",
    ]

    # Create a temporary file to store PR data
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        # Capture PRs from each repository in parallel
        processes = []
        for repo in repos:
            cmd = [
                "gh",
                "pr",
                "list",
                "--repo",
                repo,
                "--state=open",
                "--draft=false",
                "--json",
                "headRepository,number,title,headRefName,createdAt,updatedAt,url",
                "--jq",
                ".[] | [.headRepository.name, .number, .title, .headRefName, .createdAt, .updatedAt, .url] | @tsv",
            ]
            proc = subprocess.Popen(cmd, stdout=temp_file, stderr=subprocess.PIPE)
            processes.append(proc)

        # Wait for all processes to complete
        for proc in processes:
            proc.wait()

        # Add header
        temp_file.seek(0)
        content = temp_file.read()
        header = "Repository\tPR Number\tTitle\tBranch\tCreated At\tUpdated At\tURL\n"
        temp_file.seek(0)
        temp_file.write(header + content)

    # Display the results in a formatted table
    with open(temp_file.name, "r") as f:
        subprocess.run(["column", "-t", "-s", "\t"], input=f.read(), text=True)


@gh.command()
@click.option("--dry-run", is_flag=True, help="Dry run mode (default: False)")
def new_pr(dry_run):
    """Create a new PR with AI-generated title and description."""
    # Get current branch name
    current_branch = subprocess.check_output(["git", "branch", "--show-current"]).decode().strip()

    # Get default branch (usually main or master)
    default_branch = (
        subprocess.check_output(["git", "symbolic-ref", "refs/remotes/origin/HEAD"]).decode().strip().split("/")[-1]
    )

    # Get commit messages and diffs
    commit_logs = (
        subprocess.check_output(["git", "log", f"{default_branch}..{current_branch}", "--pretty=format:%s%n%b"])
        .decode()
        .strip()
    )

    # Get changed files and their content
    changed_files = (
        subprocess.check_output(["git", "diff", f"{default_branch}..{current_branch}", "--name-only"])
        .decode()
        .strip()
        .split("\n")
    )
    changed_files = [f for f in changed_files if not f.endswith(".yaml")]

    changes_content = []
    for file in changed_files:
        # Skip lock files
        if "lock" in file.lower():
            continue

        try:
            file_diff = (
                subprocess.check_output(["git", "diff", f"{default_branch}..{current_branch}", "--", file])
                .decode()
                .strip()
            )
            if file_diff:
                changes_content.append(f"Changes in {file}:\n{file_diff}\n")
        except subprocess.CalledProcessError:
            continue

    context = f"""
    Branch: {current_branch}

    Commit Messages:
    {commit_logs}

    File Changes:
    {''.join(changes_content)}
    """

    logger.info("Generating PR content...")

    prompt = PR_PROMPT_TMPL.format(context=context)

    tmp_file = f"/tmp/pr_prompt_{uuid.uuid4()}.txt"

    with open(tmp_file, "w") as f:
        f.write(prompt)

    logger.info(f"Wrote prompt to {tmp_file}")

    response = OpenAI().chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    # Extract title and body from response
    title_match = re.search(r"TITLE:\s*(.*?)(?:\n|$)", response)
    body_match = re.search(r"BODY:\s*(.*)", response, re.DOTALL)

    if not title_match or not body_match:
        logger.error("Failed to parse AI response")
        logger.error(f"Full response:\n{response}")
        logger.error(f"Title match: {title_match}")
        logger.error(f"Body match: {body_match}")
        sys.exit(1)

    title = title_match.group(1).strip()
    body = body_match.group(1).strip()

    logger.warning(f"Generated PR Title: {title}")
    logger.warning("Generated PR Body:")
    for line in body.split("\n"):
        logger.warning(line)

    if dry_run:
        logger.info("Dry run mode enabled. Skipping PR creation.")
        sys.exit(0)

    subprocess.check_output(["gh", "pr", "create", "--title", title, "--body", body])
    logger.info(f"PR created successfully with title: {title}")


if __name__ == "__main__":
    cli()
