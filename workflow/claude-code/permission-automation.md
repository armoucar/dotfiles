# Claude Code Permission Automation

Ultra-concise guide for minimizing Claude permission prompts while maintaining safety.

## Problem Solved

Claude Code asks for permission on every file edit and bash command, interrupting your workflow. This system auto-approves safe operations while protecting against dangerous ones.

## Quick Setup

**First time setup (run once in any terminal):**

```bash
# View what's currently configured
dot claude permissions show
# or use alias: dcps

# List available permission templates
dot claude permissions list
# or use alias: dcpl
```

**Per-project setup (run in project directory):**

```bash
# Apply Claude permissions template to this project
dot claude permissions apply development
# or use alias: dcpa development

# Or apply stricter rules for sensitive projects  
dot claude permissions apply strict-security
```

## Permission Strategy

**Auto-Approved**: Read operations, safe bash commands, git operations, npm/docker commands
**Requires Confirmation**: `rm`, `sudo`, database ops, `kubectl delete`, infrastructure changes
**Smart Hook**: Context-aware decisions with detailed reasoning

## Usage in Tmux Sessions

**Start Claude in different modes:**

```bash
# Autonomous mode - most development work (recommended)  
ccsa

# Strict mode - sensitive codebases requiring confirmation
ccss

# Plan mode - code review and analysis only
ccsp

# Bypass mode - containers/isolated environments only
ccsb
```

**Session management:**

```bash
# Create dedicated tmux sessions manually if needed
tmux new-session -d -s claude-dev 'ccsa'     # autonomous mode
tmux new-session -d -s claude-review 'ccsp'  # plan mode

# Switch between sessions
tmux attach -t claude-dev
tmux attach -t claude-review
```

## What Gets Auto-Approved vs Blocked

**✅ Auto-approved operations:**

- File reads: `*.md`, `*.json`, `*.yaml`, `package.json`, configs
- Git commands: `git status`, `git diff`, `git add`, `git commit`
- Package managers: `npm run *`, `yarn *`, `pnpm *`, `uv *`
- Safe bash: `ls`, `pwd`, `cat`, `grep`, `find`, `mkdir`
- Container queries: `docker ps`, `podman logs`, `kubectl get`

**⚠️ Requires confirmation:**

- File deletions: `rm *`, `rmdir *`
- Privilege escalation: `sudo *`
- Database operations: `DROP`, `DELETE`, `TRUNCATE`
- Infrastructure: `kubectl delete`, `terraform destroy`, `helm uninstall`
- Dangerous flags: `--force`, `-f`, `rm -rf`

**🔒 Smart decisions for:**

- Credential files (`.env*`, `secrets/`, `.ssh/`) - asks permission
- Unknown commands - asks permission with context

## Project-Specific Configuration

**Why use the scripts:**

- Global settings apply to all projects but some need different rules
- Sensitive projects need stricter permissions
- Development projects can be more permissive

**When to run per-project setup:**

```bash
cd /path/to/your/project

# For most projects (permissive, good for active development)
~/.claude/scripts/setup-permissions.sh init development

# For sensitive/production codebases (asks confirmation more often)
~/.claude/scripts/setup-permissions.sh init strict-security

# This creates .claude/settings.json that overrides global settings
```

## Troubleshooting

**Still getting too many prompts?**

```bash
# Check what's configured  
dot claude permissions show
# or alias: dcps

# List available templates to find a more permissive one
dot claude permissions list
# or alias: dcpl
```

**Commands being blocked unexpectedly?**

```bash
# Check audit log to see what's happening
tail -f .claude/command.log | jq .

# Show current permissions
dot claude permissions show
# or alias: dcps
```

## Available Commands

**Main commands:**

- `dot claude permissions list` - List available templates
- `dot claude permissions apply <template>` - Apply template to project
- `dot claude permissions show` - Show current configuration
- `dot claude permissions reset` - Reset global settings

**Quick start aliases:**

- `ccsa` - Start Claude in autonomous mode (recommended)
- `ccss` - Start Claude in strict mode  
- `ccsp` - Start Claude in plan-only mode
- `ccsb` - Start Claude in bypass mode

**Management aliases (shorter commands):**

- `dcpa` → `dot claude permissions apply`
- `dcps` → `dot claude permissions show`
- `dcpl` → `dot claude permissions list`

**Bin scripts (standalone executables):**

- `claude-templates` - List available templates

## Files Created/Modified

- `~/.claude/settings.json` - Global permissions (modified)
- `~/.claude/hooks/smart_permissions.py` - Intelligent hook (new)
- `config/claude/templates/` - Project templates (moved)
- `cli/app/command/claude/` - Python CLI commands (new)
- `zsh/tools/claude.zsh` - Aliases (updated)
- `.claude/settings.json` - Per-project overrides (created by init)
