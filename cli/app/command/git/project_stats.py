import click
import datetime
import os
import subprocess


@click.command(name="project-stats")
@click.option(
    "--since",
    default="6 months ago",
    help="Time period to gather stats from (default: '7 months ago')",
)
def project_stats(since: str):
    """Generate work statistics from git repositories."""
    author = _get_git_author()
    root_projects_folder = os.path.join(os.environ["HOME"], "dev/workspace")
    user_stats = _collect_git_stats(root_projects_folder, since, author)
    assessment_report = _generate_report(
        since, author, sorted(user_stats, key=lambda x: int(x.split("\n")[1].split(": ")[1]), reverse=True)
    )
    _save_and_display_report(assessment_report)


def _get_git_author() -> str:
    return subprocess.check_output(["git", "config", "user.email"]).decode().strip()


def _collect_git_stats(root_folder: str, since: str, author: str) -> list[str]:
    stats = []
    for project in os.listdir(root_folder):
        project_path = os.path.join(root_folder, project)
        if not _is_git_repo(project_path):
            continue

        try:
            commits = _get_commit_count(project_path, since)
            if commits <= 1:
                continue

            additions, deletions = _get_loc_changes(project_path, since, author)
            stats.append(_format_project_stats(project, commits, additions, deletions))
        except subprocess.CalledProcessError:
            click.echo(f"Warning: Failed to get git stats for {project}", err=True)

    return stats


def _is_git_repo(path: str) -> bool:
    return os.path.isdir(path) and os.path.exists(os.path.join(path, ".git"))


def _get_commit_count(project_path: str, since: str) -> int:
    result = (
        subprocess.check_output(
            ["git", "rev-list", "--count", f"--since={since}", f"--author=Arthur Moura", "main"],
            cwd=project_path,
        )
        .decode()
        .strip()
    )
    return int(result or "0")


def _get_loc_changes(project_path: str, since: str, author: str) -> tuple[int, int]:
    loc_changes = (
        subprocess.check_output(
            ["git", "log", f"--since={since}", f"--author={author}", "--pretty=tformat:", "--numstat"],
            cwd=project_path,
        )
        .decode()
        .strip()
        .split("\n")
    )

    additions = deletions = 0
    for line in loc_changes:
        parts = line.split()
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            additions += int(parts[0])
            deletions += int(parts[1])

    return additions, deletions


def _format_project_stats(project: str, commits: int, additions: int, deletions: int) -> str:
    return f"""Project: {project}
Commits: {commits}
Lines of Code Added: {additions}
Lines of Code Deleted: {deletions}
-------------------""".strip()


def _generate_report(since: str, author: str, stats: list[str]) -> str:
    return f"""
Self Assessment Report

Time Period: {since}
Author: {author}

User Git Statistics:
{chr(10).join(stats)}

End of Report
"""


def _save_and_display_report(report: str):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    base_path = os.path.join(os.environ["HOME"], ".oh-my-zsh/custom/tmp/self_assessment")
    os.makedirs(base_path, exist_ok=True)

    folder_path = os.path.join(base_path, timestamp)
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, "self_assessment.txt")

    with open(file_path, "w") as file:
        file.write(report)

    click.echo(f"Assessment report saved to {file_path}")
    click.echo("--------------")
    click.echo("Assessment Report:")
    click.echo(report)
