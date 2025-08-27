# Documentation Submodules Automation

## Overview

Automated system to keep external documentation repositories fresh via git submodules, running hourly with auto-commit.

## Structure

```
docs-external/
└── claude-code-docs/           # GitHub: ericbuess/claude-code-docs
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
```
