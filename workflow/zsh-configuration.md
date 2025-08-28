# ZSH Configuration System

## Overview

The `zsh/` directory provides a modular, organized approach to ZSH shell configuration within this dotfiles repository. It replaces the traditional single `.zshrc` file with a structured system that separates concerns by category and purpose.

## Directory Structure

```textplain
zsh/
├── core/           # Essential shell functionality
├── tools/          # Tool-specific configurations
├── languages/      # Programming language environments
├── containers/     # Container runtime configurations
├── personal/       # User-specific customizations
└── setup/          # Setup and initialization scripts
```

### Category Breakdown

#### `core/` - Essential Shell Functionality

- **`aliases.zsh`**: Core system aliases and utility functions
- **`configs.zsh`**: Shell configuration and environment settings
- **`editor.zsh`**: Editor-specific configurations and shortcuts

#### `tools/` - Tool-Specific Configurations

- **`aerospace.zsh`**: AeroSpace window manager integration
- **`browser.zsh`**: Browser automation and shortcuts
- **`claude.zsh`**: Claude Code integration and aliases
- **`dot.zsh`**: Dot CLI aliases and shortcuts
- **`fzf.zsh`**: Fuzzy finder configuration
- **`gh.zsh`**: GitHub CLI shortcuts and functions
- **`git.zsh`**: Git aliases, functions, and workflow shortcuts
- **`k8s.zsh`**: Kubernetes (kubectl) aliases and utilities
- **`navi.zsh`**: Interactive cheatsheet tool configuration
- **`shortcuts.zsh`**: Quick reference aliases for documentation
- **`tmux.zsh`**: Tmux session management and shortcuts

#### `languages/` - Programming Language Environments

- **`dotnet.zsh`**: .NET development environment
- **`node.zsh`**: Node.js and npm configuration
- **`python.zsh`**: Python development environment
- **`uv.zsh`**: UV Python package manager integration

#### `containers/` - Container Runtime Configurations

- **`podman.zsh`**: Podman container runtime aliases and functions

#### `personal/` - User-Specific Customizations

- **`mine.zsh`**: Personal aliases and custom functions

## Loading Mechanism

The configuration system is initialized through `_load.zsh`, which:

1. **Sets up PATH** for executable directories:

   ```bash
   export PATH=$PATH:$HOME/.oh-my-zsh/custom/bin
   # Adds all bin subdirectories
   export PATH=$PATH:$HOME/.oh-my-zsh/custom/bin-private
   ```

2. **Loads private configurations** from `private/*.zsh`

3. **Sources zsh files in order** by category:

   ```bash
   for category in core tools languages containers personal setup; do
     for file in $HOME/.oh-my-zsh/custom/zsh/$category/*.zsh(N); do
       source "$file"
     done
   done
   ```

## Key Features

### Modular Organization

- Each category serves a specific purpose
- Easy to locate and modify specific functionality
- Clean separation prevents conflicts

### Ordered Loading

- `core` loads first (essential functionality)
- `tools` and `languages` provide specialized features
- `personal` loads last (can override defaults)

### Discoverability

- Related aliases and functions are grouped together
- Tool-specific configurations in dedicated files
- Documentation and shortcuts easily accessible

## Common Patterns

### Aliases

Most files contain aliases following these patterns:

- Short, memorable names
- Tool-specific prefixes (e.g., `g` for git, `k` for kubectl)
- Descriptive functions for complex operations

### Functions

Complex operations are implemented as shell functions:

- Multi-step workflows
- Parameterized operations
- Tool integration

### Environment Setup

Language and tool files often include:

- PATH modifications
- Environment variable exports
- Tool-specific configuration

## Examples

### Adding New Aliases

Add tool-specific aliases to the appropriate category:

```bash
# For git aliases: zsh/tools/git.zsh
alias gph='git push origin HEAD'

# For general utilities: zsh/core/aliases.zsh
alias myutil='my-custom-command'
```

### Adding Documentation Shortcuts

The `shortcuts.zsh` file provides quick access to documentation:

```bash
alias docs-log='tail -f ~/Library/Logs/dotfiles-docs-update.log'
alias tmux-keys='glow ~/.oh-my-zsh/custom/workflow/tmux-shortcuts.md'
```

## Maintenance

### Adding New Categories

1. Create directory under `zsh/`
2. Add category to loading order in `_load.zsh`
3. Document the category's purpose

### File Organization

- Keep files focused on single tools or concepts
- Use descriptive filenames
- Group related functionality together

This modular approach makes the shell configuration maintainable, discoverable, and extensible while providing powerful automation and shortcuts for development workflows.
