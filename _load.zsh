export EDITOR=cursor

alias e="$EDITOR"
alias docker="podman"

export PATH=$PATH:$HOME/.oh-my-zsh/custom/bin
export PATH=$PATH:$HOME/.oh-my-zsh/custom/bin-private

# Load private files
for file in $HOME/.oh-my-zsh/custom/private/*.zsh; do
  source "$file"
done

# Load all zsh files from the new structure
for category in core tools languages containers personal setup; do
  for file in $HOME/.oh-my-zsh/custom/zsh/$category/*.zsh(N); do
    source "$file"
  done
done
