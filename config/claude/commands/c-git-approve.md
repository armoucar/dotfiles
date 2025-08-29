---
allowed-tools: Bash(gh:*)
argument-hint: [pr-urls...]
description: Approve GitHub PRs with LGTM message
---

You'll receive PR URLs and you should approve them with "LGTM" message using the gh CLI.

For each PR URL provided in $ARGUMENTS:

1. Extract the repo and PR number from the URL
2. Use `gh pr review` to approve with `--approve` flag and `--body "LGTM"`
3. Confirm successful approval

PR URLs: $ARGUMENTS
