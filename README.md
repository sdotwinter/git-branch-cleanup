# Git Branch Cleanup

A CLI tool to detect merged branches, identify stale branches, provide safe deletion with undo capability, and enforce team branch policies.

## Features

- **Detect Merged Branches**: Find branches that have been merged into main/master
- **Detect Stale Branches**: Identify branches not updated in N days (default 30)
- **Safe Deletion**: Delete branches with confirmation and logging
- **Deletion Log**: Track deleted branches for potential recovery
- **Policy Check**: Validate branches against team naming conventions
- **List All Branches**: View all branches with status indicators

## Installation

```bash
# Clone the repository
git clone https://github.com/sdotwinter/git-branch-cleanup.git
cd git-branch-cleanup

# Make the script executable
chmod +x main.py
```

## Usage

```bash
# Show help
python main.py --help

# Detect merged branches
python main.py --detect-merged

# Detect stale branches (default 30 days)
python main.py --detect-stale

# Detect stale branches (custom days)
python main.py --detect-stale --days 60

# List all branches with status
python main.py --list

# Delete specific branches (with confirmation)
python main.py --delete branch1 branch2

# Force delete branches (use with caution)
python main.py --force-delete branch1 branch2

# Check branches against team policies
python main.py --policy-check

# Use custom remote name
python main.py --detect-merged --remote upstream
```

## Examples

### Clean up merged branches
```bash
# First, detect merged branches
python main.py --detect-merged

# Then delete them
python main.py --delete feature/login bugfix/typo
```

### Find and review stale branches
```bash
# Find branches not updated in 90 days
python main.py --detect-stale --days 90

# List all branches with their status
python main.py --list
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `--detect-merged` | Detect branches merged into main/master |
| `--detect-stale` | Detect stale branches |
| `--days N` | Number of days for stale detection (default: 30) |
| `--delete BRANCH...` | Delete specified branches |
| `--force-delete BRANCH...` | Force delete branches |
| `--list` | List all branches with status |
| `--remote NAME` | Remote name (default: origin) |
| `--policy-check` | Check against team policies |
| `--help` | Show help message |

## Deletion Log

Deleted branches are logged to `.git_branch_cleanup_log.json` in the repository root. This log includes:
- Timestamp of deletion
- List of deleted branch names
- Current branch at time of deletion

## Safety Features

- **Confirmation Required**: Deletion requires explicit confirmation
- **Current Branch Protection**: Cannot delete the current branch
- **Logging**: All deletions are logged for audit/recovery
- **Policy Validation**: Optional team policy enforcement

## License

MIT License

## Author

sdotwinter
