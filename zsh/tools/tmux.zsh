#!/bin/bash

# Tmux configuration

# Oh-My-Zsh tmux plugin configuration
export ZSH_TMUX_AUTOSTART=true
export ZSH_TMUX_AUTONAME_SESSION=true
export ZSH_TMUX_ITERM2=true
export ZSH_TMUX_UNICODE=true

# Tmux aliases from oh-my-zsh tmux plugin
alias tksv='command tmux kill-server'      # Kill tmux server
alias tl='command tmux list-sessions'      # List sessions
alias tmuxconf='$EDITOR ~/.tmux.conf'      # Edit tmux config
alias tds='_tmux_directory_session'        # Create/attach to dir-based session

# Tmux window state management
alias tload='tmux-window-state load'       # Load saved tmux state

# Tmux attach/session aliases with smart command handling
# Attach to session
function ta() {
  if [[ -z $1 ]] || [[ ${1:0:1} == '-' ]]; then
    command tmux attach "$@"
  else
    command tmux attach -t "$@"
  fi
}

# Attach detached to session
function tad() {
  if [[ -z $1 ]] || [[ ${1:0:1} == '-' ]]; then
    command tmux attach -d "$@"
  else
    command tmux attach -d -t "$@"
  fi
}

# New session
function ts() {
  if [[ -z $1 ]] || [[ ${1:0:1} == '-' ]]; then
    command tmux new-session "$@"
  else
    command tmux new-session -s "$@"
  fi
}

# Kill session
function tkss() {
  if [[ -z $1 ]] || [[ ${1:0:1} == '-' ]]; then
    command tmux kill-session "$@"
  else
    command tmux kill-session -t "$@"
  fi
}

# Create/attach to directory-based session
function _tmux_directory_session() {
  local dir=${PWD##*/}
  local md5=$(printf '%s' "$PWD" | md5sum | cut -d ' ' -f 1)
  local session_name="${dir}-${md5:0:6}"
  command tmux new -As "$session_name"
}
