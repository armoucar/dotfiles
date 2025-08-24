# AeroSpace window manager configuration
export AEROSPACE_CONFIG_HOME="${HOME}/.oh-my-zsh/custom/config/aerospace"

# Ensure AeroSpace finds our config via XDG
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"

# Symlink to XDG location where AeroSpace expects it
mkdir -p "$XDG_CONFIG_HOME/aerospace"
if [[ ! -L "$XDG_CONFIG_HOME/aerospace/aerospace.toml" ]] || \
   [[ "$(readlink "$XDG_CONFIG_HOME/aerospace/aerospace.toml")" != "$AEROSPACE_CONFIG_HOME/aerospace.toml" ]]; then
    ln -sfn "$AEROSPACE_CONFIG_HOME/aerospace.toml" "$XDG_CONFIG_HOME/aerospace/aerospace.toml"
fi