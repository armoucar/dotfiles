---
allowed-tools: Grep, LS, Read, Glob
argument-hint: [source: claude|dspy|all] [search query]
description: Search and retrieve documentation content into conversation context
---

# Documentation Search Command

Search documentation and include the full content in the conversation context for reference. This don't trigger the `docs-search` subagent. This is a command that is used to search the documentation and return the full content in the conversation context for reference.

## Arguments

- **$1**: Documentation source (`claude`, `dspy`, or `all`)
- **$2+**: Search query terms

## Available Sources

- **claude**: Claude Code documentation (`docs-external/claude-code-docs/docs/`)
- **dspy**: DSPy framework documentation (`docs-external/dspy/docs/docs/`)
- **all**: Search across all available documentation sources

## Process

Based on the specified source, search the documentation using:

1. **Content search**: Use grep to find relevant files containing the query terms
2. **File name search**: Find files with names matching the query
3. **Context extraction**: Read and include relevant sections in the conversation
4. **Source attribution**: Clearly indicate which documentation source and file each result comes from

### Search Strategy

- Use case-insensitive searches
- Search both file names and content
- Look for variations of search terms
- Include surrounding context for better understanding
- Return actual documentation content, not summaries

### Output Format

For each result, provide:

- **Source**: Documentation type (Claude Code, DSPy, etc.)
- **File**: Relative path within the documentation
- **Content**: Relevant sections from the documentation
- **Context**: Brief explanation of how it relates to the query

If no results are found, suggest alternative search terms or indicate what documentation is available to search.

## Examples

- `/c-docs-search claude hooks` - Search Claude docs for hook information
- `/c-docs-search dspy signatures` - Search DSPy docs for signature information
- `/c-docs-search all modules` - Search all docs for module-related content
