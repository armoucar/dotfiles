#aliases to terminal commands
alias ls="ls -Gh"
alias l="ls -lhG"
alias ll="ls -alhG"
alias cd..="cd .."
alias gitk="gitk --all 2>/dev/null &"

#edit program config files
alias eg="vim ~/.gitconfig"
alias em="vim ~/.m2/settings.xml"
alias eb="vim ~/.bash_profile"
alias sb="source ~/.bash_profile"
alias ev="vim ~/.vimrc"
alias evd="vim ~/.vim/vimrc"
alias es="vim ~/.dot/shortcuts.sh"
alias ep="vim ~/.dot/programs.sh"
alias eproxy="vim ~/.dot/proxy.sh"
alias fg="find . | grep "
alias lg="l . | grep "

#shortcuts
alias jquery="mkdir js ; > js/script.js ;
	      curl http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js >> js/jquery.min.js ;
	      mkdir css ; > css/style.css ;
	      > index.html ;"

alias cleartrash="sudo rm -rf ~/.Trash"
alias ip="ifconfig | grep broadcast | sed 's/.*inet \(.*\) netmask.*/\1/'"
alias appengine_deploy="sh $APPENGINE_SDK_HOME/bin/appcfg.sh --enable_jar_splitting update";

#moving into folders
alias @="cd ~"
alias mov="cd ~/desenvolvimento/workspaces/banco_workspace/"
alias jswork="cd ~/desenvolvimento/workspaces/javascript_workspace"
alias javawork="cd ~/desenvolvimento/workspaces/java"
alias bancowork="cd ~/desenvolvimento/workspaces/banco_workspace"
alias opensource="cd ~/desenvolvimento/opensource"
alias desktop="cd ~/desktop"
alias home="cd ~"
alias desenv="cd ~/desenvolvimento"
alias downloads="cd ~/downloads"
alias vimdir="cd ~/.vim"
alias gae="cd $APPENGINE_SDK_HOME"
alias eclipsefy="cp -r ~/.dot/templates/project_sample ./.project"
alias jssn="cd ~/.vim/snippets/javascript"
alias vimsnippet="cd ~/.vim/snippets"
alias java_home="cd /System/Library/Frameworks/JavaVM.framework/Versions/CurrentJDK"
