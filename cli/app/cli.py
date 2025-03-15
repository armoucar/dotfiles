import click

from cli.app.command.git.prs_check import prs_check
from cli.app.command.git.new_pr import new_pr
from cli.app.command.git.project_stats import project_stats
from cli.app.command.git.changes_check import changes_check
from cli.app.command.git.auth_check import auth_check
from cli.app.command.kubectl import kubectl

from cli.app.command.alfred import (
    check_auth,
    execute_prompt,
    release,
    sync_local,
    migrate_prompts,
    create_prompts,
    delete_prompts,
    edit_prompts,
)

from cli.app.command.notes import (
    create,
    list_cmd,
    edit,
    delete,
    complete,
    incomplete,
    search,
    summary,
)

from cli.app.telemetry import initialize_telemetry


# Initialize OpenTelemetry for OpenAI instrumentation
initialize_telemetry()


@click.group()
def cli():
    """CLI application with GitHub commands."""
    pass


@click.group()
def notes():
    """Commands for managing notes and tasks."""
    pass


@click.group()
def alfred():
    """Commands for managing Alfred preferences."""
    pass


@click.group()
def git():
    """Git and GitHub related commands."""
    pass


# Add git commands to git group
git.add_command(prs_check)
git.add_command(new_pr)
git.add_command(project_stats)
git.add_command(changes_check)
git.add_command(auth_check)
cli.add_command(git)

# Add kubectl command directly to cli
cli.add_command(kubectl)

# Add alfred commands to alfred group
alfred.add_command(release)
alfred.add_command(sync_local)
alfred.add_command(migrate_prompts)
alfred.add_command(create_prompts)
alfred.add_command(delete_prompts)
alfred.add_command(edit_prompts)
alfred.add_command(execute_prompt)
alfred.add_command(check_auth)  # Keep this in alfred group since it's a different command
cli.add_command(alfred)

# Add notes commands to notes group
notes.add_command(create)
notes.add_command(list_cmd, name="list")
notes.add_command(edit)
notes.add_command(delete)
notes.add_command(complete)
notes.add_command(incomplete)
notes.add_command(search)
notes.add_command(summary)
cli.add_command(notes)

if __name__ == "__main__":
    cli()
