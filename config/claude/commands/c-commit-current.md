---
allowed-tools: [Bash, Read, Glob, Grep]
argument-hint: No arguments needed
description: Read all git changes (staged/unstaged) and create a well-described commit message
---

Read all changes made in git, might be staged or not but they aren't committed yet. Understand the context of the changes and create a well-described commit message.

Analyze the git status, git diff, and recent commit history to understand:
1. What files have been modified
2. The nature of the changes (new features, bug fixes, refactoring, etc.)
3. The scope and impact of the modifications

Then create a clear, descriptive commit message that:
- Summarizes the changes concisely
- Follows conventional commit format when appropriate
- Provides context for why the changes were made
- Is consistent with the project's commit message style

Finally, stage all changes and create the commit with the generated message.