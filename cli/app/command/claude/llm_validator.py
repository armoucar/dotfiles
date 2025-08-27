"""LLM-based validation for Claude Code permission test results."""

import os
from typing import Optional, Tuple, Literal
import dspy


class PermissionValidation(dspy.Signature):
    """
    Analyze Claude's response to determine if it executed or required confirmation for a command.

    allow: Indicates that the command was executed. It doesnt matter the result of the command, it might be success or failure.
    ask: Claude code will indicate that it needs permission to execute the command.
    """

    claude_response: str = dspy.InputField(
        desc="Claude's complete response text to the permission request, including any error messages"
    )
    command: str = dspy.InputField(desc="The specific command that was tested")
    stderr_output: str = dspy.InputField(
        desc="Any error messages or stderr output from the Claude process"
    )

    actual_result: Literal["allow", "ask", "timeout"] = dspy.OutputField(
        desc="Classification of what actually happened: allow (executed, failing or not), ask (requested confirmation), timeout"
    )


class ClaudePermissionValidator:
    """Validates Claude permission test results using GPT-5 mini via DSPy."""

    def __init__(self):
        self.validator = None
        self._setup_dspy()

    def _setup_dspy(self) -> None:
        """Configure DSPy with GPT-5 mini."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        # Configure GPT-5 mini with appropriate parameters
        lm = dspy.LM(
            model="gpt-5-mini-2025-08-07",
            api_key=api_key,
            temperature=1.0,
            max_tokens=20_000,
            reasoning_effort="minimal",
            verbosity="low",
        )

        dspy.settings.configure(lm=lm)
        self.validator = dspy.ChainOfThought(PermissionValidation)

    def validate_response(
        self,
        claude_response: str,
        command: str,
        expected_result: str,
        stderr: Optional[str] = None,
    ) -> Tuple[str, bool, float]:
        """
        Validate Claude's response using LLM analysis.

        Args:
            claude_response: Claude's full response text
            command: The command that was tested
            expected_result: Expected result (allow/ask/blocked)
            stderr: Optional stderr output for additional context

        Returns:
            Tuple of (actual_result, passed, confidence_score)
        """
        if not self.validator:
            raise RuntimeError("Validator not initialized - check OPENAI_API_KEY")

        try:
            # Use DSPy ChainOfThought to analyze the response
            result = self.validator(
                claude_response=claude_response or "No response",
                command=command,
                stderr_output=stderr or "No stderr",
            )

            actual_result = result.actual_result
            passed = actual_result == expected_result.lower()
            confidence = 0.9  # High confidence for LLM-based classification

            return actual_result, passed, confidence

        except Exception:
            # Return error state if LLM validation fails
            return "error", False, 0.0

    def is_available(self) -> bool:
        """Check if the LLM validator is available (API key present)."""
        return bool(os.getenv("OPENAI_API_KEY")) and self.validator is not None


# Global validator instance
_validator_instance: Optional[ClaudePermissionValidator] = None


def get_validator() -> ClaudePermissionValidator:
    """Get or create the global validator instance."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = ClaudePermissionValidator()
    return _validator_instance


def validate_claude_response(
    claude_response: str,
    command: str,
    expected_result: str,
    stderr: Optional[str] = None,
) -> Tuple[str, bool, float]:
    """
    Convenience function to validate Claude's response.

    Args:
        claude_response: Claude's response text
        command: The command that was tested
        expected_result: Expected permission result
        stderr: Optional stderr for context

    Returns:
        Tuple of (actual_result, passed, confidence_score)
    """
    validator = get_validator()
    return validator.validate_response(
        claude_response, command, expected_result, stderr
    )
