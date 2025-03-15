import click

from cli.app.command.check_prs import check_prs
from cli.app.command.new_pr import new_pr
from cli.app.command.work_stats import work_stats
from cli.app.command.git_recent import git_recent
from cli.app.command.kubectl import kubectl

from cli.app.command.alfred import (
    check_auth,
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


cli.add_command(check_prs)
cli.add_command(new_pr)
cli.add_command(work_stats)
cli.add_command(git_recent)
cli.add_command(kubectl)
cli.add_command(check_auth)

alfred.add_command(release)
alfred.add_command(sync_local)
alfred.add_command(migrate_prompts)
alfred.add_command(create_prompts)
alfred.add_command(delete_prompts)
alfred.add_command(edit_prompts)
cli.add_command(alfred)

# Add notes commands
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
