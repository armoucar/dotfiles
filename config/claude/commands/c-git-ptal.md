---
allowed-tools: Bash(gh search prs:*), Bash(date:*)
argument-hint: [timeframe] (optional: today, yesterday, "last week", etc. - defaults to today)
description: Fetch opened PRs from specified timeframe and create PTAL message in Portuguese
---

Fetch all my recently opened pull requests from the specified timeframe (or TODAY if no argument) and create a message in Portuguese (PT-BR) in the following format:

PTAL:
[pr link 1] - short description
[pr link 2] - short description
...

Arguments:

- $1 (optional): Timeframe like "today", "yesterday", "last week", etc. Defaults to "today"

Use `gh search prs --state open --author @me --created ">=YYYY-MM-DD"` to search across all repositories.
Convert the timeframe argument to the appropriate date format and filter PRs created on or after that date.

Format each PR with:

- The full GitHub URL  
- A brief description based on the PR title

The message should be ready to copy and paste for sharing with the team.
