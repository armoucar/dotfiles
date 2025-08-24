# Markdownlint Auto-formatting in Claude Code Hooks

This document describes how the stop hook auto-formats markdown files, including handling files outside the project directory.

## Problem

When Claude Code creates or modifies files outside the current project directory (like slash commands in `~/.claude/commands/`), markdownlint would fail with:

```
RangeError: path should be a 'path.relative()'d string, but got "../../.claude/commands/file.md"
```

This happened because markdownlint was being run from the project directory with a relative path to an external file.

## Solution

The stop hook now changes to the file's directory before running markdownlint:

```python
# Handle files outside current directory
file_path = Path(md_file)
file_dir = file_path.parent
file_name = file_path.name

# Find markdownlint config relative to the file location
file_config = find_markdownlint_config(str(file_dir))

# Run markdownlint from the file's directory
result = subprocess.run(
    ["markdownlint", "-c", file_config, "--fix", file_name],
    cwd=str(file_dir),  # Change working directory
    capture_output=True,
    text=True,
)
```

## Config Discovery

The hook implements intelligent config file discovery by walking up from the file's location:

```python
def find_markdownlint_config(start_dir):
    """Find .markdownlint.json by walking up from start_dir to $HOME."""
    current_dir = Path(start_dir).resolve()
    home_dir = Path.home()
    
    while current_dir >= home_dir:
        config_file = current_dir / ".markdownlint.json"
        if config_file.exists():
            return str(config_file)
        current_dir = current_dir.parent
    
    # Fallback to $HOME config
    return str(home_dir / ".markdownlint.json")
```

This ensures:

- Files in the project use the project's `.markdownlint.json`
- Files outside the project use `~/.markdownlint.json`
- The global config at `$HOME` serves as fallback

## File Locations

### Project Files

- **Location**: Within `/Users/U003877/.oh-my-zsh/custom/`
- **Config**: Uses project's `.markdownlint.json`
- **Example**: `workflow/claude-code/hooks-management.md`

### External Files

- **Location**: Outside the project (e.g., `~/.claude/commands/`)
- **Config**: Uses `$HOME/.markdownlint.json`
- **Example**: `/Users/U003877/.claude/commands/c-tmux-command.md`

## Setup Requirements

1. **Global Config**: Run `setup-markdownlint` to install global config:

   ```bash
   ./bin/setup-markdownlint
   ```

2. **Project Config**: The project's `.markdownlint.json` is already in place

3. **Hook Installation**: Ensure hooks are synced:

   ```bash
   ./setup-claude.zsh
   ```

## Configuration

Both configs disable line length limits for flexibility:

```json
{
  "default": true,
  "MD013": false
}
```

## Testing

To test the auto-formatting:

1. Modify a markdown file in the project
2. Modify a markdown file outside (e.g., create a slash command)
3. When Claude Code completes (Stop event), both should be formatted

## Troubleshooting

### Files Not Being Formatted

1. Check if file was actually modified in the session:

   ```bash
   jq -r 'select(.session_id == "current_session_id") | .metadata.file_paths[]' .claude/command.log
   ```

2. Verify markdownlint is installed:

   ```bash
   which markdownlint
   ```

3. Test markdownlint manually:

   ```bash
   cd /path/to/file/directory
   markdownlint -c ~/.markdownlint.json --fix filename.md
   ```

### Config Not Found

The hook will always find a config if `~/.markdownlint.json` exists. Ensure global config is installed:

```bash
ls -la ~/.markdownlint.json
```

## Benefits

- **Consistent Formatting**: All markdown files get formatted automatically
- **No Manual Intervention**: Happens transparently on session completion
- **Cross-Directory Support**: Works for files anywhere on the system
- **Session Isolation**: Only formats files modified in current session
