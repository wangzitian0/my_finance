# CRITICAL: Remove systems/ Directory

## Issue #257 Implementation - Directory Cleanup Required

The `common/systems/` directory is obsolete and must be manually removed:

```bash
rm -rf common/systems/
```

### Why Remove systems/?

1. **Broken imports**: The `systems/__init__.py` tries to import files that don't exist
2. **Duplicate functionality**: All functionality moved to proper subdirectories:
   - `systems/build_tracker.py` → `build/build_tracker.py` 
   - `systems/quality_reporter.py` → `build/quality_reporter.py`
   - `systems/metadata_manager.py` → `build/metadata_manager.py` 
   - `systems/graph_rag_schema.py` → `schemas/graph_rag_schema.py`

### Verification

After removal, verify:
- Main `common/__init__.py` imports work (✅ already tested)
- No external code imports from `common.systems` (✅ checked dcf_engine uses correct imports)
- All functionality accessible through new structure (✅ verified)

This completes Issue #257: Simplify common/ directory structure.