import click
import subprocess
from typing import List, Tuple

DEFAULT_REPOS = [
    "neon/cros-chnls.hermes",
    "neon/neon.gugelmin-chat-front",
    "neon/neon.gugelmin-ingestion-pipeline-worker",
    "neon/neon.gugelmin",
    "neon/neon.neo-cli",
]


def get_prs_for_repo(repo: str, verbose: bool = False) -> List[Tuple[str, ...]]:
    """Get PRs for a specific repository using gh CLI."""
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
    try:
        if verbose:
            click.secho(f"Running: {' '.join(cmd)}", fg="blue")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if not result.stdout:
            return []
        return [tuple(line.split("\t")) for line in result.stdout.strip().split("\n")]
    except subprocess.CalledProcessError:
        click.echo(f"Error fetching PRs for {repo}", err=True)
        return []


@click.command(name="check-prs")
@click.option("--repos", "-r", multiple=True, help="Repositories to check (format: owner/repo)")
@click.option("--verbose", is_flag=True, help="Print commands being executed")
def check_prs(repos: Tuple[str, ...], verbose: bool):
    """Check open pull requests across repositories."""
    repositories = list(repos) if repos else DEFAULT_REPOS

    # Header for the output
    headers = ["Repository", "PR Number", "Title", "Branch", "Created At", "Updated At", "URL"]

    # Collect all PRs
    all_prs = []
    with click.progressbar(repositories, label="Fetching PRs") as repos_progress:
        for repo in repos_progress:
            prs = get_prs_for_repo(repo, verbose)
            all_prs.extend(prs)

    if not all_prs:
        click.echo("No open pull requests found.")
        return

    # Calculate column widths
    widths = [max(len(str(row[i])) for row in [headers] + all_prs) for i in range(len(headers))]

    # Print header
    header_format = "  ".join(f"{header:<{width}}" for header, width in zip(headers, widths))
    click.echo(header_format)
    click.echo("-" * len(header_format))

    # Print PRs
    for pr in all_prs:
        row_format = "  ".join(f"{str(cell):<{width}}" for cell, width in zip(pr, widths))
        click.echo(row_format)
