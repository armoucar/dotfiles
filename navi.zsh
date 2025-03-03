#!/usr/bin/env zsh

export NAVI_PATH=$NAVI_PATH:$HOME/.oh-my-zsh/custom/navi
export NAVI_PATH=$NAVI_PATH:$HOME/.oh-my-zsh/custom/cli/app/command/notes

eval "$(navi widget zsh)"
