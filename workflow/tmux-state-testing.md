# Testing the Tmux-Claude State Management System

This document explains the comprehensive test suite for the tmux-window-state and claude-start workflow.

## Quick Start

### Running All Tests

```bash
# Run all tests with verbose output
test-tmux-state

# Run tests with custom pytest arguments
test-tmux-state -k test_save_state
test-tmux-state -m "not integration"
```

### Running Tests Manually

```bash
# From the project root
pytest tests/ -v

# Run specific test file
pytest tests/test_tmux_window_state.py -v

# Run specific test
pytest tests/test_claude_start.py::TestMainFunction::test_main_success -v
```

## Test Structure

### Test Files

- **`tests/test_tmux_window_state.py`** - Tests for the main state management script
- **`tests/test_claude_start.py`** - Tests for the Claude session starter
- **`tests/conftest.py`** - Shared fixtures and mock configurations
- **`tests/fixtures/`** - Sample data files for testing

### Test Categories

#### Unit Tests (Default)

- Fast, isolated tests with mocked dependencies
- Test individual functions and classes
- No external dependencies required

#### Integration Tests (`-m integration`)

- Test complete workflows end-to-end  
- May require tmux to be available
- Test real-world scenarios

#### Slow Tests (`-m slow`)

- Tests that take longer to run
- Can be skipped with `-m "not slow"`

## What's Being Tested

### tmux-window-state Script

#### Data Models

- **State class serialization/deserialization**
  - JSON round-trip accuracy
  - Handling missing optional fields
  - Invalid JSON error handling
- **Window, Session, ClaudeBinding classes**
  - Data integrity and field validation

#### Core Functionality

- **Save State**
  - Session and window enumeration
  - Claude session binding resolution
  - Ordinal calculation for duplicate names
  - Atomic file operations
  - Cleanup of stale mappings
- **Load State**
  - Session and window recreation
  - Claude session resumption with correct UUIDs
  - Window index handling (non-zero starts)
  - Focus restoration
- **Helper Functions**
  - Tmux command parsing and error handling
  - File I/O operations
  - Current session detection

#### Edge Cases

- **Tmux State Variations**
  - Sessions starting at non-zero indices
  - Windows with special characters in names
  - Very long window names or paths
  - Duplicate window names (ordinal handling)
- **Error Conditions**
  - No tmux server running
  - Corrupted state files
  - File permission errors
  - Panes with incomplete information
- **Recovery Scenarios**
  - Missing Claude sessions during load
  - Partial restoration failures
  - Stale Claude map entries

### claude-start Script

#### Core Functionality

- **UUID Generation and Management**
  - Valid UUID format generation
  - Unique identifiers across sessions
- **Tmux Integration**
  - Session, window, and pane info extraction
  - Error handling for tmux command failures
- **Claude Map Management**
  - File creation and updates
  - Atomic write operations
  - Duplicate entry replacement
  - Preservation of other entries

#### Edge Cases

- **Environment Validation**
  - Detection of tmux session context
  - Proper error messaging
- **Special Characters**
  - Session/window names with spaces, symbols
  - Very long names
- **File Operations**
  - Handling corrupted existing maps
  - Permission errors
  - Atomic write failures

## Mock Strategy

### Tmux Command Mocking

- **subprocess.run** mocked to simulate tmux responses
- Configurable responses for different command patterns
- Error simulation for failure scenarios
- Realistic output formatting with whitespace/newlines

### File System Mocking

- **Path operations** mocked for predictable testing
- Temporary directories for file I/O tests
- Permission error simulation
- Atomic write operation verification

### External Dependencies

- **UUID generation** mocked for predictable test outcomes
- **datetime.now()** mocked for consistent timestamps
- **os.environ** patched for TMUX session simulation

## Test Fixtures

### Sample Data

- **`sample_state.json`** - Complete state with multiple sessions and Claude bindings
- **`sample_claude_map`** - Claude pane mappings with various scenarios
- **`incomplete_state_json`** - State with missing optional fields
- **`corrupted_state_json`** - Invalid JSON for error testing

### Mock Configurations

- **`mock_tmux_responses`** - Predefined tmux command outputs
- **`mock_subprocess_run`** - Configurable subprocess mocking
- **`mock_uuid4`** - Predictable UUID generation
- **`tmux_builder`** - Helper for building complex tmux responses

## Test Coverage Focus

### Critical Paths

- Complete save/load workflow
- Claude session resumption accuracy
- Error recovery and graceful failures
- File consistency and atomic operations

### Real-World Scenarios

- Multiple Claude sessions across different windows
- Session reorganization and renaming
- Server restarts and recovery
- Concurrent tmux operations

### Error Conditions

- Network/system failures during operations
- Corrupted or missing state files
- Tmux server unavailability
- File system permission issues

## Running Tests in CI/CD

The test suite is designed to be CI-friendly:

```bash
# Fast test run (skip integration tests)
pytest tests/ -m "not integration" --tb=short

# Full test run with coverage
pytest tests/ --cov=bin --cov-report=xml

# Parallel execution for speed
pytest tests/ -n auto
```

## Test Maintenance

### Adding New Tests

1. **Identify the functionality** to test (not just code coverage)
2. **Consider edge cases** and failure scenarios
3. **Use appropriate fixtures** from conftest.py
4. **Mock external dependencies** properly
5. **Test behavior, not implementation**

### Test Organization

- Group related tests in classes
- Use descriptive test names that explain the scenario
- Add docstrings for complex test scenarios
- Use parametrized tests for similar scenarios with different data

### Mock Management

- Keep mocks simple and focused
- Use shared fixtures for common mock patterns  
- Verify mock calls when behavior testing is important
- Reset mocks between tests to avoid interference

## Benefits

### Confidence in Critical Workflow

- Your important tmux-claude workflow is protected by comprehensive tests
- Refactoring and improvements can be made safely
- Edge cases that could cause data loss are covered

### Documentation Through Tests

- Tests serve as executable documentation of expected behavior
- New contributors can understand the system through test cases
- Complex scenarios are clearly demonstrated

### Regression Prevention  

- Bugs that have been fixed won't reappear
- New features won't break existing functionality
- System behavior is consistent and predictable
