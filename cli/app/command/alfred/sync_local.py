import os
import subprocess
import shutil
import zipfile
import click

# Configuration
ALFRED_PREFS = os.path.expanduser("~/Documents/Alfred.alfredpreferences")
TMP_DIR = "tmp"  # Changed to use local tmp directory
REPO = "armoucar/alfred-preferences"


def get_latest_release_zip():
    """Download the latest release zip from GitHub."""
    try:
        # Get the latest release information
        response = subprocess.check_output(
            ["gh", "release", "view", "--json", "assets", "--repo", REPO], text=True
        ).strip()

        if not response:
            print("No releases found.")
            return None

        # Parse the JSON response to find the zip asset
        import json

        release_info = json.loads(response)
        assets = release_info.get("assets", [])
        zip_asset = next((asset for asset in assets if asset["name"].endswith(".zip")), None)

        if not zip_asset:
            print("No zip asset found in the latest release.")
            return None

        zip_url = zip_asset["url"]
        zip_name = zip_asset["name"]

        # Download the zip file using the gh CLI
        zip_path = os.path.join(TMP_DIR, zip_name)
        subprocess.run(["gh", "release", "download", "--repo", REPO, "-p", zip_name, "-D", TMP_DIR], check=True)

        print(f"Downloaded latest release: {zip_path}")
        return zip_path
    except subprocess.CalledProcessError as e:
        print(f"Failed to get latest release: {e}")
        return None


def replace_alfred_preferences(zip_path):
    """Replace the Alfred preferences with the contents of the zip."""
    if not os.path.exists(zip_path):
        print("Error: Zip file not found!")
        return False

    # Remove the existing Alfred preferences
    if os.path.exists(ALFRED_PREFS):
        shutil.rmtree(ALFRED_PREFS)

    # Extract the new preferences
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(ALFRED_PREFS)

    print(f"Replaced Alfred preferences with contents from {zip_path}")
    return True


@click.command()
def sync_local():
    """Sync local Alfred preferences with the latest release."""
    # Ensure tmp directory exists
    os.makedirs(TMP_DIR, exist_ok=True)

    zip_path = get_latest_release_zip()
    if zip_path:
        replace_alfred_preferences(zip_path)


if __name__ == "__main__":
    sync_local()
