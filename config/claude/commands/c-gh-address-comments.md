---
allowed-tools: ["Bash", "Read", "Edit", "MultiEdit", "Grep", "Glob", "WebFetch", "TodoWrite"]
argument-hint: "No arguments required - will guide you through addressing PR comments interactively"
description: "Interactive workflow for addressing GitHub PR comments step by step"
---

# GitHub PR Comment Resolution Workflow

I'll help you systematically address comments on your GitHub pull request. This command provides an interactive workflow where we'll:

1. **Fetch PR comments** - Get all comments from the current PR
2. **Review each comment** - Go through comments one by one
3. **Plan actions** - For each comment, you'll decide whether to:
   - Implement the suggested changes
   - Resolve without changes (with explanation)
   - Ask for clarification
   - Mark as addressed

4. **Execute changes** - Make code changes as needed
5. **Update PR** - Push changes and resolve comments

Let's start by getting the current PR information and comments.

## Getting Started

First, I'll check if we're in a Git repository and identify the current PR:

!git branch --show-current
!gh pr view --json number,title,url,comments

Then we'll go through each comment systematically, and you can tell me how you'd like to handle each one.