export EDITOR=cursor

alias e="$EDITOR"
alias docker="podman"

export PATH=$PATH:$HOME/.oh-my-zsh/custom/bin
export PATH=$PATH:$HOME/.oh-my-zsh/custom/bin-public

# Load private files
for file in $HOME/.oh-my-zsh/custom/private/*.zsh; do
  source "$file"
done

source $HOME/.oh-my-zsh/custom/cli/app/command/notes/alias.zsh

# Load all zsh files from the new structure
for category in core tools languages containers personal setup; do
  for file in $HOME/.oh-my-zsh/custom/zsh/$category/*.zsh(N); do
    source "$file"
  done
done
