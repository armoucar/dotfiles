---
allowed-tools: Write, WebFetch
argument-hint: <command-name> <description>
description: Create a new user command with c- prefix and full guidance
---

# Create New User Command

Create a new user command in the ~/.claude/commands/ directory with the `c-` prefix naming convention.

## Process

1. First, read the official documentation to understand best practices:
   - Read @docs-external/claude-code-docs/docs/slash-commands.md
   - Review custom slash command features and syntax

2. Parse the arguments to extract command name and description from `$ARGUMENTS`

3. Create the command following these guidelines:
   - **IMPORTANT**: Always use the `c-` prefix in the filename (e.g., `c-git-approve.md`)
   - Save as `.md` file in `~/.claude/commands/`
   - The actual slash command will be `/c-[name]` (e.g., `/c-git-approve`)
   - Include proper frontmatter with:
     - `description`: Brief command description
     - `allowed-tools`: Tools the command can use
     - `argument-hint`: Expected arguments format
     - `model`: Specific model if needed

4. Template structure:

   ```markdown
   ---
   allowed-tools: [relevant tools]
   argument-hint: [expected arguments]
   description: [brief description]
   ---

   [Command prompt content using $ARGUMENTS]
   ```

**Critical**: The filename MUST start with `c-` prefix. For example, if creating a git approval command, the file should be named `c-git-approve.md`, making the command available as `/c-git-approve`.
