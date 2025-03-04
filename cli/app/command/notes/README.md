# Notes CLI

A CLI tool for managing notes and tasks that stores data in YAML files.

## Features

- Create, read, update, and delete notes and tasks
- Store creation dates for all items
- Mark tasks as complete/incomplete with completion dates
- List items sorted by creation date (newest first)
- Filter items by type and tags
- Interactive selection using fzf
- Store all data as YAML files that can be committed to git
- Filenames include timestamps and the first few words of content
- Shell aliases for quick access to commands

## Usage

### Creating Items

```bash
# Create a note
dot notes create note --content "Points discussed in the meeting with marketing team"

# Create a task
dot notes create task --content "Complete the quarterly report by Friday"

# Add tags to any item type
dot notes create note --content "Discussion notes about product roadmap" --tags work --tags important
```

### Listing Items

```bash
# List all items (newest first)
dot notes list

# List items with content shown
dot notes list --show-content

# Filter by type
dot notes list --type note
dot notes list --type task

# Filter by tag
dot notes list --tag work

# List only completed tasks
dot notes list --type task --completed

# List only pending tasks
dot notes list --type task --pending
```

### Editing Items

```bash
# Edit any item (select with fzf)
dot notes edit

# Edit only notes
dot notes edit --type note

# Edit only items with a specific tag
dot notes edit --tag work
```

### Managing Task Completion

```bash
# Mark a task as completed (select from incomplete tasks with fzf)
dot notes complete

# Mark a task as incomplete (select from completed tasks with fzf)
dot notes incomplete
```

### Deleting Items

```bash
# Delete an item (select with fzf)
dot notes delete

# Delete without confirmation
dot notes delete --force
```

### Searching Content

```bash
# Search for text in notes and tasks
dot notes search "keyword"

# Search with only content lines shown
dot notes search "keyword" --content-only
```

## Aliases

To use the convenient shell aliases, add this line to your `.zshrc`:

```bash
source ~/.oh-my-zsh/custom/cli/app/command/notes/alias.zsh
```

Then you can use these shortcuts:

| Alias   | Command                             | Description                     |
|---------|-------------------------------------|---------------------------------|
| notc    | dot notes create                    | Create a new item               |
| notcn   | dot notes create note               | Create a new note               |
| notct   | dot notes create task               | Create a new task               |
| notl    | dot notes list                      | List all items                  |
| notln   | dot notes list --type note          | List notes only                 |
| notlt   | dot notes list --type task          | List tasks only                 |
| notlc   | dot notes list --type task --completed | List completed tasks         |
| notlp   | dot notes list --type task --pending   | List pending tasks           |
| notls   | dot notes list --show-content       | List with content shown         |
| notlta  | dot notes list --tag <arg>          | List by tag                     |
| note    | dot notes edit                      | Edit an item (using fzf)        |
| noten   | dot notes edit --type note          | Edit a note (using fzf)         |
| notet   | dot notes edit --type task          | Edit a task (using fzf)         |
| notcom  | dot notes complete                  | Mark a task as completed        |
| notinc  | dot notes incomplete                | Mark a task as incomplete       |
| notd    | dot notes delete                    | Delete an item (using fzf)      |
| notdf   | dot notes delete --force            | Delete without confirmation     |
| nots    | dot notes search                    | Search in notes content         |
| noth    | help                                | Show all available aliases      |

## Storage

All items are stored as YAML files in the following locations:

- Notes: `~/.oh-my-zsh/custom/notes/notes/`
- Tasks: `~/.oh-my-zsh/custom/notes/tasks/`

Each file is named with a timestamp followed by the first few words of content (e.g., `2023-04-15-14-30-22_points_discussed_in_meeting.yaml`).

Each file contains metadata like creation date, content, tags, and timestamps. For tasks, completion status and completion date are also tracked.

The directory structure is git-friendly, allowing you to version control your notes.

## Requirements

- Python 3.6+
- Click library
- PyYAML library
- fzf (for interactive selection)
- ripgrep (optional, for better search)
