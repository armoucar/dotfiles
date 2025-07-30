#!/usr/bin/env zsh

export NAVI_PATH=$NAVI_PATH:$HOME/.oh-my-zsh/custom/navi

export CLI_COMMANDS_PATH=$HOME/.oh-my-zsh/custom/cli/app/command

for dir in $CLI_COMMANDS_PATH/*/; do
  export NAVI_PATH=$NAVI_PATH:$dir
done

eval "$(navi widget zsh)"
