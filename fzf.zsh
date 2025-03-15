export FZF_DEFAULT_COMMAND='find . -type f \
  -not -path "*/\.git/*" \
  -not -path "*/.venv/*" \
  -not -path "*/node_modules/*" \
  -not -path "*/vendor/*" \
  -not -path "*/.build/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/.swiftpm/*"'

export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"

llmcontext() {
  # Capture selected filenames into a variable
  local selected_files
  selected_files="$(fzf --multi)"

  # Exit if no file is selected
  [[ -z "$selected_files" ]] && return

  # Prepare output
  {
    # Print all filenames
    echo "$selected_files"

    # Print a blank line
    echo

    # Loop over each file and surround its contents with tags
    while IFS= read -r f; do
      echo "<$f>"
      cat "$f"
      echo "</$f>"
      echo
    done <<<"$selected_files"
  } | pbcopy
}

source <(fzf --zsh)
