# VSCode/Cursor Configuration Management

## Quick Setup

### Create Symlinks to Centralized Settings

```bash
setup-vscode-settings
```

## Config Files

### Settings Structure

- **Source**: `~/.oh-my-zsh/custom/config/settings.jsonc` (centralized configuration)
- **VSCode**: `~/Library/Application Support/Code/User/settings.json` → symlink to settings.jsonc
- **Cursor**: `~/Library/Application Support/Cursor/User/settings.json` → symlink to settings.jsonc

### How It Works

- Script detects installed editors (VSCode/Cursor)
- Backs up existing settings with timestamp (if not already symlinks)
- Creates symlinks from editor settings locations to centralized config
- Single source of truth with comments preserved
- Immediate sync between VSCode and Cursor

### Settings Organization

The centralized `settings.jsonc` file is organized into semantic sections:

- **Editor Settings**: Basic editor configuration, fonts, tabs
- **Terminal Settings**: Shell integration, fonts, behavior fixes
- **Workbench & UI**: Theme, layout, explorer settings
- **File Management**: Exclusions, trimming, Python cache handling
- **Language Settings**: JavaScript/TypeScript, Python, Jupyter
- **Git & Version Control**: Git, GitHub, GitLens configuration  
- **Security & Trust**: Workspace trust settings
- **Application Settings**: Updates, timeouts, JSON schema
- **Cursor-Specific**: AI features and Cursor-only settings

### Legacy Files

- `config/vscode-settings.jsonc` (deprecated) - old merge-based config
- Can be safely removed after migration to symlink approach
