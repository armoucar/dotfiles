# VSCode/Cursor Configuration Management

## Quick Setup

### Apply Settings
```bash
setup-vscode-settings
```

## Config Files

### Settings Location
- **Source**: `~/.oh-my-zsh/custom/config/vscode-settings.jsonc`
- **VSCode**: `~/Library/Application Support/Code/User/settings.json`  
- **Cursor**: `~/Library/Application Support/Cursor/User/settings.json`

### How It Works
- Script detects installed editors (VSCode/Cursor)
- Backs up existing settings with timestamp
- Merges source config into editor settings
- Handles JSON with comments (JSONC format)
- Uses Python for reliable JSON parsing and merging