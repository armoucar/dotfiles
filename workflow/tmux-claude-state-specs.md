# Tmux-Claude State Management Specifications

## Overview

A state management system that preserves and restores tmux workspace organization along with associated Claude Code conversation sessions, allowing users to seamlessly continue their work across tmux server restarts.

## Core Requirements

### State Preservation

**Tmux Session State**

- Capture all active tmux sessions with their names
- Record all windows within each session
- Preserve window names and their sequential order
- Store the working directory for each window
- Remember which session and window was currently active

**Claude Session State**

- Track which tmux windows have active Claude Code instances
- Bind each Claude Code session to its specific tmux window
- Maintain persistent session identifiers that survive tmux restarts
- Associate Claude sessions with window names (not positions or indices)

### State Restoration

**Workspace Reconstruction**

- Recreate all tmux sessions with identical names
- Restore windows in each session with original names and order
- Set each window to its saved working directory
- Return focus to the previously active session and window

**Claude Session Resumption**

- Automatically restart Claude Code in windows that previously had it running
- Resume each Claude conversation exactly where it left off
- Maintain conversation history and context across restarts
- Handle cases where Claude sessions may no longer exist gracefully

### Session Lifecycle Management

**Creation Phase**

- Enable users to start new Claude sessions with persistent tracking
- Automatically generate and manage unique session identifiers
- Bind new Claude sessions to their current tmux window context

**Tracking Phase**

- Continuously maintain the relationship between tmux windows and Claude sessions
- Update state when windows are renamed or reorganized
- Clean up orphaned session mappings when windows are closed

**Recovery Phase**

- Restore both tmux organization and Claude sessions in a single operation
- Handle partial failures gracefully (restore what's possible)
- Provide clear feedback on what was successfully restored

## Behavioral Expectations

### Window Management Independence

- Users can freely rename tmux windows without breaking Claude session bindings
- Window reordering and reorganization should not affect session restoration
- The system should work regardless of window indices or positions

### Session Persistence

- Claude conversations must persist across complete tmux server shutdowns
- State should survive system reboots and terminal application restarts
- Session restoration should work after arbitrary time delays

### Error Handling

- Gracefully handle missing or corrupted Claude sessions during restoration
- Continue restoring other sessions even if some fail
- Provide meaningful feedback about restoration success and failures

### User Experience

- State saving and loading should be simple single-command operations
- The system should work transparently without requiring session ID management
- Users should be able to verify what state exists before restoration

## Success Criteria

The system successfully meets requirements when:

1. **Complete Workspace Restoration**: A user can kill their tmux server, restart it, and restore their exact workspace layout with all Claude conversations continuing seamlessly

2. **Conversation Continuity**: Claude Code sessions resume with full conversation history and context preserved

3. **Organization Preservation**: All window names, directories, and session organization remain identical after restoration

4. **Reliability**: The system works consistently across different usage patterns and handles edge cases gracefully

5. **Transparency**: Users don't need to think about session IDs, mappings, or technical details - the system just works

## Implementation Foundation

### Claude Code Session Management

Claude Code provides built-in session persistence through command-line options that enable the state management system:

**Session Creation with Specific ID**

- `claude --session-id <uuid>` - Start a new Claude session with a predetermined UUID
- The UUID must be a valid format and becomes the permanent identifier for that conversation
- This allows predictable session creation that can be tracked and later resumed

**Session Resumption**

- `claude --resume <uuid>` - Resume an existing Claude session using its UUID
- Restores the complete conversation history and context from that session
- Fails gracefully if the session UUID doesn't exist or is corrupted

**Session Discovery**

- `claude --resume` (without UUID) - Interactive session selection from available sessions
- `claude --continue` - Resume the most recently active session

### State Management Strategy

The tmux-Claude state system leverages these Claude Code capabilities by:

**UUID Management**

- Generating unique session identifiers when starting new Claude instances
- Storing the mapping between tmux windows (by name) and Claude session UUIDs
- Maintaining this mapping across tmux server restarts

**State Binding**

- Associating each Claude session UUID with its specific tmux window name
- Using window names as stable identifiers that persist through reorganization
- Tracking which windows should have Claude sessions restored

**Recovery Process**

- Reading saved tmux window organization and Claude session mappings
- Recreating tmux sessions and windows in their original configuration
- Launching `claude --resume <uuid>` in each window that previously had a Claude session

This approach ensures that both the tmux workspace structure and the Claude conversation contexts are preserved and restored as a cohesive unit.
