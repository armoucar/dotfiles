
export GREP_OPTIONS="--color=auto"
export GREP_COLOR="4;33"
export CLICOLOR="auto"

# rbenv version | sed -e 's/ .*//'
__rbenv_ps1 ()
{
  rbenv_ruby_version=`rbenv version | sed -e 's/ .*//'`
  printf $rbenv_ruby_version
}

#export PS1='\w `~/.rvm/bin/rvm-prompt i v g` | node-`node -v` `git branch 2> /dev/null | grep -e ^* | sed -E  s/^\\\\\*\ \(.+\)$/\(\\\\\1\)\ /`\n\[\033[37m\]$\[\033[00m\] '
#export PS1='\w `rbenv version | sed -e 's/ .*//'` | node-`node -v` `git branch 2> /dev/null | grep -e ^* | sed -E  s/^\\\\\*\ \(.+\)$/\(\\\\\1\)\ /`\n\[\033[37m\]$\[\033[00m\] '
#export PS1='\[\033[01;32m\]\u@\h\[\033[01;33m\] \w$(__git_ps1) ruby=$(__rbenv_ps1) | node=`node -v` \n\[\033[01;34m\]\$\[\033[00m\] '
export PS1='\[\033[01;32m\]\u@\h\[\033[01;33m\] \w$(__git_ps1) ruby=$(__rbenv_ps1) | node=`node -v` \n\[\033[01;34m\]\$\[\033[00m\] '
# export PS1='\w \n$ '


export EC2_HOME="$HOME/dev/ec2-api-tools-1.6.7.1"
export APPENGINE_SDK_HOME="$HOME/dev/appengine-java-sdk-1.8.9"
export JAVA_HOME=`/usr/libexec/java_home -v 1.8`

export MONGODB_HOME="/Users/arthur/dev/mongodb-osx-x86_64-2.4.9"
export MYSQL_HOME="/usr/local/mysql"
export REDIS_HOME="/Users/arthur/dev/redis-2.8.2"
export ANDROID_HOME="/Users/arthur/dev/android-sdk-macosx"
export M2_HOME="/Users/arthur/dev/apache-maven-3.1.1"
export GRADLE_HOME="/Users/arthur/dev/gradle-1.10"
export ANT_HOME="/Users/arthur/dev/apache-ant-1.9.3"

export BUNDLER_EDITOR="mvim"

# Path
export PATH="/usr/local/bin:$PATH"
export PATH=$PATH:$APPENGINE_SDK_HOME/bin
export PATH=$PATH:$EC2_HOME/bin
export PATH=$PATH:$MONGODB_HOME/bin
export PATH=$PATH:$MYSQL_HOME/bin
export PATH=$PATH:$REDIS_HOME/src
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$M2_HOME/bin
export PATH=$PATH:$GRADLE_HOME/bin
export PATH=$PATH:$ANT_HOME/bin

#node
. ~/.nvm/nvm.sh

#rvm
#[[ -s "$HOME/.rvm/scripts/rvm" ]] && source "$HOME/.rvm/scripts/rvm"

#rbenv
eval "$(rbenv init -)"
