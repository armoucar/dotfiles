export PAGER=""

function gh-actions() {
  open -a "Google Chrome" --args --profile-directory="Default"
  open "https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/actions"
}
