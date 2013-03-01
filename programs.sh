#rvm
[[ -s "$HOME/.rvm/scripts/rvm" ]] && source "$HOME/.rvm/scripts/rvm"

#node
. ~/.nvm/nvm.sh

export GREP_OPTIONS="--color=auto"
export GREP_COLOR="4;33"
export CLICOLOR="auto"
export PS1='\w `~/.rvm/bin/rvm-prompt i v g` `git branch 2> /dev/null | grep -e ^* | sed -E  s/^\\\\\*\ \(.+\)$/\(\\\\\1\)\ /`\n\[\033[37m\]$\[\033[00m\] '

export APPENGINE_SDK_HOME="~/desenvolvimento/appengine-java-sdk-1.7.5"
export ANDROID_NDK="~/desenvolvimento/android-ndk-r8c"
export JAVA_HOME=`/usr/libexec/java_home -v 1.7`

# MacPorts Installer addition
export PATH=$PATH:/opt/local/bin:/opt/local/sbin
export PATH=$PATH:/opt/subversion/bin/
export PATH=$PATH:$APPENGINE_SDK_HOME/bin
