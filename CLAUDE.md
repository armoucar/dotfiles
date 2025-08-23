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
uv pip install -e .

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

Available through bin scripts:

- `gwip`: Git commit with "--wip-- [skip ci]" message
- `git-branches-check`: Check status of all branches
- `git-branches-prune`: Clean up old branches
- `git-file-history`: View file history

## Architecture

### ZSH Loading Order

1. `_load.zsh` is the entry point that:
   - Sets up PATH with bin and bin-public directories
   - Loads all private/*.zsh files
   - Sources CLI aliases from cli/app/command/notes/alias.zsh
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

## Notes

- The project uses `uv` for Python dependency management (not pip or poetry)
- Telemetry only initializes if the OpenTelemetry server is running (<http://127.0.0.1:6006>)
- The `dot` command entry point requires proper package structure (packages = ["cli"] in pyproject.toml)
- Private keys and secrets should only be placed in the `private/` directory
- Claude Code configuration is managed through `.claude/` directory and `setup-claude.zsh`
