"""Apply Claude Code permission templates to projects."""

import click

from .utils import (
    get_project_claude_dir,
    get_template_path,
    load_json_file,
    save_json_file,
    list_available_templates,
)


@click.command(name="permissions-apply")
@click.argument("template_name", default="development")
def permissions_apply(template_name: str):
    """Apply a permission template to the current project.

    Args:
        template_name: Name of the template to apply (default: development)
    """
    template_path = get_template_path(template_name)

    # Check if template exists
    if not template_path.exists():
        click.secho(f"Template '{template_name}' not found", fg="red")
        click.echo("Available templates:")
        for template in list_available_templates():
            click.echo(f"  - {template}")
        return

    # Create .claude directory if it doesn't exist
    project_claude_dir = get_project_claude_dir()
    project_claude_dir.mkdir(parents=True, exist_ok=True)

    # Copy template to project settings
    template_data = load_json_file(template_path)
    if not template_data:
        click.secho("Error loading template", fg="red")
        return

    project_settings_path = project_claude_dir / "settings.json"
    if save_json_file(project_settings_path, template_data):
        click.secho(
            f"Applied template '{template_name}' to current project", fg="green"
        )
        click.echo(f"Settings file: {project_settings_path}")
    else:
        click.secho("Error applying template", fg="red")
