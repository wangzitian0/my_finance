# Spider Metadata System

This document describes the new metadata tracking system that prevents unnecessary data re-downloads, provides comprehensive tracking, and enables efficient data management.

## Overview

The metadata system implements the following features as requested in [Issue #38](https://github.com/wangzitian0/my_finance/issues/38):

✅ **Markdown indexes** - Each directory gets a `README.md` with comprehensive file listings
✅ **Download deduplication** - Prevent unnecessary re-downloads to conserve third-party quotas  
✅ **Partial retry mechanism** - Retry only failed downloads, not successful ones
✅ **Index rebuilding** - Reconstruct metadata and indexes after manual file changes
✅ **Comprehensive tracking** - MD5 checksums, timestamps, version info, and download history

## Architecture

### Core Components

1. **MetadataManager** (`common/metadata_manager.py`)
   - Central class for all metadata operations
   - Handles MD5 calculation, file tracking, and index generation
   - Thread-safe and efficient file operations

2. **Updated Spiders**
   - `spider/yfinance_spider.py` - Enhanced with metadata integration
   - `spider/sec_edgar_spider.py` - Enhanced with metadata integration
   - Both check for existing data before downloading

3. **Management Scripts**
   - `scripts/manage_metadata.py` - Metadata management utilities
   - `scripts/retry_failed.py` - Retry failed downloads selectively

4. **Pixi Integration**
   - New commands in `pixi.toml` for easy metadata management

### Data Structure

Each ticker directory contains:
```
data/original/<source>/<ticker>/
├── .metadata.json          # Comprehensive metadata
├── README.md               # Human-readable index
├── <ticker>_<source>_<oid>_<timestamp>.json  # Data files
└── ...
```

## Metadata Format

### .metadata.json Structure

```json
{
  "ticker": "AAPL",
  "source": "yfinance",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T12:00:00",
  "version": "1.0.0",
  "files": {
    "AAPL_yfinance_1d_240101-100000.json": {
      "filename": "AAPL_yfinance_1d_240101-100000.json",
      "filepath": "/full/path/to/file.json",
      "data_type": "1d",
      "file_size": 1024000,
      "md5_hash": "a1b2c3d4e5f6...",
      "created_at": "2024-01-01T10:00:00",
      "config_info": {
        "period": "1y",
        "interval": "1d",
        "oid": "1d",
        "exe_id": "yfinance_1d_240101-100000"
      }
    }
  },
  "download_history": [
    {
      "timestamp": "2024-01-01T10:00:00",
      "action": "file_created",
      "filename": "AAPL_yfinance_1d_240101-100000.json",
      "data_type": "1d",
      "file_size": 1024000
    },
    {
      "timestamp": "2024-01-01T11:00:00",
      "action": "download_failed",
      "data_type": "1h",
      "config_info": {...},
      "error_message": "API rate limit exceeded"
    }
  ]
}
```

### README.md Format

```markdown
# AAPL - YFINANCE Data

## Summary
- **Ticker**: AAPL
- **Source**: yfinance
- **Total Files**: 5
- **Total Size**: 2.5 MB
- **Last Updated**: 2024-01-01 12:00:00
- **Created**: 2024-01-01 10:00:00

## File Types
- **1d**: 2 files
- **1h**: 2 files
- **5m**: 1 files

## Files
| Filename | Type | Size | Created | MD5 Hash |
|----------|------|------|---------|----------|
| AAPL_yfinance_1d_240101-120000.json | 1d | 512 KB | 2024-01-01 12:00 | `a1b2c3d4...` |
| AAPL_yfinance_1h_240101-110000.json | 1h | 1.2 MB | 2024-01-01 11:00 | `b2c3d4e5...` |

## Download History
- **2024-01-01 12:00**: Created AAPL_yfinance_1d_240101-120000.json (1d)
- **2024-01-01 11:30**: Failed to download 5m - API rate limit exceeded
- **2024-01-01 11:00**: Created AAPL_yfinance_1h_240101-110000.json (1h)
```

## Usage

### Command Line Interface

#### Pixi Commands (Recommended)

```bash
# List all sources and tickers
pixi run metadata-list

# Rebuild metadata from existing files
pixi run metadata-rebuild

# Generate/update README.md indexes
pixi run metadata-index

# Show failed downloads
pixi run metadata-failures

# Clean up orphaned metadata entries
pixi run metadata-cleanup

# Retry failed downloads
pixi run retry-failed
```

#### Direct Script Usage

```bash
# Metadata management
python scripts/manage_metadata.py list
python scripts/manage_metadata.py rebuild --source yfinance --ticker AAPL
python scripts/manage_metadata.py index --source sec-edgar
python scripts/manage_metadata.py failures
python scripts/manage_metadata.py cleanup

# Retry failed downloads
python scripts/retry_failed.py
python scripts/retry_failed.py --source yfinance --ticker AAPL
python scripts/retry_failed.py --dry-run  # Show what would be retried
```

### Programmatic Usage

```python
from common.metadata_manager import MetadataManager

# Initialize
mm = MetadataManager("/path/to/data/original")

# Check if recent data exists (prevents re-download)
config_info = {"period": "1y", "interval": "1d", "oid": "1d"}
if mm.check_file_exists_recent("yfinance", "AAPL", "1d", config_info, hours=24):
    print("Recent data exists, skipping download")

# Add file record after successful download
mm.add_file_record("yfinance", "AAPL", "/path/to/file.json", "1d", config_info)

# Generate README.md
mm.generate_markdown_index("yfinance", "AAPL")

# Mark failed download for later retry
mm.mark_download_failed("yfinance", "AAPL", "1h", config_info, "Rate limit exceeded")

# Rebuild metadata from existing files
mm.rebuild_metadata_from_files("yfinance", "AAPL")
```

## Download Deduplication Logic

### YFinance Spider
- Checks for existing data within **24 hours** by default
- Compares config parameters: period, interval, oid
- Verifies file exists and MD5 matches recorded hash
- Skips download if recent valid data found

### SEC Edgar Spider  
- Checks for existing data within **7 days** by default (filings change less frequently)
- Compares config parameters: filing_type, count, email
- Verifies downloaded files in subdirectories
- Skips download if recent valid data found

## Retry Mechanism

### Failed Download Tracking
- All download failures are logged with timestamp and error message
- Config information is preserved for accurate retry
- Failed downloads don't prevent successful ones from being tracked

### Retry Process
1. `retry_failed.py` scans metadata for failed downloads
2. Groups failures by source and ticker
3. Creates temporary config files for each retry batch
4. Executes appropriate spider with retry config
5. Updates metadata with retry results

### Retry Configuration
- **YFinance**: Creates config with unique data_periods from failures
- **SEC Edgar**: Creates config with unique file_types from failures
- Preserves original parameters (count, email, etc.)

## Index Rebuilding

### Manual File Management
When files are manually added/removed:

```bash
# Rebuild metadata for specific ticker
pixi run metadata-rebuild --source yfinance --ticker AAPL

# Rebuild metadata for entire source  
pixi run metadata-rebuild --source sec-edgar

# Rebuild everything
pixi run metadata-rebuild
```

### Automated Rebuilding
- `rebuild_metadata_from_files()` scans directory for JSON files
- Recreates metadata based on file timestamps and names
- Generates MD5 hashes for existing files
- Creates comprehensive download history

## Error Handling

### File Integrity
- MD5 checksums verify file integrity
- Corrupted files are detected during existence checks
- Missing files trigger metadata cleanup

### Download Failures
- Network errors are logged with full context
- API rate limits are tracked separately
- Partial failures don't affect successful downloads

### Metadata Corruption
- Metadata files can be rebuilt from scratch
- JSON parsing errors fall back to rebuild process
- Invalid metadata entries are cleaned up automatically

## Performance Considerations

### Efficiency Features
- MD5 calculation uses streaming for large files
- File existence checks before expensive operations
- Batch processing for multiple operations
- Efficient JSON serialization with proper defaults

### Scalability
- Metadata operations are per-ticker (independent)
- No global state or locks required
- Memory usage scales with individual file metadata only
- Suitable for thousands of tickers

## Migration from Old System

### For Existing Data
1. Run metadata rebuild: `pixi run metadata-rebuild`
2. Generate indexes: `pixi run metadata-index`
3. Verify with: `pixi run metadata-list`

### Compatibility
- Old data files are fully compatible
- Filename patterns remain unchanged
- Directory structure preserved
- New features are additive only

---

*This system fully implements the requirements from [GitHub Issue #38](https://github.com/wangzitian0/my_finance/issues/38) and provides a solid foundation for efficient, quota-aware data downloading with comprehensive tracking and management capabilities.*