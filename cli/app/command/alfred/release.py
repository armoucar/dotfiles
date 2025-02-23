import os
import subprocess
import datetime
import shutil
import click

# Configuration
ALFRED_PREFS = os.path.expanduser("~/Documents/Alfred.alfredpreferences")
TMP_DIR = os.path.expanduser("~/tmp")
ZIP_NAME = f"AlfredBackup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
ZIP_PATH = os.path.join(TMP_DIR, ZIP_NAME)
REPO = "armoucar/alfred-preferences"

# Ensure the tmp directory exists
os.makedirs(TMP_DIR, exist_ok=True)


def zip_preferences():
    """Compress the Alfred preferences directory."""
    if not os.path.exists(ALFRED_PREFS):
        print("Error: Alfred preferences directory not found!")
        return False

    shutil.make_archive(ZIP_PATH.replace(".zip", ""), "zip", ALFRED_PREFS)
    print(f"Created backup: {ZIP_PATH}")
    return True


def get_latest_release():
    """Get the latest release tag from the local repo."""
    try:
        output = subprocess.check_output(["gh", "release", "list", "-R", REPO], text=True).strip()
        if output:
            latest_tag = output.split("\n")[0].split("\t")[2]  # Extract the latest tag
            return latest_tag
    except subprocess.CalledProcessError:
        print("No releases found. Starting from v1.0.")
    return "v1.0"


def increment_version(version):
    """Increment the version number (e.g., v1.0 -> v1.1)."""
    try:
        major, minor = map(int, version.lstrip("v").split("."))
        return f"v{major}.{minor + 1}"
    except ValueError:
        return "v1.0"


def create_github_release():
    """Create a GitHub release and upload the zip file."""
    latest_version = get_latest_release()
    print(f"Latest version: {latest_version}")
    new_version = increment_version(latest_version)

    print(f"Creating release {new_version}")
    try:
        subprocess.run(
            [
                "gh",
                "release",
                "create",
                new_version,
                ZIP_PATH,
                "-R",
                REPO,
                "-t",
                f"Backup {new_version}",
                "-n",
                "Automated backup of Alfred preferences",
            ],
            check=True,
        )
        print(f"Release {new_version} created and backup uploaded.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create release: {e}")


@click.command()
def release():
    """Create a new release of Alfred preferences."""
    if zip_preferences():
        create_github_release()


if __name__ == "__main__":
    release()
