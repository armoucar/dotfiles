#! /usr/bin/env zsh

function _init_dotfiles() {
  git clone \
    https://github.com/zsh-users/zsh-autosuggestions \
    ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions 2>/dev/null || {
    echo "Note: zsh-autosuggestions plugin directory already exists, skipping clone..."
  }
}

function _init_cli() {
  pip install -e $HOME/.oh-my-zsh/custom/cli
}

function _init_tmux() {
  $HOME/.oh-my-zsh/custom/setup-tmux.zsh
}

alias init-dotfiles="_init_dotfiles"
alias init-cli="_init_cli"
alias init-tmux="_init_tmux"
