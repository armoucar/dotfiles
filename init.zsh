#! /usr/bin/env zsh

function init-dotfiles() {
  git clone \
    https://github.com/zsh-users/zsh-autosuggestions \
    ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions 2>/dev/null || {
    echo "Note: zsh-autosuggestions plugin directory already exists, skipping clone..."
  }
}

function init-cli() {
  pip install -e $HOME/.oh-my-zsh/custom/cli
}
