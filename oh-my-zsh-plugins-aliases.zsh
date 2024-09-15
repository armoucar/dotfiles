printContentAfterMatch() {
  searchPattern="$1"
  file="$2"
  lineNumber=$(grep -n "$searchPattern" "$file" | cut -d: -f1)
  if [ ! -z "$lineNumber" ]; then
    totalLines=$(wc -l <"$file")
    linesAfterMatch=$((totalLines - lineNumber))
    tail -n $linesAfterMatch "$file" | tail -n +2
  else
    echo "Match for \"$searchPattern\" not found in $file."
  fi
}

printContentBetweenMatches() {
  startPattern="$1"
  endPattern="$2"
  file="$3"
  awk "/$startPattern/,/$endPattern/" "$file"
}

alias a-docker='printContentAfterMatch "## Aliases" $HOME/.oh-my-zsh/plugins/docker/README.md'
alias a-docker-compose='printContentAfterMatch "## Aliases" $HOME/.oh-my-zsh/plugins/docker-compose/README.md'
alias a-git='printContentAfterMatch "## Aliases" $HOME/.oh-my-zsh/plugins/git/README.md'
alias a-git-commit='printContentBetweenMatches "## Syntax" "- \`wip\`" $HOME/.oh-my-zsh/plugins/git-commit/README.md'
alias agc='a-git-commit'

ag() {
  searchString="$1"
  a-git | grep "$searchString" | awk -F'|' '{print $2 " -> " $3}'
}
