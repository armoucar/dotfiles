"""Permission management commands for Claude Code."""

import shutil
from datetime import datetime
import click

from .utils import (
    get_claude_dir,
    get_project_claude_dir,
    get_templates_dir,
    get_template_path,
    load_json_file,
    save_json_file,
    get_global_settings,
    get_project_settings,
    list_available_templates,
    format_permission_rules,
)


@click.group()
def permissions():
    """Manage Claude Code permissions and templates."""
    pass


@permissions.command()
def list():
    """List available permission templates."""
    click.secho("Available Claude Code permission templates:", fg="blue", bold=True)
    click.echo()

    templates = list_available_templates()
    if not templates:
        click.secho("No templates found", fg="yellow")
        return

    templates_dir = get_templates_dir()
    for template_name in templates:
        template_path = templates_dir / f"{template_name}.json"
        template_data = load_json_file(template_path)

        click.secho(f"  {template_name}", fg="green", bold=True)

        if template_data and "description" in template_data:
            click.echo(f"    {template_data['description']}")

        # Show permission summary
        if template_data and "permissions" in template_data:
            perms = template_data["permissions"]
            allow_count = len(perms.get("allow", []))
            ask_count = len(perms.get("ask", []))
            deny_count = len(perms.get("deny", []))

            click.echo(
                f"    Permissions: {allow_count} allowed, {ask_count} ask, {deny_count} denied"
            )
        click.echo()


@permissions.command()
@click.argument("template_name")
def apply(template_name: str):
    """Apply a permission template to the current project."""
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


@permissions.command()
def show():
    """Show current permission configuration."""
    click.secho("Current Claude Code permissions:", fg="blue", bold=True)
    click.echo()

    # Show project settings
    project_settings = get_project_settings()
    if project_settings:
        click.secho("Project settings (.claude/settings.json):", fg="green", bold=True)
        perms = project_settings.get("permissions", {})

        default_mode = perms.get("defaultMode", "default")
        click.echo(f"Default mode: {default_mode}")

        if "allow" in perms:
            click.echo(f"Auto-approved operations ({len(perms['allow'])}):")
            click.echo(format_permission_rules(perms["allow"][:5]))
            if len(perms["allow"]) > 5:
                click.echo(f"  ... and {len(perms['allow']) - 5} more")

        if "ask" in perms:
            click.echo(f"Requires confirmation ({len(perms['ask'])}):")
            click.echo(format_permission_rules(perms["ask"][:3]))
            if len(perms["ask"]) > 3:
                click.echo(f"  ... and {len(perms['ask']) - 3} more")

        if "deny" in perms:
            click.echo(f"Denied operations ({len(perms['deny'])}):")
            click.echo(format_permission_rules(perms["deny"][:3]))
            if len(perms["deny"]) > 3:
                click.echo(f"  ... and {len(perms['deny']) - 3} more")
        click.echo()
    else:
        click.echo("No project-specific settings found")
        click.echo()

    # Show global settings
    global_settings = get_global_settings()
    if global_settings:
        click.secho("Global settings (~/.claude/settings.json):", fg="blue", bold=True)
        perms = global_settings.get("permissions", {})

        default_mode = perms.get("defaultMode", "default")
        click.echo(f"Default mode: {default_mode}")

        if "allow" in perms:
            click.echo(f"Auto-approved operations: {len(perms['allow'])} patterns")

        if "ask" in perms:
            click.echo(f"Requires confirmation: {len(perms['ask'])} patterns")

        if "deny" in perms:
            click.echo(f"Denied operations: {len(perms['deny'])} patterns")
    else:
        click.echo("No global settings found")


@permissions.command()
@click.option(
    "--backup/--no-backup", default=True, help="Create backup of current settings"
)
def reset(backup: bool):
    """Reset global permissions to default template."""
    claude_dir = get_claude_dir()
    global_settings_path = claude_dir / "settings.json"
    default_template_path = get_template_path("settings")

    if not default_template_path.exists():
        click.secho("Default template not found", fg="red")
        return

    # Create backup if requested
    if backup and global_settings_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = claude_dir / f"settings.json.backup.{timestamp}"

        try:
            shutil.copy2(global_settings_path, backup_path)
            click.secho(f"Backup created: {backup_path}", fg="yellow")
        except OSError as e:
            click.secho(f"Warning: Could not create backup: {e}", fg="yellow")

    # Apply default template
    template_data = load_json_file(default_template_path)
    if not template_data:
        click.secho("Error loading default template", fg="red")
        return

    if save_json_file(global_settings_path, template_data):
        click.secho("Global permissions reset to default", fg="green")
    else:
        click.secho("Error resetting global permissions", fg="red")
