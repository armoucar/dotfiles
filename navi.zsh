#!/usr/bin/env zsh

export NAVI_PATH=$HOME/.oh-my-zsh/custom/navi

eval "$(navi widget zsh)"

export NEO_CLI_PATH=$HOME/dev/workspace/neon.neo-cli

for dir in $NEO_CLI_PATH/neo/*/; do
  export NAVI_PATH=$NAVI_PATH:$dir
done
