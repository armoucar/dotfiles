export EDITOR=cursor

alias e="$EDITOR"

export PATH=$PATH:$HOME/.oh-my-zsh/custom/bin
export PATH=$PATH:$HOME/.oh-my-zsh/custom/bin-public

for file in $HOME/.oh-my-zsh/custom/private/*.zsh; do
  source "$file"
done
