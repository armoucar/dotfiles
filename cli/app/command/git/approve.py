import click
import re
import subprocess
import json
from urllib.parse import urlparse


@click.command(name="approve")
@click.argument("pr_url", required=True)
def approve(pr_url):
    """Approve a GitHub PR and any linked PRs found in its description."""
    try:
        owner, repo, number = parse_pr_url(pr_url)

        # Fetch PR body
        body = get_pr_body(owner, repo, number)

        # Find linked PRs
        linked_prs = find_linked_prs(body, pr_url)

        if not linked_prs:
            click.secho("No linked PRs found.", fg="yellow")
        else:
            for linked in linked_prs:
                state = get_pr_state(linked)
                if state == "OPEN":
                    approve_pr(linked)
                else:
                    click.secho(f"Linked PR {linked} is not open (state={state}), skipping.", fg="yellow")

        # Finally, approve the original PR if it's open
        orig_state = get_pr_state(pr_url)
        if orig_state == "OPEN":
            approve_pr(pr_url)
        else:
            click.secho(f"Original PR {pr_url} is not open (state={orig_state}), skipping.", fg="yellow")

    except Exception as e:
        raise click.ClickException(str(e))


def parse_pr_url(pr_url):
    """
    Parse a GitHub PR URL and return (owner, repo, number).
    """
    parsed = urlparse(pr_url)
    if parsed.netloc != "github.com":
        raise ValueError(f"Not a GitHub URL: {pr_url}")
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 4 or parts[-2] != "pull":
        raise ValueError(f"Not a PR URL: {pr_url}")
    owner, repo, _, number = parts[-4], parts[-3], parts[-2], parts[-1]
    return owner, repo, int(number)


def get_pr_body(owner, repo, number):
    """
    Fetch the PR description using gh CLI and return the body text.
    """
    result = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/pulls/{number}", "--jq", ".body"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to fetch PR body: {result.stderr}")
    return result.stdout


def find_linked_prs(text, original_url):
    """
    Find GitHub PR URLs in the text, excluding the original.
    """
    pattern = re.compile(r"https://github\.com/[^/]+/[^/]+/pull/\d+")
    matches = set(pattern.findall(text))
    return [url for url in matches if url != original_url]


def get_pr_state(pr_url):
    """
    Get the PR state ('OPEN', 'CLOSED', 'MERGED') via gh CLI.
    """
    result = subprocess.run(
        ["gh", "pr", "view", pr_url, "--json", "state"], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to fetch PR state: {result.stderr}")
    data = json.loads(result.stdout)
    return data.get("state")


def approve_pr(pr_url):
    """
    Approve the PR via gh CLI with a standard 'LGTM' body.
    """
    click.secho(f"Approving PR: {pr_url}", fg="green")
    result = subprocess.run(
        ["gh", "pr", "review", pr_url, "--approve", "--body", "LGTM"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to approve PR {pr_url}: {result.stderr}")
    click.secho(result.stdout, fg="green")
