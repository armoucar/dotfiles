# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a dotfiles repository for managing development tools, scripts, and configurations on macOS. The project structure is organized as a custom oh-my-zsh folder (`~/.oh-my-zsh/custom`) containing:

- **bin/**: Executable shell scripts available in PATH (git-managed)
- **bin-private/**: Private executable scripts (git-ignored)
- **cli/**: Python Click application for advanced workflows
- **config/**: Configuration files for various tools
- **zsh/**: ZSH configurations organized by category (core, tools, languages, containers, personal)
- **workflow/**: Documentation for specific workflows (see [Workflow Documentation](#workflow-documentation))
- **private/**: Git-ignored directory for secrets and private configurations

## Key Commands

### Development Environment

```bash
# Install/update Python dependencies (uses uv)
uv sync

# Reinstall the dot CLI in editable mode
uv tool install --editable .

# Check outdated dependencies (direct dependencies only)
uv tree --outdated --depth=1

# Update all dependencies
uv sync --upgrade
```

### dot CLI Usage

The `dot` command is the main entry point for advanced scripts:

```bash
# Git workflows
dot git commit          # Smart commit with telemetry
dot git new-pr          # Create a new pull request
dgc                     # Alias for dot git commit
dgp                     # Alias for dot git new-pr

# Other commands
dot alfred              # Manage Alfred preferences
dot audio              # Audio processing utilities
dot crawl              # Web crawling tools
dot kubectl            # Kubernetes operations
dot llm                # AI-powered commands
```

### Common Git Aliases

Available through git aliases (defined in `zsh/tools/git.zsh`):

- `gwip`: Git commit with "--wip-- [skip ci]" message
- `glocal-squash`: Squash local commits into one
- `gdss`: Git diff shortstat against main branch
- `inctag`: Increment and create git tags (major/minor/patch)

Available as executable scripts in `bin/`:

- `git-branches-check`: Check status of all branches
- `git-branches-prune`: Clean up old branches
- `git-file-history`: View file history

## Architecture

### ZSH Loading Order

1. `_load.zsh` is the entry point that:
   - Sets up PATH with bin and bin-private directories
   - Loads all private/*.zsh files
   - Sources CLI aliases (`dgc`, `dgp`) from `zsh/tools/dot.zsh`
   - Loads zsh files in order: core → tools → languages → containers → personal → setup

### Python CLI Structure

The CLI app (`cli/app/cli.py`) is a Click application with command groups:

- Commands are organized in `cli/app/command/` subdirectories
- Each command group may have its own cheatsheet (*.cheat files)
- Telemetry is conditionally initialized if server is available (checks `/v1/projects`)

### Executable Scripts

Scripts in `bin/` must:

- Have execute permissions (`chmod +x`)
- Use appropriate shebang (#!/bin/bash, #!/usr/bin/env python, etc.)
- Be self-contained or properly source dependencies

## Important Files

- `pyproject.toml`: Python project configuration using uv/hatchling
- `cli/app/telemetry.py`: OpenTelemetry integration with server availability check
- `_load.zsh`: Main ZSH configuration loader
- `cli/app/cli.py`: Click CLI entry point (imports may need fixing for missing modules)

## Environment Setup

### Setup Scripts

The repository includes several setup scripts in `bin/` for configuring the environment:

- **`setup-full`**: Interactive setup running all scripts with single confirmation
- **`setup-zsh-plugins`**: Install ZSH plugins (zsh-autosuggestions)  
- **`setup-cli`**: Install dot CLI using `uv tool install --editable`
- **`setup-tmux`**: Sync tmux configuration and theme
- **`setup-claude`**: Configure Claude Code hooks and notifications
- **`setup-markdownlint`**: Install global markdownlint configuration
- **`setup-chrome-profile`**: Configure default Chrome profile for automation
- **`setup-vscode-settings`**: Sync VSCode/Cursor settings
- **`setup-workspaces`**: Configure development workspaces

All setup scripts provide minimal single-line output indicating success or failure.

### Tmux Theme Installation

When setting up this environment on a new machine, install the Catppuccin tmux theme:

```bash
# Install TPM (Tmux Plugin Manager)
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm

# Install Catppuccin theme manually (more reliable)
git clone https://github.com/catppuccin/tmux.git ~/.tmux/plugins/catppuccin

# Source tmux config to apply theme
tmux source-file ~/.oh-my-zsh/custom/config/tmux.conf

# Kill and restart tmux server for theme to fully apply
tmux kill-server
```

The tmux config already includes the necessary Catppuccin mocha theme configuration.

## Workflow Documentation

The `workflow/` directory contains organized documentation for specific workflows and configurations:

### claude-code/

Claude Code hooks management and configuration workflows. See `workflow/claude-code/CLAUDE.md` for:

- Hook management (Notification, Command Logger, Stop hooks)
- Audio notification configuration
- `setup-claude.zsh` integration

### development/

Development environment setup and configuration. See `workflow/development/CLAUDE.md` for:

- Tmux configuration and theme setup
- VS Code configuration
- Development tool workflows

### tools/

System-level tools and utilities configuration. See `workflow/tools/CLAUDE.md` for:

- AeroSpace window manager setup
- Desktop organization workflows
- System productivity tools

## Markdownlint & Auto-formatting

The repository includes a `.markdownlint.json` configuration that disables line length limits (MD013). This configuration is automatically discovered by the Claude stop hook, which performs auto-formatting on modified markdown and Python files after each Claude session.

### Auto-formatting Behavior

The Claude stop hooks (`config/claude/hooks/stop/`) automatically:

- **Markdown Formatting** (`stop_markdown_formatter.py`): Fixes MD040 code block language issues and runs `markdownlint --fix`
- **Python Formatting** (`stop_python_formatter.py`): Formats Python files using `ruff format`
- **Session Notifications** (`stop_notification.py`): Plays Submarine.aiff completion sound
- **Tmux Integration** (`stop_tmux_bell.py`): Triggers tmux bell indicator for terminal notifications
- **Session Summary** (`stop_session_summary.py`): Displays completion status with file counts

All hooks run in parallel, use shared utilities for session isolation, and only process files modified during the current Claude session.

### Setup

Run `setup-markdownlint` to install the global configuration, making it available to the Claude stop hook in any directory.

## Claude Hooks System

The repository includes a comprehensive hook system for Claude Code integration:

### Available Hooks

- **Stop Hook**: Auto-formats modified files and plays completion notification
- **Notification Hook**: Plays audio notifications for various Claude events  
- **Command Logger**: Logs all Claude tool usage for analysis

### Hook Configuration

All hooks are managed in `config/claude/` and synchronized using `setup-claude`:

- Hook scripts in `config/claude/hooks/`
- Audio notifications in `config/claude/voice_notifications/`
- Settings and configuration files

## Notes

- The project uses `uv` for Python dependency management (not pip or poetry)
- Telemetry only initializes if the OpenTelemetry server is running (<http://127.0.0.1:6006>)
- The `dot` command entry point requires proper package structure (packages = ["cli"] in pyproject.toml)
- Private keys and secrets should only be placed in the `private/` directory
- Claude Code configuration is managed through `config/claude/` directory and `setup-claude`
- Markdownlint configuration in `.markdownlint.json` enables auto-formatting via Claude stop hook

## Coding Standards

- **NEVER use `Path(__file__).parent` constructions** - These create brittle location-dependent code that breaks when files are moved or imported from different contexts
- Use environment variables, configuration files, or pass paths as parameters instead
- Prefer conventional import strategies and dependency injection over file-system path calculations
