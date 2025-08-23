# Setup Scripts

Complete guide for all dotfiles setup scripts located in `bin/`.

## Quick Start

```bash
# Run full interactive setup
setup-full

# Or run individual scripts
setup-dotfiles
setup-cli
setup-tmux
setup-claude
```

## Available Scripts

### Core Setup Scripts

#### `setup-full`

**Purpose**: Interactive guide through all setup scripts  
**Usage**: `setup-full`  
**Description**: Runs all setup scripts with explanations and user confirmation for each step.

#### `setup-dotfiles`

**Purpose**: Install ZSH plugins and dependencies  
**Usage**: `setup-dotfiles`  
**What it does**:

- Clones `zsh-autosuggestions` plugin if not present
- Sets up essential ZSH functionality

#### `setup-cli`

**Purpose**: Install the `dot` CLI command  
**Usage**: `setup-cli`  
**What it does**:

- Installs the Python CLI in editable mode using pip
- Enables `dot` command for advanced workflows

#### `setup-tmux`

**Purpose**: Sync tmux configuration  
**Usage**: `setup-tmux`  
**What it does**:

- Copies `config/tmux.conf` to `~/.tmux.conf`
- Reloads tmux config if tmux is running
- Applies Catppuccin theme settings

#### `setup-claude`

**Purpose**: Configure Claude Code hooks and settings  
**Usage**: `setup-claude`  
**What it does**:

- Syncs `config/claude/` directory contents to `~/.claude/`
- Configures notification, logging, and stop hooks
- Sets up audio notifications (requires `generate_notification_voices.py`)

#### `setup-markdownlint`

**Purpose**: Install global markdownlint configuration  
**Usage**: `setup-markdownlint`  
**What it does**:

- Copies `.markdownlint.json` to `~/.markdownlint.json`
- Enables Claude stop hook to find config in any directory
- Required for automatic markdown formatting after Claude sessions

### Application Setup Scripts

#### `setup-chrome-profile`

**Purpose**: Configure default Chrome profile  
**Usage**: `setup-chrome-profile`  
**What it does**:

- Lists available Chrome profiles
- Sets default profile for browser automation
- Saves selection to `~/.chrome_profile`

#### `setup-vscode-settings`

**Purpose**: Sync VSCode/Cursor settings  
**Usage**: `setup-vscode-settings`  
**What it does**:

- Syncs editor settings and configurations
- Applies consistent development environment

#### `setup-workspaces`

**Purpose**: Configure development workspaces  
**Usage**: `setup-workspaces`  
**What it does**:

- Sets up project workspace configurations
- Organizes development environment

## Aliases

For convenience, these aliases are available in ZSH:

```bash
init-dotfiles  # → setup-dotfiles
init-cli       # → setup-cli  
init-tmux      # → setup-tmux
init-claude    # → setup-claude
```

## Setup Order Recommendations

For new machine setup, run scripts in this order:

1. **`setup-zsh-plugins`** - Core ZSH functionality
2. **`setup-cli`** - Enable dot command
3. **`setup-tmux`** - Terminal multiplexer
4. **`setup-claude`** - AI assistant integration
5. **`setup-markdownlint`** - Global markdown formatting
6. **`setup-chrome-profile`** - Browser automation
7. **`setup-vscode-settings`** - Editor configuration
8. **`setup-workspaces`** - Project organization

Or simply run `setup-full` for guided interactive setup.

## Script Structure

All setup scripts follow these conventions:

- **Location**: `bin/setup-*`
- **Permissions**: Executable (`chmod +x`)
- **Shebang**: `#!/bin/bash`
- **Naming**: `setup-<component>`
- **Headers**: Descriptive comments explaining purpose

## Manual Execution Only

These scripts are designed for **manual execution only**. They are not automatically run by `_load.zsh` or any other initialization scripts. This gives you full control over when and which components are set up.

## Error Handling

- Scripts include basic error checking
- Most failures are non-fatal and provide helpful messages
- `setup-full` allows continuing after individual script failures
- Check script output for specific error details
