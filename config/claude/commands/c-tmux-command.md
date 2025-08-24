---
allowed-tools: Read, Edit, MultiEdit, Bash, Glob, Grep
argument-hint: [tmux configuration changes to make]
description: Apply tmux configuration changes to dotfiles repo
---

You are helping with tmux configuration changes in the user's dotfiles repository at `/Users/U003877/.oh-my-zsh/custom`.

## Your Task

Apply the requested tmux configuration changes: $ARGUMENTS

## Key Files

- Main config: `config/tmux.conf`
- ZSH tmux tools: `zsh/tools/tmux.zsh`
- Setup script: `bin/setup-tmux`

## Process

1. Read the relevant tmux configuration files to understand current setup
2. **Always check for keybinding conflicts** before adding new shortcuts
3. Apply the requested changes following tmux best practices
4. Choose suitable alternative keys that don't conflict with existing bindings
5. Ensure changes follow the existing code style and conventions
6. Test that the configuration syntax is valid if possible

## Important Notes

- This is a dotfiles repository, so edit files in place
- Follow existing patterns and commenting style
- Consider both tmux.conf settings and any related ZSH aliases/functions
- **Conflict Detection**: Always analyze existing `bind` commands in tmux.conf to avoid key conflicts
- **Key Selection**: Choose intuitive alternatives (e.g., `;` for last-window, `'` for marks, etc.)
- The user may need to reload tmux config with `C-b r` or restart tmux after changes
