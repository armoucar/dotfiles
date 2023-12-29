alias k="gitk --all 2>/dev/null &"
alias o="open ."
alias npmls0="npm ls --depth=0"
alias fg="find . | grep "
alias rin="rm -rf node_modules && npm install"
alias rinv="rm -rf node_modules && npm install --verbose"
alias ip="ifconfig | grep broadcast | sed 's/.*inet \(.*\) netmask.*/\1/'"
alias cls='printf "\33c[3J"'
alias ntl='ntl -A'

function gopen () {
  git remote -v | head -n 1 | awk -F "@" '{print $2}' | awk -F " " '{print $1}' | sed 's/:/\//g' | sed 's/.git//g' | awk '{print "http://"$1}' | xargs open
}
