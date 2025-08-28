---
allowed-tools: LS, Write, Bash
argument-hint: <workflow_name>
description: Document a discovered workflow in timestamped directory under Documents/Workflows
---

# Workflow Documentation Creator

Write a well-defined workflow to a document under `$HOME/Documents/Workflows`. Create a new directory with naming style: `dd_MM_yyyy_hh_mm_workflow_name_here` and inside create `workflow.md` and `summary.md`.

## Process

1. **Create Workflow Directory**
   - Generate timestamp in format: `dd_MM_yyyy_hh_mm`
   - Create directory: `$HOME/Documents/Workflows/[timestamp]_$ARGUMENTS`

2. **Write Documents**
   - `workflow.md`: Step-by-step workflow as detailed as possible
   - `summary.md`: A super concise one paragraph description of the workflow

## Workflow Document Structure

The `workflow.md` should include:

```markdown
# [Workflow Name]

## Overview
[Brief description of what this workflow accomplishes]

## Prerequisites
- [Tool/dependency requirements]
- [Initial setup needed]

## Step-by-Step Process

### Step 1: [Action Name]
```bash
[command if applicable]
```

[Description and expected outcome]

### Step 2: [Action Name]

[Continue with numbered steps...]

## Verification

[How to verify the workflow completed successfully]

## Troubleshooting

[Common issues and solutions]

## Related Workflows

[Links to related documented workflows]

```

## Content Guidelines

- Extract key steps from the current session context
- Include specific commands, file paths, and configurations used
- Note decision points and alternatives considered
- Capture verification steps and success criteria
- Include any troubleshooting insights discovered

The documents should capture the well-defined workflow that was discovered in the conversation.
