import click


@click.command()
def new():
    """Create a new item."""
    click.echo("Creating new item...")
