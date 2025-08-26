---
allowed-tools: [Read, Write, MultiEdit, Bash]
argument-hint: <tool-command-pattern>
description: Add a Claude Code tool command to permission templates and apply to current project
---

# Add Tool Command to Permission Templates

Add the provided Claude Code tool command pattern to the appropriate permission templates in your dotfiles configuration, then apply the updated template to the current project.

## Process

1. **Parse the command pattern**: `$ARGUMENTS`
   - Identify the tool type (Bash, Read, Edit, Write, etc.)
   - Assess risk level of the command

2. **Read existing templates** from `$HOME/.oh-my-zsh/custom/config/claude/templates/`:
   - `development.json` (most permissive)
   - `settings.json` (balanced permissions)
   - `strict-security.json` (read-only focus - skip updates)

3. **Categorize the command** based on risk:
   - **Allow section**: Safe operations (read, list, non-destructive commands)
   - **Ask section**: Potentially destructive operations (rm, sudo, secret access)
   - **Deny section**: Explicitly dangerous patterns (only if needed)

4. **Determine which templates to update**:
   - Always add to `development.json` if it makes sense
   - Add to `settings.json` if it's a moderate-risk command
   - Use intelligent reasoning based on command type

5. **Update the templates**:
   - Read each template file
   - Add the command pattern to the appropriate section
   - Ensure no duplicates
   - Maintain JSON formatting

6. **Update current project settings**:
   - Check if there's a `.claude/settings.json` in the current project
   - If it exists, also add the command pattern to the current project's settings file
   - **Always update** `$HOME/.oh-my-zsh/custom/config/claude/settings.json` (dotfiles main settings)
   - This ensures the updated permissions are immediately available without reapplying templates
   
7. **Re-apply current template to project** (fallback):
   - Check what template is currently applied by reading `.claude/settings.json` and looking at the `CLAUDE_PROJECT_TYPE` env variable
   - Automatically re-apply the same template using `dot claude permissions apply <current-template>`
   - This ensures the updated permissions are immediately available in the current project
   - Confirm successful re-application

## Command Analysis Rules

- **Bash commands**: Check for destructive patterns (rm, sudo, --force flags)
- **File operations**: Read operations are safer than Write/Edit
- **Development tools**: npm, pip, git are generally development-friendly
- **System commands**: Assess based on potential impact

Provide clear feedback on which templates were updated and why, then proceed with template application.
