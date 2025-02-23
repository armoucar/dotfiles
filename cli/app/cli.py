import click

from app.command import check_prs
from app.command import new_pr
from app.command import work_stats
from app.command import xls_files
from app.command.alfred import check_auth, release, sync_local


@click.group()
def cli():
    """CLI application with GitHub commands."""
    pass


@click.group()
def notes():
    """Commands for managing notes."""
    pass


@click.group()
def alfred():
    """Commands for managing Alfred preferences."""
    pass


cli.add_command(check_prs.check_prs)
cli.add_command(new_pr.new_pr)
cli.add_command(work_stats.work_stats)
cli.add_command(xls_files.xls_files)

alfred.add_command(check_auth.check_auth)
alfred.add_command(release.release)
alfred.add_command(sync_local.sync_local)
cli.add_command(alfred)

if __name__ == "__main__":
    cli()
