"""Homebrew package management commands."""

import click
import subprocess
import sys
import yaml
from pathlib import Path


def run_command(command, check=True, capture_output=False):
    """Run a shell command with error handling."""
    try:
        result = subprocess.run(
            command, shell=True, check=check, capture_output=capture_output, text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running command: {command}")
        click.echo(f"Exit code: {e.returncode}")
        if capture_output:
            click.echo(f"Output: {e.stdout}")
            click.echo(f"Error: {e.stderr}")
        return None


def check_brew_installed():
    """Check if Homebrew is installed."""
    result = run_command("which brew", check=False, capture_output=True)
    return result is not None and result.returncode == 0


def install_brew():
    """Install Homebrew if not present."""
    click.echo("Installing Homebrew...")
    install_script = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    result = run_command(install_script)
    if result:
        click.echo("✓ Homebrew installed successfully")
        return True
    else:
        click.echo("✗ Failed to install Homebrew")
        return False


def load_config():
    """Load the brew configuration from YAML file."""
    config_path = Path("~/.oh-my-zsh/custom/config/brew.yaml").expanduser()

    if not config_path.exists():
        click.echo(f"✗ Config file not found: {config_path}")
        sys.exit(1)

    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        click.echo(f"✗ Error parsing config file: {e}")
        sys.exit(1)


def get_installed_packages():
    """Get list of currently installed packages and casks."""
    packages = set()
    casks = set()

    # Get installed packages
    result = run_command("brew list --formula", capture_output=True, check=False)
    if result and result.returncode == 0:
        packages = (
            set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
        )

    # Get installed casks
    result = run_command("brew list --cask", capture_output=True, check=False)
    if result and result.returncode == 0:
        casks = (
            set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
        )

    return packages, casks


def install_taps(taps):
    """Install tap repositories."""
    if not taps:
        return

    click.echo(f"Installing {len(taps)} taps...")
    for tap in taps:
        click.echo(f"  Installing tap: {tap}")
        result = run_command(f"brew tap {tap}")
        if result:
            click.echo(f"  ✓ {tap}")
        else:
            click.echo(f"  ✗ {tap}")


def install_packages(packages, installed_packages):
    """Install regular packages."""
    if not packages:
        return

    to_install = [pkg for pkg in packages if pkg not in installed_packages]

    if not to_install:
        click.echo("✓ All packages already installed")
        return

    click.echo(f"Installing {len(to_install)} packages...")
    for package in to_install:
        click.echo(f"  Installing: {package}")
        result = run_command(f"brew install {package}")
        if result:
            click.echo(f"  ✓ {package}")
        else:
            click.echo(f"  ✗ {package}")


def install_casks(casks, installed_casks):
    """Install cask packages."""
    if not casks:
        return

    to_install = [cask for cask in casks if cask not in installed_casks]

    if not to_install:
        click.echo("✓ All casks already installed")
        return

    click.echo(f"Installing {len(to_install)} casks...")
    for cask in to_install:
        click.echo(f"  Installing cask: {cask}")
        result = run_command(f"brew install --cask {cask}")
        if result:
            click.echo(f"  ✓ {cask}")
        else:
            click.echo(f"  ✗ {cask}")


def update_brew():
    """Update Homebrew and all packages."""
    click.echo("Updating Homebrew...")
    result = run_command("brew update")
    if not result:
        click.echo("✗ Failed to update Homebrew")
        return False

    click.echo("Upgrading packages...")
    result = run_command("brew upgrade")
    if not result:
        click.echo("✗ Failed to upgrade packages")
        return False

    click.echo("✓ Homebrew and packages updated successfully")
    return True


@click.command()
@click.argument("action", type=click.Choice(["install", "update"]))
def brew(action):
    """Manage Homebrew packages from YAML config."""
    # Check if brew is installed, install if needed
    if not check_brew_installed():
        if not install_brew():
            sys.exit(1)

    config = load_config()

    if action == "install":
        # Install packages from config
        installed_packages, installed_casks = get_installed_packages()

        install_taps(config.get("taps", []))
        install_packages(config.get("packages", []), installed_packages)
        install_casks(config.get("casks", []), installed_casks)

        click.echo("✓ Setup complete")

    elif action == "update":
        # Update all packages
        if update_brew():
            click.echo("✓ Update complete")
        else:
            sys.exit(1)
