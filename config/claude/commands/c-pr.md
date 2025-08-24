---
allowed-tools: [Bash, Read, Glob, Grep]
argument-hint: [optional: additional context or title override]
description: Create or update PR for current branch with comprehensive analysis
---

Create a pull request for the current branch. If the PR already exists, update the title and description with comprehensive information about all changes included.

Process:
1. Analyze git status, diff, and commit history to understand all changes
2. Check if PR already exists for current branch
3. If PR exists, update it; otherwise create new PR
4. Generate concise summary covering all features and changes (no file paths)
5. Use conventional PR format with clear summary

Arguments: $ARGUMENTS

Execute the PR creation/update process with thorough analysis of the branch changes.