---
allowed-tools: Bash(bin/git/github-activity:*)
argument-hint: [days]
description: Generate work summary from GitHub activity for specified days
---

Generate a **summary of the work done** in a **single list** based on GitHub activity from the last $1 days, following these rules:

* The output must be written in **Portuguese (PT-BR)**.
* Use a **bullet point list** only (no sections, no paragraphs).
* Each list item should be a **single, concise phrase** describing one distinct work front.
* Do **not** create multiple list items for the same work front.

The goal is to have a straightforward summary of the activities, expressed as a clean, one-item-per-work-front list.

First, run the GitHub activity command: !`bin/git/github-activity -d $1`

Then analyze the output and provide the summary following the rules above.
