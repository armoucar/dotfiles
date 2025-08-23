# AeroSpace Reference Guide

## What is AeroSpace?

AeroSpace is a tiling window manager for macOS that automatically arranges
windows in a grid layout. It provides keyboard-driven window management
similar to i3wm on Linux.

## Key Features

- **Automatic tiling**: Windows snap into grid layouts
- **Workspace management**: Organize apps across multiple virtual desktops
- **Multi-monitor support**: Seamless window movement between displays
- **Service mode**: Temporary mode for quick adjustments
- **Configurable**: Customize all keybindings and behavior

## Setup & Installation

1. **Download**: Get AeroSpace from the official website
2. **Config Location**: `~/.config/aerospace/aerospace.toml`
3. **Permissions**: Grant accessibility permissions in System Settings >
   Privacy & Security
4. **Auto-start**: Enable launch on login when prompted

## Layout Types

- **Tiles**: Windows arranged in a grid (default)
- **Accordion**: Only one window visible at a time in a split
- **Floating**: Windows can overlap and be positioned freely

## Workspace Organization

### Default Workspace Assignments

- **Monitor 1**: 1,2,3,Q,W,E,A,S,D
- **Monitor 2**: 4,5,6,R,T,Y,F,G,H,V,B,N
- **Monitor 3**: 7,8,9,U,I,O,J,K,L,M

### Best Practices

- Use workspaces to organize different projects or contexts
- Assign specific apps to specific workspaces for consistency
- Use the number keys (1-9) for most frequently accessed workspaces

## CLI Commands

```bash
aerospace list-workspaces              # List all workspaces
aerospace list-windows                 # List all windows
aerospace focus --window-id <id>       # Focus specific window
aerospace move left/right/up/down      # Move windows via CLI
aerospace reload-config                # Reload configuration
```

## Configuration Tips

- All keybindings can be customized in the config file
- Use `aerospace reload-config` after making changes
- The default modifier is Alt, but can be changed
- You can create custom workspace assignments

## Troubleshooting

- **Keybindings not working**: Check accessibility permissions
- **Windows not tiling**: Ensure the app isn't in floating mode
- **Config changes not applying**: Run `aerospace reload-config`
- **Debug window issues**: Use `aerospace list-windows`

## Integration Tips

- Combine with Raycast or Alfred for app launching
- Use service mode for quick one-off adjustments
- Set up workspace-specific app assignments in config
- Consider creating custom keybindings for your workflow

---

**Quick shortcuts reference**: See `aerospace-shortcuts.md`
