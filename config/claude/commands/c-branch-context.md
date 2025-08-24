---
allowed-tools: [Bash, Grep, Read]
argument-hint: (no arguments needed)
description: Analyze git branch changes from fork point to understand branch purpose
---

Use git to understand the changes made to this branch and what it is about. This branch we're in is probably forked from `main` so you have to start reading from the first forked commit. Understand what this is about and say at the end we're ready to continue working on it.

Steps to follow:
1. Identify the fork point from main branch
2. List all commits made on this branch since the fork
3. Analyze the changes in those commits using git diff
4. Examine modified files to understand the feature/fix being implemented
5. Provide a summary of what this branch accomplishes
6. Confirm readiness to continue working on it