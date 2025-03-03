# Notes CLI aliases
# Add this to your .zshrc: source ~/.oh-my-zsh/custom/cli/app/command/notes/alias.zsh

# Create commands
alias notcn="dot notes create note -t"
alias notct="dot notes create task -t"

# List commands
alias notl="dot notes list"
alias notln="dot notes list --type note"
alias notlt="dot notes list --type task"
alias notlc="dot notes list --type task --completed"
alias notlp="dot notes list --type task --pending"
alias notls="dot notes list --show-content"

# Edit command
alias note="dot notes edit"
alias noten="dot notes edit --type note"
alias notet="dot notes edit --type task"

# Task completion commands
alias notcom="dot notes complete"
alias notinc="dot notes incomplete"

# Delete command
alias notd="dot notes delete"
alias notdf="dot notes delete --force"

# Search command
alias nots="dot notes search"

# Tags filtering
notlta() {
  dot notes list --tag "$1"
}

# Print a help message with all available aliases
noth() {
  echo "Notes CLI aliases:"
  echo "  notc    - Create a new item (note or task)"
  echo "  notcn   - Create a new note"
  echo "  notct   - Create a new task"
  echo "  notl    - List all items"
  echo "  notln   - List notes only"
  echo "  notlt   - List tasks only"
  echo "  notlc   - List completed tasks"
  echo "  notlp   - List pending tasks"
  echo "  notls   - List with content shown"
  echo "  notlta  - List by tag (requires argument: notlta work)"
  echo "  note    - Edit an item (using fzf)"
  echo "  noten   - Edit a note (using fzf)"
  echo "  notet   - Edit a task (using fzf)"
  echo "  notcom  - Mark a task as completed"
  echo "  notinc  - Mark a task as incomplete"
  echo "  notd    - Delete an item (using fzf)"
  echo "  notdf   - Delete without confirmation"
  echo "  nots    - Search in notes content (requires argument: nots keyword)"
  echo "  noth    - Show this help message"
}
