# Useful aliases for ClaudeCode
alias cc='claude'
alias ccp='claude -p'
alias ccc='claude -c'
alias ccr='claude -r'
alias ccv='claude --verbose'
alias ccskip='claude --dangerously-skip-permissions'
alias ccu='claude update'
alias ccm='claude mcp'
alias ccs='claude-start'

# Git-related aliases
alias cccommit='claude commit'
alias ccpr='claude pr'
alias ccreview='claude review'

# Development aliases
alias cctest='claude test'
alias cclint='claude lint'
alias ccdocs='claude docs'

# Model-specific aliases
alias ccsonnet='claude --model sonnet'
alias ccopus='claude --model opus'
alias cchaiku='claude --model claude-3-haiku-20240307'

# Configuration sync alias
alias claude-sync='~/.oh-my-zsh/custom/claude/setup.zsh'

# Short aliases for permission modes (using claude-start for proper tmux integration)
alias ccsa="claude-start --permission-mode acceptEdits"
alias ccss="claude-start --permission-mode default"
alias ccsp="claude-start --permission-mode plan"
alias ccsb="claude-start --dangerously-skip-permissions"
alias ccsr="claude-resume"

# Permission management aliases (using dot CLI)
alias dcpa="dot claude permissions-apply"
