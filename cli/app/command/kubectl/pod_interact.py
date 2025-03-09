"""Command for interacting with pods - viewing logs or executing commands in pods with a given instance label."""

import click
import os
import subprocess
from typing import Literal


@click.command(name="pod")
@click.argument("namespace")
@click.argument("instance")
@click.argument("mode", type=click.Choice(["log", "exec"]))
@click.option("--since", default="0s", help="Time duration for which to fetch logs (only used in 'log' mode)")
@click.option("--command", default="/bin/sh", help="Command to execute in the pod (only used in 'exec' mode)")
def pod_interact(namespace: str, instance: str, mode: Literal["log", "exec"], since: str, command: str):
    """
    Interact with pods with the given instance label in a namespace.

    MODE can be either 'log' (view logs) or 'exec' (execute a command in the pod).

    NAMESPACE: The Kubernetes namespace where the pods are located.

    INSTANCE: The instance label of the pods.

    NOTE: This command opens iTerm2 panes and requires iTerm2 on macOS.
    """
    if not namespace or not instance:
        click.echo("Error: namespace and instance are required")
        return

    # Check for macOS and iTerm2
    if not (os.uname().sysname == "Darwin" and "ITERM_SESSION_ID" in os.environ):
        click.echo("Error: This command only works on macOS with iTerm2")
        return

    # Get pod names
    pods_cmd = [
        "kubectl",
        "get",
        "pods",
        "-n",
        namespace,
        "-l",
        f"app.kubernetes.io/instance={instance}",
        "-o",
        "name",
    ]

    try:
        pods_result = subprocess.run(pods_cmd, capture_output=True, text=True, check=True)
        pod_names = pods_result.stdout.strip().split("\n")
    except subprocess.CalledProcessError:
        click.echo(f"Error: Failed to get pods in namespace {namespace} with instance {instance}")
        return

    if not pod_names or pod_names[0] == "":
        click.echo(f"No pods found in namespace {namespace} with instance {instance}")
        return

    # Operation mode-specific command
    if mode == "log":
        click.echo(f"Opening logs for pods with instance {instance} in namespace {namespace}...")
        cmd_template = f'kubectl logs -f {{pod}} -n {namespace} --since={since} | jq -Rc \'fromjson? // . | if type == "object" and has("@timestamp") then {{timestamp: .["@timestamp"], level: .["log.level"], message: .message}} else . end\''
    else:  # mode == "exec"
        click.echo(f"Executing '{command}' in pods with instance {instance} in namespace {namespace}...")
        cmd_template = f"kubectl exec -it {{pod}} -n {namespace} -- {command}"

    # Open each pod interaction in a new iTerm2 pane
    first = True
    for pod in pod_names:
        pod_name = pod.split("/")[-1]
        cmd = cmd_template.format(pod=pod_name)

        # Create Apple Script command based on whether this is the first pane or not
        if first:
            script = f"""
            tell application "iTerm2"
                tell current session of current window
                    write text "{cmd}"
                    tell application "System Events" to tell application process "iTerm2" to keystroke "-" using {{command down}}
                end tell
            end tell
            """
            first = False
        else:
            script = f"""
            tell application "iTerm2"
                tell current session of current window
                    set newSession to split horizontally with default profile
                    select newSession
                    write text "{cmd}"
                    tell application "System Events" to tell application process "iTerm2" to keystroke "-" using {{command down}}
                end tell
            end tell
            """

        # Execute the AppleScript
        try:
            subprocess.run(["osascript", "-e", script], check=True)
        except subprocess.CalledProcessError:
            click.echo(f"Error opening interaction for pod {pod_name}")

    # Maximize the window
    maximize_script = """
    tell application "iTerm2"
        activate
        tell current window
            set zoomed to true
        end tell
    end tell
    """

    try:
        subprocess.run(["osascript", "-e", maximize_script], check=True)
    except subprocess.CalledProcessError:
        pass
