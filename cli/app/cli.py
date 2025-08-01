import click

from cli.app.command.git import (
    prs_check,
    new_pr,
    project_stats,
    changes_check,
    auth_check,
    commit,
    approve,
    analyze_prs,
)

from cli.app.command.kubectl import (
    pod_interact,
    watch_gugelmin,
)

from cli.app.command.alfred import (
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

from cli.app.command.investment import (
    simulate,
    compare,
    generator,
)

from cli.app.command.crawl import page
from cli.app.command.audio import audio
from cli.app.command.llm import code
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


@click.group()
def kubectl():
    """Kubernetes (kubectl) commands."""
    pass


@click.group()
def crawl():
    """Crawl commands."""
    pass


@click.group()
def investment():
    """Investment simulation commands."""
    pass


@click.group()
def llm():
    """LLM and AI-powered commands."""
    pass


# Add git commands to git group
git.add_command(prs_check)
git.add_command(new_pr)
git.add_command(project_stats)
git.add_command(changes_check)
git.add_command(auth_check)
git.add_command(commit)
git.add_command(approve)
git.add_command(analyze_prs)
cli.add_command(git)


# Add alfred commands to alfred group
alfred.add_command(release)
alfred.add_command(sync_local)
alfred.add_command(migrate_prompts)
alfred.add_command(create_prompts)
alfred.add_command(delete_prompts)
alfred.add_command(edit_prompts)
alfred.add_command(execute_prompt)
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

# Add all commands to the kubectl group
kubectl.add_command(watch_gugelmin)
kubectl.add_command(pod_interact)
cli.add_command(kubectl)

# Add all commands to the crawl group
crawl.add_command(page)
cli.add_command(crawl)

# Add all commands to the investment group
investment.add_command(simulate)
investment.add_command(compare)
investment.add_command(generator)
cli.add_command(investment)

# Add audio command group
cli.add_command(audio)

# Add all commands to the llm group
llm.add_command(code)
cli.add_command(llm)

if __name__ == "__main__":
    cli()
