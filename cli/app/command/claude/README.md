# Claude Code Permission Testing

Test and validate Claude Code permission configurations with automated test suites.

## Quick Start

```bash
# Validate your settings
dot claude test validate

# Run 10 random tests
dot claude test random

# Test a specific command
dot claude test single "git status"

# Run all tests
dot claude test all
```

## Commands

### `dot claude test validate`

Validates your `~/.claude/settings.json` configuration file.

```bash
dot claude test validate
```

### `dot claude test random`

Runs a random subset of permission tests (default: 10 tests).

```bash
# Basic usage - runs 10 random tests across all permission types
dot claude test random

# Custom count and seed for reproducibility - run exact same 5 tests every time
dot claude test random --count 5 --seed 42

# Test only safe operations that should be auto-approved
dot claude test random --category allow --count 8

# Use more powerful model with fewer parallel processes for complex tests
dot claude test random --model sonnet --parallel 2 --timeout 30
```

### `dot claude test single`

Tests permissions for a single command.

```bash
# Test safe filesystem command - should be auto-approved
dot claude test single "ls -la"

# Test destructive operation - should require confirmation
dot claude test single "rm -rf temp/"

# Test git operation that could affect remote repo - using cheaper model
dot claude test single "git push origin main" --model haiku
```

### `dot claude test all`

Runs all 53 available test cases.

```bash
# Run complete test suite - validates all permission categories
dot claude test all

# Run with detailed output and more parallel processes for speed
dot claude test all --verbose --parallel 6
```

### `dot claude test list-cases`

Lists all available test cases organized by category.

```bash
dot claude test list-cases
```

## Options

| Option          | Description                      | Default |
|-----------------|----------------------------------|---------|
| `--count -c`    | Number of random tests           | 10      |
| `--seed -s`     | Random seed for reproducibility  | Random  |
| `--model -m`    | Claude model (haiku/sonnet/opus) | haiku   |
| `--parallel -p` | Concurrent test processes        | 10      |
| `--timeout -t`  | Timeout per test (seconds)       | 60.0    |
| `--category`    | Test category (allow/ask)        | All     |
| `--verbose -v`  | Show detailed output             | false   |

## Test Categories

- **Allow (27 tests)**: Commands that should be auto-approved
- **Ask (26 tests)**: Commands requiring user confirmation

## Examples

```bash
# Quick permission check with 5 tests - fast validation of settings
dot claude test random -c 5

# Reproducible test run - same 10 tests every time for debugging
dot claude test random --seed 1234 --count 10

# Test only operations that require user confirmation
dot claude test random --category ask

# Test single database command - should require confirmation
dot claude test single "psql -c 'SELECT * FROM users'"

# Full test suite with verbose output - comprehensive validation
dot claude test all -v

# Fast test with shorter timeout and more parallel processes
dot claude test random --timeout 30 --parallel 12
```

## Exit Codes

- `0`: All tests passed
- `1`: One or more tests failed or validation error
