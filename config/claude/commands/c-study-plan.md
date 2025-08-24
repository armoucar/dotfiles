---
allowed-tools: [Write, Read, LS, Glob, Bash]
argument-hint: <technology/topic with optional depth level>
description: Intelligent study plan manager that auto-detects existing studies and creates depth-appropriate plans
---

# Intelligent Study Plan Manager

Manage study plans for: **$ARGUMENTS**

## Smart Workflow

1. **Parse Input**: Extract topic and depth level from the description
   - **Depth Keywords**:
     - `deep`, `detailed`, `comprehensive`, `robust`, `thorough` → Detailed plan (8-10 topics/level)
     - `superficial`, `quick`, `basic`, `light`, `overview` → Light plan (2-3 topics/level)  
     - Default → Standard plan (3-4 topics/level)

2. **Search Existing Studies**:
   - Read all `*-summary.md` files in `$HOME/.oh-my-zsh/custom/study/`
   - Use summary content to intelligently match user's topic
   - Look for keyword matches, related technologies, similar focus areas

3. **Auto-Decision Logic**:
   - **Strong Match Found**: Continue existing study
     - Display current study file and progress
     - Show completed items and highlight next topics
     - Suggest focus areas based on unchecked items
   - **No Match Found**: Create new comprehensive study
     - Generate new study with appropriate depth level
     - Create both `{topic}.md` and `{topic}-summary.md` files

4. **For Continuing Studies**: Progress tracking and guidance

## Study Session Workflow

**CRITICAL**: Never mark topics as completed until user explicitly indicates they're done:

1. **Present Content**: Provide study material for the requested topic
2. **Wait for User**: Let user study, ask questions, request clarifications
3. **Take Notes**: Only when user says "take notes" or similar
4. **Mark Complete**: Only when user says "next topic", "I'm done with this", or similar

**Never automatically mark topics as [x] completed!**

## Note-Taking Policy

**CRITICAL**: Only take notes when user explicitly requests it. Examples:

- "take notes on X"
- "add this to my notes"
- "write this down"

**Never automatically add notes** during study sessions. Just provide information.

**When taking notes**: Ultra concise format

- Bullet points only
- Key facts/commands/concepts
- No explanations or elaboration
- Maximum 3-5 bullets per topic

## Study Creation Requirements

### File Structure

1. **Main Study File**: `{topic}.md` (kebab-case filename)
2. **Summary File**: `{topic}-summary.md` with topic description and keywords
3. **Location**: `$HOME/.oh-my-zsh/custom/study/` folder

### Study Plan Structure

Create progressive learning plan with three levels, adjusted by depth:

**Basics** → **Intermediate** → **Advanced**

### Depth-Based Topic Count

- **Light** (2-3 topics/level): Quick overviews, essential concepts only
- **Standard** (3-4 topics/level): Balanced coverage, practical focus
- **Detailed** (8-10 topics/level): Comprehensive, thorough exploration

### Format Requirements

- Use checkboxes `- [ ]` with **bold topic name** and brief description
- Create placeholder sections under "Notes" for each topic  
- Include "Study Progress" section at top with all checkboxes
- Add separator `---` between progress and notes sections
- Make topics specific to the technology/framework
- Focus on practical, hands-on learning objectives

### Summary File Template

```markdown
# {Topic} Study Summary

{Single concise paragraph describing the study topic, covering main areas of focus, key technologies, learning objectives, and practical applications. Include relevant keywords naturally within the description for intelligent matching.}
```

## Usage Examples

- `c-study-plan "rust web development"` → Auto-detect, standard depth
- `c-study-plan "deep dive into kubernetes"` → Detailed plan (8-10 topics)
- `c-study-plan "quick python overview"` → Light plan (2-3 topics)  
- `c-study-plan "continue my claude studies"` → Auto-match existing study
- `c-study-plan "comprehensive react hooks guide"` → Detailed React plan

**Execute the intelligent workflow now based on the provided arguments.**
