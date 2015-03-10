#aliases to terminal commands
alias ls="ls -Gh"
alias l="ls -lhG"
alias ll="ls -alhG"
alias cd..="cd .."
alias gitk="gitk --all 2>/dev/null &"
alias mvim="mvim 2>/dev/null &"
alias g="git"
alias gsa="git config --get-regexp alias"
alias gcd="git checkout develop"
alias gcm="git checkout master"
alias tree="find . -print | sed -e 's;[^/]*/;|____;g;s;____|; |;g'"

#ruby/bundler/rails
alias be="bundle exec"
alias r="bundle exec rails"
alias s="bundle exec rspec"
alias rake="bundle exec rake"
alias srs="bin/spring rails server"
alias src="bin/spring rails console"
alias srspec="bin/spring rspec"
alias pd="bundle exec cap production deploy"
alias sd="bundle exec cap staging deploy"

#edit program config files
alias eg="vim ~/.gitconfig"
alias em="vim ~/.m2/settings.xml"
alias eb="vim ~/.bash_profile"
alias sb="source ~/.bash_profile"
alias ev="vim ~/.vimrc"
alias es="vim ~/.dot/shortcuts.sh"
alias ep="vim ~/.dot/programs.sh"
alias eproxy="vim ~/.dot/proxy.sh"
alias fg="find . | grep "
alias lg="l . | grep "

#shortcuts
alias cleartrash="sudo rm -rf ~/.Trash"
alias ip="ifconfig | grep broadcast | sed 's/.*inet \(.*\) netmask.*/\1/'"
alias appengine_deploy="sh $APPENGINE_SDK_HOME/bin/appcfg.sh --enable_jar_splitting update";
alias serve="python -m SimpleHTTPServer"

#moving into folders
alias work="cd ~/dev/workspaces"
alias exp="cd ~/dev/workspaces/experiments"
alias oss="cd ~/dev/workspaces/oss"
alias lov="cd ~/dev/workspaces/lov"
alias ct="cd ~/dev/workspaces/lov/customisation-tools"
alias lovw="cd ~/dev/workspaces/lov/web"
alias models="cd ~/dev/workspaces/lov/models"
alias blog="cd ~/dev/workspaces/oss/sites/blog"
alias desktop="cd ~/desktop"
alias dev="cd ~/dev"
alias downloads="cd ~/downloads"
alias vimdir="cd ~/.vim"
alias gae="cd $APPENGINE_SDK_HOME"
alias jssn="cd ~/.vim/snippets/javascript"
alias vimsnippet="cd ~/.vim/snippets"

#ssh
alias deployer="ssh deployer@fabstudio-web.cloudapp.net"
alias ipam_server="ssh ubuntu@54.191.249.237"
alias ipam_mysql="mysql -h ipam-database.c0bedn8hxciu.us-west-2.rds.amazonaws.com -u root -p"

#ngix
alias start-nginx="sudo nginx"
alias stop-nginx="sudo nginx -s stop"
alias config-nginx="sudo mvim /usr/local/etc/nginx/nginx.conf"

#custom
alias bgem="grunt && rake build"
alias buc="bundle update customisation_tools-rails"
