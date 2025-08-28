---
allowed-tools: Write, WebFetch
argument-hint: <command-name> <description>
description: Create a new user command with c- prefix and full guidance
---

# Create New User Command

Create a new user command named `/c-$ARGUMENTS` in the ~/.claude/commands/ directory.

## Process

1. First, read the official documentation to understand best practices:
   - Read @docs-external/claude-code-docs/docs/slash-commands.md
   - Review custom slash command features and syntax

2. Create the command following these guidelines:
   - Use the `c-` prefix naming convention
   - Save as `.md` file in `~/.claude/commands/`
   - Include proper frontmatter with:
     - `description`: Brief command description
     - `allowed-tools`: Tools the command can use
     - `argument-hint`: Expected arguments format
     - `model`: Specific model if needed

3. Template structure:

   ```markdown
   ---
   allowed-tools: [relevant tools]
   argument-hint: [expected arguments]
   description: [brief description]
   ---

   [Command prompt content]
   ```

Extract the command name (without c- prefix) and description from the arguments to create a well-structured, functional user command.
