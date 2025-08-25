# Tmux FZF Switcher Plugin

A self-contained tmux plugin that provides powerful fzf-powered window and session switching with live preview functionality.

## Features

- **Full-screen fzf interface** with live preview
- **Three switching modes**: all, sessions-only, windows-only
- **Live preview** showing actual window content
- **Smart navigation** with keyboard shortcuts
- **Self-contained** - no external PATH dependencies

## Key Bindings

- `C-b w` - Show all windows and sessions (windows first, then sessions)
- `C-b s` - Sessions-only switcher (replaces default tmux session chooser)
- `C-b W` - Windows-only switcher

## Navigation Controls

- `Tab` - Toggle preview on/off
- `Ctrl+U` / `Ctrl+D` - Scroll preview up/down
- `Enter` - Switch to selected window/session
- `Esc` - Cancel and close switcher

## Installation

### Manual Installation

1. Clone or copy this plugin to your tmux plugins directory:

   ```bash
   mkdir -p ~/.tmux/plugins
   cp -r /path/to/tmux-fzf-switcher ~/.tmux/plugins/
   ```

2. Add to your `~/.tmux.conf`:

   ```bash
   run '~/.tmux/plugins/tmux-fzf-switcher/tmux-fzf-switcher.tmux'
   ```

3. Reload tmux configuration:

   ```bash
   tmux source-file ~/.tmux.conf
   ```

### Using TPM (Tmux Plugin Manager)

Add to your `~/.tmux.conf`:

```bash
set -g @plugin 'your-username/tmux-fzf-switcher'
```

Then press `prefix + I` to install.

## Requirements

- `fzf` - Fuzzy finder
- `tmux` - Terminal multiplexer
- `bash` - Shell for running scripts

## Plugin Structure

```
tmux-fzf-switcher/
├── tmux-fzf-switcher.tmux    # Main plugin entry point
├── scripts/
│   ├── switcher.sh           # Main switcher logic
│   └── preview.sh            # Preview generator
└── README.md                 # This file
```

## How It Works

The plugin creates a full-screen fzf interface that lists tmux sessions and windows. When you navigate through the list, the preview pane shows the actual content of the selected window or session (active window content for sessions).

All scripts use relative paths, making the plugin completely self-contained and portable.
