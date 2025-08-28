"""Single command testing for Claude Code permissions."""

import asyncio
import sys

import click

from .test_cases import TestCase
from .test_runner import PermissionTestRunner, validate_settings


@click.command()
@click.argument("command")
@click.option("--model", "-m", default="haiku", help="Claude model to use for testing")
@click.option("--timeout", "-t", default=60.0, help="Timeout in seconds", type=float)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def single(command: str, model: str, timeout: float, verbose: bool):
    """Test a single command's permissions."""

    click.secho(f"Testing single command: {command}", fg="blue", bold=True)
    click.echo(f"Model: {model}")
    click.echo(f"Timeout: {timeout}s")
    click.echo()

    # Validate settings first
    if not validate_settings():
        sys.exit(1)

    # Create a test case for the single command
    test_case: TestCase = {
        "command": command,
        "expected": "unknown",  # We don't know what to expect
        "category": "manual",
        "description": "Manual test case",
    }

    # Run the test
    runner = PermissionTestRunner(model=model, parallel=1, timeout=timeout)

    # Show validation method
    click.echo("Validation method: LLM (GPT-5 mini)")

    try:
        click.echo("Running test...")
        results = asyncio.run(runner.run_tests([test_case]))
        result = results[0]

        click.echo()
        if result.timeout:
            click.secho("⏱️  Test timed out", fg="yellow")
        elif result.error:
            click.secho(f"💥 Test error: {result.error}", fg="red")
        else:
            click.secho("✅ Test completed", fg="green")

        click.echo(f"Result: {result.actual_result}")
        click.echo(f"Duration: {result.duration:.2f}s")

        if verbose and (result.error or result.timeout):
            click.echo("\nDetailed output available - check Claude Code logs")

    except KeyboardInterrupt:
        click.secho("\nTest interrupted by user", fg="yellow")
        sys.exit(1)
    except Exception as e:
        click.secho(f"\nError running test: {e}", fg="red")
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)
