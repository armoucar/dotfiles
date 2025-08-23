# kubectl - Kubernetes CLI Commands

This module provides convenient commands for interacting with Kubernetes using
kubectl.

## Available Commands

### Kubernetes Monitoring and Interaction

| Command | Description |
|---------|-------------|
| `cli kubectl watch-gugelmin` | Watch Gugelmin and related pods |
| `cli kubectl pod NAMESPACE INSTANCE MODE [OPTIONS]` | Interact with pods by viewing logs or executing commands |

## Pod Interaction Modes

The `pod` command supports two modes:

1. **log** - View logs from pods:

   ```bash
   cli kubectl pod NAMESPACE INSTANCE log [--since DURATION]
   ```

2. **exec** - Execute commands in pods:

   ```bash
   cli kubectl pod NAMESPACE INSTANCE exec [--command COMMAND]
   ```

## Examples

```bash
# Watch Gugelmin pods
cli kubectl watch-gugelmin

# View logs for gugelmin in the neon namespace for the last hour
cli kubectl pod neon gugelmin log --since 1h

# Execute a shell in the first gugelmin pod in the neon namespace
cli kubectl pod neon gugelmin exec

# Execute a specific command in all gugelmin pods
cli kubectl pod neon gugelmin exec --command "ls -la /app"
```

## Notes

- The `pod` command requires macOS with iTerm2 installed.
- All commands require kubectl to be installed and configured on your system.
