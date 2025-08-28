---
allowed-tools: Bash, Write
argument-hint: [issue-title] [description or context]
description: Create a new issue document in ~/Documents/Issues/ with standardized format
---

Create a new issue document based on the provided title and description. Follow this process:

1. **Generate filename**: Use current date-time format `YYYY-MM-DD--HH-MM-[issue-name].md`

2. **Create issue document** in `$HOME/Documents/Issues/` with the following structure:

```markdown
# [Issue Title]

**Date:** [Current Date]  
**Project:** [Current project name if applicable]  
**Priority:** [Low/Medium/High - default to Medium]

## Issue Description

[Detailed description of the issue]

## Current State

[Current status, versions, or conditions]

## Root Cause

[Analysis of what's causing the issue, if known]

## Impact

[Effect on the project or workflow]

## Potential Solutions

1. **[Solution 1]**: [Description]
2. **[Solution 2]**: [Description] 
3. **[Solution 3]**: [Description]

## Recommended Action

[Specific next steps or monitoring recommendations]

## Related Files

[List any relevant file paths]

## Additional Context

[Any other relevant information, dependency chains, etc.]
```

3. **Process arguments**:
   - Use `$1` as the issue title (convert to kebab-case for filename)
   - Use remaining arguments (`$2`, `$3`, etc.) as description/context
   - If no arguments provided, prompt for input

4. **Create the issue file** and confirm successful creation with the full path

The command should handle the entire workflow: directory creation, filename generation, content creation, and confirmation.
