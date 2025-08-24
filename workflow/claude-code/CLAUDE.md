# Claude Code Workflows

This directory contains workflows and documentation for managing Claude Code configuration and hooks.

## Available Documentation

### hooks-management.md

Complete workflow for managing Claude Code hooks including:

- Current hook types (Notification, Command Logger, Stop)
- Adding new hooks step-by-step process
- Hook script structure and best practices
- Audio management and troubleshooting

This workflow covers the complete setup from creating hook scripts to syncing configuration through the `setup-claude.zsh` script.

### jsonl-observability.md

Documentation for the JSONL-based observability logging system:

- Comprehensive metadata capture for all tool usage
- Session isolation using session_id
- Queryable log format with jq examples
- Integration with stop hook for auto-formatting

This provides full observability into Claude Code sessions for debugging and analysis.

### markdownlint-autoformat.md

Documentation for automatic markdown formatting in the stop hook:

- Cross-directory support for files outside the project
- Intelligent config file discovery
- Working directory management for external files
- Troubleshooting formatting issues

This ensures consistent markdown formatting across all Claude-modified files.
