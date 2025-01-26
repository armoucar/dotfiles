export FZF_DEFAULT_COMMAND='find . -type f \
  -not -path "*/\.git/*" \
  -not -path "*/.venv/*" \
  -not -path "*/node_modules/*" \
  -not -path "*/vendor/*" \
  -not -path "*/.build/*" \
  -not -path "*/.swiftpm/*"'

export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
