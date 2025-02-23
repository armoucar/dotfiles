import click

from app.command import check_prs
from app.command import new_pr
from app.command import work_stats
from app.command import xls_files


@click.group()
def cli():
    """CLI application with GitHub commands."""
    pass


@click.group()
def notes():
    """Commands for managing notes."""
    pass


@click.group()
def snippets():
    """Commands for managing code snippets."""
    pass


cli.add_command(check_prs.check_prs)
cli.add_command(new_pr.new_pr)
cli.add_command(work_stats.work_stats)
cli.add_command(xls_files.xls_files)

if __name__ == "__main__":
    cli()
