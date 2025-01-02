import click

from app.command import new_command
from app.command import check_prs
from app.command import new_pr


@click.group()
def cli():
    """CLI application with GitHub commands."""
    pass


cli.add_command(new_command.new)
cli.add_command(check_prs.check_prs)
cli.add_command(new_pr.new_pr)

if __name__ == "__main__":
    cli()
