export EDITOR=cursor

alias e="$EDITOR"

export PATH=$PATH:$HOME/.oh-my-zsh/custom/bin

for file in $HOME/.oh-my-zsh/custom/private/*.zsh; do
  source "$file"
done
