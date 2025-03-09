"""Watch Gugelmin and related pods."""

import click
import os
import subprocess
import time


@click.command(name="watch-gugelmin")
def watch_gugelmin():
    """Watch Gugelmin and related pods."""
    click.echo("Watching pods (Press Ctrl+C to stop)...")

    try:
        while True:
            os.system("clear")

            # Execute each command and capture output
            cmd_outputs = []

            cmds = [
                ["kubectl", "get", "pods", "-n", "neon", "-l", "app.kubernetes.io/instance=gugelmin"],
                ["kubectl", "get", "pods", "-n", "neon", "-l", "app.kubernetes.io/instance=gugelmin-chat-front"],
                [
                    "kubectl",
                    "get",
                    "pods",
                    "-n",
                    "neon",
                    "-l",
                    "app.kubernetes.io/instance=gugelmin-ingestion-pipeline-worker",
                ],
                ["kubectl", "get", "pods", "-n", "cros-chnls", "-l", "app.kubernetes.io/instance=hermes"],
                [
                    "kubectl",
                    "get",
                    "pods",
                    "-n",
                    "customer-service",
                    "-l",
                    "app.kubernetes.io/instance=genesys-widget-front",
                ],
                [
                    "kubectl",
                    "get",
                    "pods",
                    "-n",
                    "customer-service",
                    "-l",
                    "app.kubernetes.io/instance=genesys-widget-api",
                ],
            ]

            for cmd in cmds:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    cmd_outputs.append(result.stdout)
                except Exception as e:
                    cmd_outputs.append(f"Error executing {' '.join(cmd)}: {str(e)}")

            # Print all outputs
            click.echo("\n\n".join(cmd_outputs))

            # Wait before refreshing
            time.sleep(10)
    except KeyboardInterrupt:
        click.echo("\nStopped watching.")
