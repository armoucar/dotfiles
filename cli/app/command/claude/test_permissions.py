"""Command for testing Claude Code permissions."""

import asyncio
import sys
from typing import Optional

import click

from .test_cases import (
    TestCase,
    get_all_test_cases,
    get_test_cases_by_category,
    get_test_categories,
)
from .test_runner import PermissionTestRunner, select_random_tests, validate_settings
from .utils import get_global_settings


@click.group()
def test():
    """Test Claude Code permission configuration."""
    pass


@test.command()
@click.option(
    "--count", "-c", default=10, help="Number of random tests to run", type=int
)
@click.option("--seed", "-s", type=int, help="Random seed for reproducibility")
@click.option("--model", "-m", default="haiku", help="Claude model to use for testing")
@click.option(
    "--parallel", "-p", default=10, help="Number of parallel test processes", type=int
)
@click.option(
    "--timeout", "-t", default=60.0, help="Timeout per test in seconds", type=float
)
@click.option(
    "--category",
    type=click.Choice(["allow", "ask"]),
    help="Test only specific permission category",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def random(
    count: int,
    seed: Optional[int],
    model: str,
    parallel: int,
    timeout: float,
    category: Optional[str],
    verbose: bool,
):
    """Run random permission tests (default command)."""

    click.secho("Claude Code Permission Testing", fg="blue", bold=True)
    click.secho("=" * 40, fg="blue")

    # Validate settings first
    if not validate_settings():
        sys.exit(1)

    # Show configuration
    settings = get_global_settings()
    click.echo("Settings: ~/.claude/settings.json")
    click.echo(f"Model: {model}")
    click.echo(f"Parallel processes: {parallel}")
    click.echo(f"Timeout: {timeout}s")

    # Get test cases
    if category:
        all_tests = get_test_cases_by_category(category)
        click.echo(f"Category: {category} ({len(all_tests)} tests available)")
    else:
        all_tests = get_all_test_cases()
        click.echo(f"All categories ({len(all_tests)} tests available)")

    if not all_tests:
        click.secho("No test cases found!", fg="red")
        sys.exit(1)

    # Select tests to run
    selected_tests, actual_seed = select_random_tests(all_tests, count, seed)
    click.echo(f"Selected {len(selected_tests)} tests (seed: {actual_seed})")
    click.echo()

    if verbose:
        click.echo("Tests to run:")
        for test in selected_tests:
            click.echo(f"  - {test['command']} (expect: {test['expected']})")
        click.echo()

    # Run tests
    runner = PermissionTestRunner(model=model, parallel=parallel, timeout=timeout)

    # Show validation method
    click.echo("Validation method: LLM (GPT-5 mini)")

    with click.progressbar(length=len(selected_tests), label="Running tests") as bar:

        def progress_callback(completed, total):
            # Update progress bar as tests complete
            bar.pos = completed
            bar.render_progress()

        try:
            results = asyncio.run(runner.run_tests(selected_tests, progress_callback))
        except KeyboardInterrupt:
            click.secho("\nTests interrupted by user", fg="yellow")
            sys.exit(1)
        except Exception as e:
            click.secho(f"\nError running tests: {e}", fg="red")
            if verbose:
                import traceback

                traceback.print_exc()
            sys.exit(1)

    # Show results
    click.echo()
    report = runner.generate_report(results)
    click.echo(report)

    # Exit with error code if any tests failed
    failed_count = sum(1 for r in results if not r.passed)
    if failed_count > 0:
        sys.exit(1)


@test.command()
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


@test.command()
@click.option("--model", "-m", default="haiku", help="Claude model to use for testing")
@click.option(
    "--parallel", "-p", default=10, help="Number of parallel test processes", type=int
)
@click.option(
    "--timeout", "-t", default=60.0, help="Timeout per test in seconds", type=float
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def all(model: str, parallel: int, timeout: float, verbose: bool):
    """Run all available permission tests."""

    click.secho("Claude Code Permission Testing - ALL TESTS", fg="blue", bold=True)
    click.secho("=" * 50, fg="blue")

    # Validate settings first
    if not validate_settings():
        sys.exit(1)

    all_tests = get_all_test_cases()

    click.echo("Settings: ~/.claude/settings.json")
    click.echo(f"Model: {model}")
    click.echo(f"Parallel processes: {parallel}")
    click.echo(f"Timeout: {timeout}s")
    click.echo(f"Total tests: {len(all_tests)}")
    click.echo()

    if verbose:
        # Show breakdown by category
        categories = get_test_categories()
        for category in categories:
            category_tests = get_test_cases_by_category(category)
            click.echo(f"  {category}: {len(category_tests)} tests")
        click.echo()

    # Run all tests
    runner = PermissionTestRunner(model=model, parallel=parallel, timeout=timeout)

    # Show validation method
    click.echo("Validation method: LLM (GPT-5 mini)")

    with click.progressbar(length=len(all_tests), label="Running all tests") as bar:

        def progress_callback(completed, total):
            # Update progress bar as tests complete
            bar.pos = completed
            bar.render_progress()

        try:
            results = asyncio.run(runner.run_tests(all_tests, progress_callback))
        except KeyboardInterrupt:
            click.secho("\nTests interrupted by user", fg="yellow")
            sys.exit(1)
        except Exception as e:
            click.secho(f"\nError running tests: {e}", fg="red")
            if verbose:
                import traceback

                traceback.print_exc()
            sys.exit(1)

    # Show results
    click.echo()
    report = runner.generate_report(results)
    click.echo(report)

    # Exit with error code if any tests failed
    failed_count = sum(1 for r in results if not r.passed)
    if failed_count > 0:
        sys.exit(1)


@test.command()
def list_cases():
    """List all available test cases."""

    click.secho("Available Test Cases", fg="blue", bold=True)
    click.secho("=" * 30, fg="blue")

    categories = get_test_categories()

    for category in categories:
        tests = get_test_cases_by_category(category)
        click.secho(
            f"\n{category.upper()} ({len(tests)} tests):", fg="green", bold=True
        )

        for test in tests:
            click.echo(f"  • {test['command']}")
            click.echo(f"    {test['description']}")
            click.echo(f"    Expected: {test['expected']}")

    total_tests = len(get_all_test_cases())
    click.echo(f"\nTotal: {total_tests} test cases")


@test.command()
def validate():
    """Validate Claude Code settings configuration."""

    click.secho("Validating Claude Code Settings", fg="blue", bold=True)
    click.secho("=" * 40, fg="blue")

    success = validate_settings()

    if success:
        settings = get_global_settings()
        permissions = settings.get("permissions", {})

        allow_count = len(permissions.get("allow", []))
        ask_count = len(permissions.get("ask", []))
        deny_count = len(permissions.get("deny", []))

        click.echo("\nPermission Summary:")
        click.echo(f"  Allow patterns: {allow_count}")
        click.echo(f"  Ask patterns: {ask_count}")
        click.echo(f"  Deny patterns: {deny_count}")

        default_mode = permissions.get("defaultMode", "default")
        click.echo(f"  Default mode: {default_mode}")

        click.secho("\n✅ Settings are valid and ready for testing", fg="green")
    else:
        click.secho("\n❌ Settings validation failed", fg="red")
        sys.exit(1)


# Note: 'random' is the default subcommand - users can run 'dot claude test random' or just 'dot claude test' followed by other commands
