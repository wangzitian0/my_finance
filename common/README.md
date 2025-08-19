# Common - Shared Components

Manages interactions between different modules, defines schemas and shared tools. Responsible for inter-module coordination and data standardization.

## Core Components

### MetadataManager (`metadata_manager.py`)
Comprehensive metadata tracking system that prevents unnecessary data re-downloads and provides efficient data management.

**Features:**
- ✅ **Markdown indexes** - Each directory gets a `README.md` with comprehensive file listings
- ✅ **Download deduplication** - Prevent unnecessary re-downloads to conserve third-party quotas  
- ✅ **Partial retry mechanism** - Retry only failed downloads, not successful ones
- ✅ **Index rebuilding** - Reconstruct metadata and indexes after manual file changes
- ✅ **Comprehensive tracking** - MD5 checksums, timestamps, version info, and download history

**Usage Example:**
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
```

### BuildTracker (`build_tracker.py`)
Tracks build executions with comprehensive manifests and artifact management.

**Features:**
- Unique build IDs with timestamp
- BUILD_MANIFEST.md generation
- Build artifact tracking
- Status monitoring

### Configuration (`config.py`)
Configuration management utilities for different data tiers and job configurations.

### Logger (`logger.py`)
Centralized logging system with execution ID tracking.

### Progress (`progress.py`)
Progress tracking utilities for long-running operations.

### Utils (`utils.py`)
General utility functions shared across the project.

## Command Line Usage

### Pixi Commands (Recommended)

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

## Metadata Format

Each ticker directory contains:
```
data/stage_01_extract/<source>/<date_partition>/<ticker>/
├── .metadata.json          # Comprehensive metadata
├── README.md               # Human-readable index
├── <ticker>_<source>_<oid>_<timestamp>.json  # Data files
└── ...
```

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
    }
  ]
}
```

## Download Deduplication Logic

### YFinance Spider
- Checks for existing data within **24 hours** by default
- Compares config parameters: period, interval, oid
- Verifies file exists and MD5 matches recorded hash
- Skips download if recent valid data found

### SEC Edgar Spider  
- Checks for existing data within **7 days** by default
- Compares config parameters: filing_type, count, email
- Verifies downloaded files in subdirectories
- Skips download if recent valid data found

## Migration from Old System

For existing data:
1. Run metadata rebuild: `pixi run metadata-rebuild`
2. Generate indexes: `pixi run metadata-index`
3. Verify with: `pixi run metadata-list`

---

*This system fully implements comprehensive metadata tracking and download deduplication for efficient, quota-aware data collection.*