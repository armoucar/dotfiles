# Tmux Catppuccin Theme Setup

## Install

```bash
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
git clone https://github.com/catppuccin/tmux.git ~/.tmux/plugins/catppuccin
tmux kill-server
```

## Configuration

Add to `config/tmux.conf`:

```bash
# Catppuccin theme configuration
set -g @catppuccin_flavor "mocha"
set -g @catppuccin_window_status_style "rounded"

# Override window text to show window names instead of hostname
set -g @catppuccin_window_default_text "#W"
set -g @catppuccin_window_current_text "#W"
set -g @catppuccin_window_default_fill "number"
set -g @catppuccin_window_current_fill "number"

# Disable automatic renaming
set -g automatic-rename off
set -g allow-rename off

# Load theme
run '~/.tmux/plugins/catppuccin/catppuccin.tmux'

# Fix hostname bug - force window name display
set -g window-status-format "#[fg=#{@thm_surface_2},bg=#{@thm_base}] #I #[fg=#{@thm_fg},bg=#{@thm_base}]#W "
set -g window-status-current-format "#[fg=#{@thm_crust},bg=#{@thm_mauve}] #I #[fg=#{@thm_crust},bg=#{@thm_mauve}]#W "

# Status modules
set -g status-right-length 100
set -g status-left-length 100
set -g status-left ""
set -g status-right "#{E:@catppuccin_status_application}"
set -agF status-right "#{E:@catppuccin_status_cpu}"
set -ag status-right "#{E:@catppuccin_status_session}"
set -ag status-right "#{E:@catppuccin_status_uptime}"
set -agF status-right "#{E:@catppuccin_status_battery}"
```

## Requirements

- **Nerd Font**: Set terminal font to a Nerd Font (e.g., 0xProtoNerdFont) for icons
- **256-color terminal**: Already configured in tmux.conf

## Window Names

Use `Ctrl+Space + ,` to rename windows. Names will persist (no hostname display).