---
allowed-tools: LS, Write, Bash
argument-hint: <spec_name>
description: Write a well-defined plan to Documents/Specs with detailed plan.md and concise summary.md
---

# Specs Writer

Write a well-defined plan to a document under `$HOME/Documents/Specs`. Create a new directory with naming style: `dd_MM_yyyy_hh_mm_good_spec_name_here` and inside create `plan.md` and `summary.md`.

## Process

1. **Create Spec Directory**
   - Generate timestamp in format: `yyyy_MM_dd_hh_mm`
   - Create directory: `$HOME/Documents/Specs/[timestamp]_$ARGUMENTS`

2. **Write Documents**
   - `plan.md`: The plan as detailed as it can be
   - `summary.md`: A super concise one paragraph description of the plan

The documents should capture the well-defined plan that was just created in the conversation.