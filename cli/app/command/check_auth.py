import subprocess
import click

@click.command()
def check_auth():
    """Check if the GitHub CLI is authenticated."""
    try:
        # Run a simple gh command that requires authentication
        subprocess.run(["gh", "auth", "status"], check=True)
        print("GitHub CLI is authenticated.")
    except subprocess.CalledProcessError:
        print("GitHub CLI is not authenticated. Please run 'gh auth login' to authenticate.")


if __name__ == "__main__":
    check_auth()
