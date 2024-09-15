alias o="open ."
alias npmls0="npm ls --depth=0"
alias rin="rm -rf node_modules && npm install"
alias rinv="rm -rf node_modules && npm install --verbose"
alias ip="ifconfig | grep broadcast | sed 's/.*inet \(.*\) netmask.*/\1/'"
alias cls='printf "\33c[3J"'
alias ntl='ntl -A'
alias tree='tree -I "__pycache__"'

function fg() {
  ignored_folders=(.venv __pycache__ node_modules dist build)

  find_command="find ."
  for folder in "${ignored_folders[@]}"; do
    find_command+=" -path \"*/$folder\" -prune -o"
  done

  find_command+=" -print | grep \"$1\""

  eval $find_command
}

function gopen() {
  git remote -v | head -n 1 | awk -F "@" '{print $2}' | awk -F " " '{print $1}' | sed 's/:/\//g' | sed 's/.git//g' | awk '{print "http://"$1}' | xargs open
}

function gopenac() {
  git remote -v | head -n 1 | awk -F "@" '{print $2}' | awk -F " " '{print $1}' | sed 's/:/\//g' | sed 's/.git/\/actions/g' | awk '{print "http://"$1}' | xargs open
}
