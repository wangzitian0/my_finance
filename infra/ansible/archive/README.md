# Ansible Archive

## 📁 Archived Files

This directory contains legacy and specialized ansible playbooks that were consolidated into the simplified 3-file structure (`setup.yml`, `start.yml`, `stop.yml`).

### Archived Playbooks

- **`init.yml`** - Legacy comprehensive environment setup (replaced by `setup.yml`)
- **`reset.yml`** - Environment reset and cleanup (functionality moved to `p3 reset` command)
- **`ollama.yml`** - AI model setup (specialized functionality, rarely used)
- **`p3_ready_setup.yml`** - P3 ready command specific setup (merged into `setup.yml`)
- **`p3_stop_cleanup.yml`** - P3 stop command specific cleanup (functionality in `stop.yml`)

### Migration Notes

These files were archived on 2025-09-10 as part of the ansible directory consolidation to simplify the infrastructure management to just 3 core operations:

1. **SETUP** (`setup.yml`) - Environment initialization
2. **START** (`start.yml`) - Service startup  
3. **STOP** (`stop.yml`) - Service shutdown

### Recovery

If any specific functionality from these archived playbooks is needed, they can be restored or their relevant tasks can be integrated back into the core 3-file structure.

### Usage History

- These files were part of the original complex 22-file ansible structure
- Most functionality has been consolidated or moved to direct P3 command implementations
- Role modules (`roles/`) were preserved for modular functionality