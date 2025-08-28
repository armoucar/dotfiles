---
allowed-tools: [Bash, Read, Edit, MultiEdit, Grep, Glob]
argument-hint: "[dependency names (optional)] - specify dependencies to update, or leave empty to update all"
description: "Update UV dependencies, check outdated packages, update pyproject.toml ranges, and sync workspace"
---

You are tasked with updating UV dependencies in this project. Follow this process:

1. **Check outdated dependencies**: Run `uv tree --outdated --depth 1` to see which direct dependencies are outdated.

2. **Present options to user**: Show the user all available dependency updates and ask them which ones they want to update. Wait for their response before proceeding.

3. **Update selected dependencies**:
   - For each dependency the user selects, use `uv add <package>@latest` or similar to get the latest version
   - Update the version ranges in pyproject.toml files to reflect the new versions (important: the user wants updated ranges, not pinned versions)

4. **Generate lock file and sync**:
   - Ensure `uv.lock` is generated properly
   - Run `uv sync --all-extras --all-packages` to sync the workspace

5. **Report results**: Summarize what dependencies were updated and their new versions.

Arguments provided: $ARGUMENTS
