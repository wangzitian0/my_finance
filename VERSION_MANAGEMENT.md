# P3 Version Management System

**Automated version tracking for the P3 CLI tool with git integration and automatic updates.**

## Overview

The P3 Version Management System provides:
- **Automatic version updates** after git pull operations
- **Manual version control** with semantic versioning (major.minor.patch.build)
- **Git integration** with branch and commit hash tracking
- **P3 CLI integration** with convenient commands
- **Git hooks** for seamless automation

## Quick Start

### 1. Check Current Version
```bash
p3 version                    # Show current version and git info
p3 version-check             # Check if version update is needed
```

### 2. Install Automatic Updates
```bash
p3 install-version-hooks     # Install git hooks for auto-updates
```

### 3. Manual Version Management
```bash
p3 version-increment patch   # Increment patch version (1.0.0 → 1.0.1)
p3 version-increment minor   # Increment minor version (1.0.1 → 1.1.0)  
p3 version-increment major   # Increment major version (1.1.0 → 2.0.0)
p3 version-increment build   # Increment build number (1.0.0 → 1.0.0.1)
```

### 4. Version History and Updates
```bash
p3 version-history          # Show version-related git commits
p3 version-update           # Manually check and update after git changes
```

## How It Works

### Version Format
```
major.minor.patch.build-branch+githash

Examples:
1.1.0.5-hotfix-p3-test+9ace2f3d     # Development build
2.0.1+a1b2c3d4                      # Main branch release
1.5.2.12                             # Clean build without git info
```

### Automatic Version Updates

**Git Hooks Integration:**
- **Post-merge hook** automatically updates version after `git pull`
- **Build number increments** when git hash changes
- **Branch tracking** updates when switching branches
- **Commit counting** tracks commits since last version update

**Manual Triggers:**
- Version updates when git state changes (different hash/branch)
- Force updates with `p3 version-update` command
- Manual increments with `p3 version-increment [level]`

### Version Storage

Version information is stored in `.p3_version.json`:
```json
{
  "major": 1,
  "minor": 1, 
  "patch": 0,
  "build": 5,
  "git_hash": "9ace2f3d",
  "git_branch": "hotfix/p3-test",
  "last_updated": "2025-09-01T21:58:56.112493",
  "update_count": 8
}
```

## Available Commands

### P3 CLI Commands
```bash
p3 version                   # Show current version and git information
p3 version-info             # Same as version command (detailed info)
p3 version-increment LEVEL  # Increment version (major|minor|patch|build)
p3 version-update           # Update version after git pull (auto-detects changes)
p3 version-check            # Check for potential version updates needed
p3 version-history          # Show version change history and git commits
p3 install-version-hooks    # Install git hooks for automatic version updates
```

### Direct Python Commands  
```bash
python p3_version.py info            # Show version information
python p3_version.py increment patch # Increment version level
python p3_version.py update-on-pull  # Update after git pull
python p3_version.py check-updates   # Check if update needed
python p3_version.py history         # Show git commit history
```

### Shell Scripts
```bash
./scripts/update_p3_version.sh      # Interactive version update script
python scripts/install_version_hooks.py  # Install git hooks
```

## Installation and Setup

### Automatic Installation
The version system is automatically available when using P3. No additional installation required.

### Git Hooks Installation
Enable automatic version updates after git pull:
```bash
p3 install-version-hooks
```

This installs a post-merge git hook that automatically updates the version when you pull changes.

### Manual Installation (if needed)
If the version system is not working:

1. **Ensure files exist:**
   - `p3_version.py` - Main version management module
   - `.p3_version.json` - Version storage file (created automatically)
   - `scripts/install_version_hooks.py` - Hook installer
   - `scripts/git-hooks/post-merge` - Git hook script

2. **Test the system:**
   ```bash
   python demo_p3_version.py        # Run comprehensive demo
   python test_p3_version.py        # Run validation tests
   ```

## Integration Details

### P3 CLI Integration
The version system is fully integrated into the P3 CLI:
- Version information displayed in help output
- Version commands available as `p3 version-*`
- Error handling and fallbacks when version system unavailable
- Pixi environment compatibility

### Git Integration  
- **Worktree support** - works correctly in git worktrees
- **Branch detection** - tracks current branch for version labeling
- **Commit hash tracking** - includes short commit hash in version
- **Dirty working directory** detection and warnings
- **Commit counting** since last version update

### File Structure
```
my_finance/
├── p3_version.py                    # Main version management module
├── .p3_version.json                 # Version storage (git tracked)
├── demo_p3_version.py              # Comprehensive demo script
├── test_p3_version.py              # Validation test suite
├── scripts/
│   ├── install_version_hooks.py    # Git hooks installer
│   ├── update_p3_version.sh        # Manual update script  
│   └── git-hooks/
│       └── post-merge               # Git post-merge hook
└── p3.py                           # P3 CLI with version integration
```

## Troubleshooting

### Common Issues

**"Version information not available"**
- Check if `p3_version.py` exists in project root
- Verify Python can import the module: `python -c "import p3_version"`
- Run the test suite: `python test_p3_version.py`

**"Git hooks not installed"**  
- Run: `p3 install-version-hooks`
- Check hooks directory: `ls .git/hooks/`
- Verify hook is executable: `ls -la .git/hooks/post-merge`

**Version not updating after git pull**
- Check if git hooks are installed: `p3 version` (look for hooks status)
- Manually trigger update: `p3 version-update`
- Check git hook log output during next pull

**Wrong git directory in worktrees**
- The system automatically handles worktrees
- Verify with: `p3 version` (should show correct branch)
- If issues persist, check `.git` file content

### Debug Information
```bash
# Show detailed version info
p3 version

# Check update requirements  
p3 version-check

# Show git integration status
python -c "from p3_version import get_version_manager; m=get_version_manager(); print(f'Git dir: {m._get_git_dir()}')"

# Run full system test
python test_p3_version.py
```

## Development

### Testing Changes
```bash
python demo_p3_version.py          # Run comprehensive demo
python test_p3_version.py          # Run validation tests  
p3 version-check                   # Check if system detects changes
```

### Adding New Features
1. Modify `P3VersionManager` class in `p3_version.py`
2. Add corresponding P3 CLI commands in `p3.py`
3. Update command mappings and help text
4. Add tests to `test_p3_version.py`
5. Update this documentation

### File Locations
- **Version logic:** `p3_version.py` - main module  
- **CLI integration:** `p3.py` - command definitions
- **Git hooks:** `scripts/git-hooks/post-merge`
- **Installation:** `scripts/install_version_hooks.py`
- **Storage:** `.p3_version.json` (tracked in git)

---

**The P3 Version Management System provides seamless, automated version tracking integrated directly into your development workflow.**