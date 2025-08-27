"""Test runner for Claude Code permission validation."""

import asyncio
from textwrap import dedent
import random
import time
from typing import List, Optional, Tuple
import click

from .test_cases import TestCase
from .utils import get_global_settings
from .llm_validator import validate_claude_response


class TestResult:
    """Result of a permission test."""

    def __init__(
        self,
        test_case: TestCase,
        actual_result: str,
        passed: bool,
        duration: float,
        error: Optional[str] = None,
        timeout: bool = False,
        confidence: float = 0.0,
    ):
        self.test_case = test_case
        self.actual_result = actual_result
        self.passed = passed
        self.duration = duration
        self.error = error
        self.timeout = timeout
        self.confidence = confidence

    @property
    def expected_result(self) -> str:
        return self.test_case["expected"]

    @property
    def command(self) -> str:
        return self.test_case["command"]

    @property
    def category(self) -> str:
        return self.test_case["category"]

    @property
    def description(self) -> str:
        return self.test_case["description"]


class PermissionTestRunner:
    """Runs permission tests in parallel using LLM-based validation."""

    def __init__(self, model: str = "haiku", parallel: int = 10, timeout: float = 60.0):
        self.model = model
        self.parallel = parallel
        self.timeout = timeout
        self.results: List[TestResult] = []

    async def run_single_test(self, test_case: TestCase) -> TestResult:
        """Run a single permission test."""
        start_time = time.time()

        # Create a test prompt that will trigger the permission system
        prompt = dedent(f"""
        Execute: `{test_case["command"]}`.

        1. Don't execute anything else before.
        2. Don't search anything else before.
        3. You can test it by calling the Bash tool.
        4. Assume the tool I asked you to execute is installed and even if you can't locate it, execute the command anyway to receive the error result.
        """)

        # Use claude in print mode with specified model
        cmd = ["claude", "-p", "--model", self.model, "--output-format", "json", prompt]

        try:
            # Run the command with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE,
            )

            # Send empty input to avoid hanging on interactive prompts
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=b"\n"), timeout=self.timeout
            )

            duration = time.time() - start_time

            # Parse the result using LLM validation
            stdout_str = stdout.decode("utf-8", errors="ignore")
            stderr_str = stderr.decode("utf-8", errors="ignore")

            # Use LLM validation to analyze Claude's response
            actual_result, passed, confidence = self._analyze_claude_response(
                stdout_str, stderr_str, test_case["command"], test_case["expected"]
            )

            return TestResult(
                test_case=test_case,
                actual_result=actual_result,
                passed=passed,
                duration=duration,
                confidence=confidence,
            )

        except asyncio.TimeoutError:
            duration = time.time() - start_time
            if process:
                try:
                    process.kill()
                    await process.wait()
                except:
                    pass

            return TestResult(
                test_case=test_case,
                actual_result="timeout",
                passed=False,
                duration=duration,
                timeout=True,
            )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_case=test_case,
                actual_result="error",
                passed=False,
                duration=duration,
                error=str(e),
            )

    def _analyze_claude_response(
        self, stdout: str, stderr: str, command: str, expected_result: str
    ) -> Tuple[str, bool, float]:
        """Analyze Claude's response using LLM validation."""
        try:
            actual_result, passed, confidence = validate_claude_response(
                claude_response=stdout,
                command=command,
                expected_result=expected_result,
                stderr=stderr if stderr else None,
            )
            return actual_result, passed, confidence
        except Exception as e:
            # Return error state if LLM validation fails
            click.echo(f"LLM validation failed: {e}", err=True)
            return "error", False, 0.0

    async def run_tests(
        self, test_cases: List[TestCase], progress_callback=None
    ) -> List[TestResult]:
        """Run multiple tests in parallel with optional progress callback."""
        if not test_cases:
            return []

        # Create semaphore to limit concurrent tests
        semaphore = asyncio.Semaphore(self.parallel)
        completed_count = 0
        results_lock = asyncio.Lock()
        final_results = []

        async def run_with_semaphore_and_progress(test_case: TestCase) -> TestResult:
            nonlocal completed_count
            async with semaphore:
                result = await self.run_single_test(test_case)

                # Update progress
                async with results_lock:
                    completed_count += 1
                    if progress_callback:
                        progress_callback(completed_count, len(test_cases))

                return result

        # Run all tests concurrently
        tasks = [run_with_semaphore_and_progress(test_case) for test_case in test_cases]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any exceptions that occurred
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(
                    TestResult(
                        test_case=test_cases[i],
                        actual_result="error",
                        passed=False,
                        duration=0.0,
                        error=str(result),
                    )
                )
            else:
                final_results.append(result)

        self.results = final_results
        return final_results

    def generate_report(self, results: List[TestResult]) -> str:
        """Generate a formatted test report."""
        if not results:
            return "No tests were run."

        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        failed_tests = total_tests - passed_tests

        report = []
        report.append(
            f"Test Results: {passed_tests}/{total_tests} passed ({passed_tests / total_tests * 100:.1f}%)"
        )
        report.append("")

        # Group results by category
        by_category = {}
        for result in results:
            category = result.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(result)

        # Show results by category
        for category, category_results in sorted(by_category.items()):
            category_passed = sum(1 for r in category_results if r.passed)
            report.append(
                f"{category.upper()} ({category_passed}/{len(category_results)} passed):"
            )

            for result in category_results:
                status = "✅ PASS" if result.passed else "❌ FAIL"
                if result.timeout:
                    status = "⏱️  TIMEOUT"
                elif result.error:
                    status = "💥 ERROR"

                confidence_str = (
                    f" (confidence: {result.confidence:.2f})"
                    if result.confidence > 0
                    else ""
                )
                report.append(f"  {status}: {result.command}{confidence_str}")
                if not result.passed:
                    report.append(
                        f"    Expected: {result.expected_result}, Got: {result.actual_result}"
                    )
                    if result.error:
                        report.append(f"    Error: {result.error}")
                report.append(f"    Duration: {result.duration:.2f}s")
            report.append("")

        # Summary of failures
        if failed_tests > 0:
            report.append("FAILED TESTS:")
            for result in results:
                if not result.passed:
                    report.append(f"- {result.command}")
                    report.append(
                        f"  Expected '{result.expected_result}' but got '{result.actual_result}'"
                    )
                    if result.error:
                        report.append(f"  Error: {result.error}")
            report.append("")

        return "\n".join(report)


def select_random_tests(
    all_tests: List[TestCase], count: int, seed: Optional[int] = None
) -> Tuple[List[TestCase], int]:
    """Select a random subset of tests."""
    if seed is None:
        seed = random.randint(1, 10000)

    random.seed(seed)

    if count >= len(all_tests):
        return all_tests, seed

    # Try to get a balanced selection from each category
    selected = []

    # Group by expected result to ensure we test all permission types
    by_expected = {}
    for test in all_tests:
        expected = test["expected"]
        if expected not in by_expected:
            by_expected[expected] = []
        by_expected[expected].append(test)

    # Select proportionally from each expected result type
    per_category = count // len(by_expected)
    remainder = count % len(by_expected)

    for i, (expected, tests) in enumerate(by_expected.items()):
        # Add one extra test to some categories to handle remainder
        category_count = per_category + (1 if i < remainder else 0)
        category_count = min(category_count, len(tests))

        selected.extend(random.sample(tests, category_count))

    return selected, seed


def validate_settings() -> bool:
    """Validate that Claude settings are properly configured."""
    settings = get_global_settings()
    if not settings:
        click.secho("❌ No Claude settings found at ~/.claude/settings.json", fg="red")
        return False

    permissions = settings.get("permissions")
    if not permissions:
        click.secho("❌ No permissions section found in settings", fg="red")
        return False

    required_sections = ["allow", "ask"]
    for section in required_sections:
        if section not in permissions:
            click.secho(f"❌ Missing '{section}' section in permissions", fg="red")
            return False
        if not isinstance(permissions[section], list):
            click.secho(f"❌ '{section}' section must be a list", fg="red")
            return False

    click.secho("✅ Claude settings validation passed", fg="green")
    return True
