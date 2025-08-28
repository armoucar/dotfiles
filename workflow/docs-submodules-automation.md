# Documentation Submodules Automation

## Overview

Automated system to keep external documentation repositories fresh via git submodules, running hourly with auto-commit.

## Structure

```
docs-external/
├── aerospace/                  # GitHub: nikitabobko/AeroSpace
├── claude-code-docs/           # GitHub: ericbuess/claude-code-docs
└── dspy/                       # GitHub: stanfordnlp/dspy
```

## Components

- **Update Script**: `bin/system/docs-external-update`
- **LaunchAgent**: `config/launchd/com.dotfiles.docs-external-update.plist`
- **Setup**: `bin/setup/setup-docs-automation`
- **Logs**: `~/Library/Logs/dotfiles-docs-update.log`

## Schedule

Runs **every hour** via macOS launchd, updates submodules to latest commits and auto-commits changes locally.

## Adding New Documentation

```bash
# Add new submodule
git submodule add https://github.com/user/repo.git docs-external/repo-name

# Commit the addition
git add .gitmodules docs-external/
git commit -m "docs: Add repo-name documentation submodule"
```

## Management

```bash
# Status
launchctl list | grep dotfiles

# Logs  
tail -f ~/Library/Logs/dotfiles-docs-update.log

# Manual run
docs-external-update
```

## Commit Pattern

```
chore: Update external documentation submodules [auto]

- docs-external/claude-code-docs: updated to abc1234
- docs-external/dspy: updated to def5678
```

## Integration with Documentation Search

The submodules automatically integrate with Claude Code's documentation search system:

### Subagent Search (summaries only)

```
Use the docs-search agent to find information about [topic]
```

### Command Search (full content)

```
/c-docs-search claude [query]      # Search Claude Code docs
/c-docs-search dspy [query]        # Search DSPy docs
/c-docs-search aerospace [query]   # Search AeroSpace docs
/c-docs-search all [query]         # Search all documentation
```

### Available Documentation Sources

- **aerospace**: AeroSpace window manager documentation (`docs-external/aerospace/docs/`)
- **claude**: Claude Code documentation (`docs-external/claude-code-docs/docs/`)
- **dspy**: DSPy framework documentation (`docs-external/dspy/docs/docs/`)

New submodules are automatically discovered by both search workflows.
