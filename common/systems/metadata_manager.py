#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metadata management system for download tracking and deduplication.

Manages download metadata including MD5 checksums, timestamps, and download tracking.
Prevents unnecessary re-downloads and enables partial retry functionality.

Issue #184: Moved to systems/ as part of library restructuring
"""

import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class MetadataManager:
    """
    Manages download metadata including MD5 checksums, timestamps, and download tracking.
    Prevents unnecessary re-downloads and enables partial retry functionality.
    """

    def __init__(self, base_data_dir: str):
        self.base_data_dir = base_data_dir
        self.metadata_filename = ".metadata.json"
        self.index_filename = "README.md"

    def get_metadata_path(self, source: str, ticker: str) -> str:
        """Get the metadata file path for a specific ticker in the latest partition."""
        # Use latest symlink or find most recent partition
        latest_link = os.path.join(self.base_data_dir, source, "latest")
        if os.path.exists(latest_link):
            ticker_dir = os.path.join(latest_link, ticker)
        else:
            # Fallback: find most recent date partition
            source_dir = os.path.join(self.base_data_dir, source)
            if os.path.exists(source_dir):
                date_dirs = [
                    d
                    for d in os.listdir(source_dir)
                    if os.path.isdir(os.path.join(source_dir, d)) and d.isdigit()
                ]
                if date_dirs:
                    latest_date = max(date_dirs)
                    ticker_dir = os.path.join(source_dir, latest_date, ticker)
                else:
                    # Fallback to old structure
                    ticker_dir = os.path.join(source_dir, ticker)
            else:
                ticker_dir = os.path.join(self.base_data_dir, source, ticker)

        return os.path.join(ticker_dir, self.metadata_filename)

    def get_index_path(self, source: str, ticker: str) -> str:
        """Get the README.md index file path for a specific ticker in the latest partition."""
        # Use latest symlink or find most recent partition
        latest_link = os.path.join(self.base_data_dir, source, "latest")
        if os.path.exists(latest_link):
            ticker_dir = os.path.join(latest_link, ticker)
        else:
            # Fallback: find most recent date partition
            source_dir = os.path.join(self.base_data_dir, source)
            if os.path.exists(source_dir):
                date_dirs = [
                    d
                    for d in os.listdir(source_dir)
                    if os.path.isdir(os.path.join(source_dir, d)) and d.isdigit()
                ]
                if date_dirs:
                    latest_date = max(date_dirs)
                    ticker_dir = os.path.join(source_dir, latest_date, ticker)
                else:
                    # Fallback to old structure
                    ticker_dir = os.path.join(source_dir, ticker)
            else:
                ticker_dir = os.path.join(self.base_data_dir, source, ticker)

        return os.path.join(ticker_dir, self.index_filename)

    def calculate_file_md5(self, filepath: str) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""

    def load_metadata(self, source: str, ticker: str) -> Dict[str, Any]:
        """Load existing metadata for a ticker."""
        metadata_path = self.get_metadata_path(source, ticker)
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "ticker": ticker,
            "source": source,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "files": {},
            "download_history": [],
        }

    def save_metadata(self, source: str, ticker: str, metadata: Dict[str, Any]) -> None:
        """Save metadata for a ticker."""
        ticker_dir = os.path.join(self.base_data_dir, source, ticker)
        os.makedirs(ticker_dir, exist_ok=True)

        metadata["updated_at"] = datetime.now().isoformat()
        metadata_path = self.get_metadata_path(source, ticker)

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)

    def add_file_record(
        self,
        source: str,
        ticker: str,
        filepath: str,
        data_type: str,
        config_info: Dict[str, Any],
    ) -> None:
        """Add a file record to metadata."""
        metadata = self.load_metadata(source, ticker)

        filename = os.path.basename(filepath)
        file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        md5_hash = self.calculate_file_md5(filepath)

        file_record = {
            "filename": filename,
            "filepath": filepath,
            "data_type": data_type,
            "file_size": file_size,
            "md5_hash": md5_hash,
            "created_at": datetime.now().isoformat(),
            "config_info": config_info,
        }

        metadata["files"][filename] = file_record

        # Add to download history
        history_record = {
            "timestamp": datetime.now().isoformat(),
            "action": "file_created",
            "filename": filename,
            "data_type": data_type,
            "file_size": file_size,
        }
        metadata["download_history"].append(history_record)

        self.save_metadata(source, ticker, metadata)

    def _config_matches_ignore_exe_id(
        self, config1: Dict[str, Any], config2: Dict[str, Any]
    ) -> bool:
        """Compare two configs while ignoring the exe_id field."""
        if config1 is None or config2 is None:
            return config1 == config2

        # Create copies without exe_id for comparison
        config1_filtered = {k: v for k, v in config1.items() if k != "exe_id"}
        config2_filtered = {k: v for k, v in config2.items() if k != "exe_id"}

        return config1_filtered == config2_filtered

    def check_file_exists_recent(
        self,
        source: str,
        ticker: str,
        data_type: str,
        config_info: Dict[str, Any],
        hours: int = 24,
    ) -> bool:
        """Check if a recent file with matching config exists."""
        metadata = self.load_metadata(source, ticker)
        cutoff_time = datetime.now() - timedelta(hours=hours)

        for filename, file_record in metadata["files"].items():
            if file_record.get("data_type") == data_type and self._config_matches_ignore_exe_id(
                file_record.get("config_info"), config_info
            ):

                created_at = datetime.fromisoformat(file_record["created_at"])
                if created_at > cutoff_time:
                    # Verify file still exists and matches MD5
                    filepath = file_record["filepath"]
                    if os.path.exists(filepath) and self.calculate_file_md5(
                        filepath
                    ) == file_record.get("md5_hash", ""):
                        return True

        return False

    def get_failed_downloads(self, source: str, ticker: str) -> List[Dict[str, Any]]:
        """Get list of failed download attempts for retry."""
        metadata = self.load_metadata(source, ticker)
        failed_downloads = []

        for record in metadata["download_history"]:
            if record.get("action") == "download_failed":
                failed_downloads.append(record)

        return failed_downloads

    def mark_download_failed(
        self,
        source: str,
        ticker: str,
        data_type: str,
        config_info: Dict[str, Any],
        error_msg: str,
    ) -> None:
        """Mark a download as failed for later retry."""
        metadata = self.load_metadata(source, ticker)

        failure_record = {
            "timestamp": datetime.now().isoformat(),
            "action": "download_failed",
            "data_type": data_type,
            "config_info": config_info,
            "error_message": error_msg,
        }
        metadata["download_history"].append(failure_record)

        self.save_metadata(source, ticker, metadata)

    def generate_markdown_index(self, source: str, ticker: str) -> None:
        """Generate README.md index for a ticker directory."""
        metadata = self.load_metadata(source, ticker)
        ticker_dir = os.path.join(self.base_data_dir, source, ticker)
        index_path = self.get_index_path(source, ticker)

        # Count files by type
        file_counts = {}
        total_size = 0
        latest_date = None

        for filename, file_record in metadata["files"].items():
            data_type = file_record.get("data_type", "unknown")
            file_counts[data_type] = file_counts.get(data_type, 0) + 1
            total_size += file_record.get("file_size", 0)

            created_at = datetime.fromisoformat(file_record["created_at"])
            if latest_date is None or created_at > latest_date:
                latest_date = created_at

        # Format file size
        def format_size(size_bytes):
            if size_bytes == 0:
                return "0 B"
            size_names = ["B", "KB", "MB", "GB"]
            import math

            i = int(math.floor(math.log(size_bytes, 1024)))
            p = math.pow(1024, i)
            s = round(size_bytes / p, 2)
            return f"{s} {size_names[i]}"

        # Generate markdown content
        markdown_content = f"""# {ticker} - {source.upper()} Data

## Summary
- **Ticker**: {ticker}
- **Source**: {source}
- **Total Files**: {len(metadata["files"])}
- **Total Size**: {format_size(total_size)}
- **Last Updated**: {latest_date.strftime('%Y-%m-%d %H:%M:%S') if latest_date else 'N/A'}
- **Created**: {datetime.fromisoformat(metadata["created_at"]).strftime('%Y-%m-%d %H:%M:%S')}

## File Types
"""

        for data_type, count in sorted(file_counts.items()):
            markdown_content += f"- **{data_type}**: {count} files\n"

        markdown_content += "\n## Files\n\n"
        markdown_content += "| Filename | Type | Size | Created | MD5 Hash |\n"
        markdown_content += "|----------|------|------|---------|----------|\n"

        # Sort files by creation date (newest first)
        sorted_files = sorted(
            metadata["files"].items(), key=lambda x: x[1]["created_at"], reverse=True
        )

        for filename, file_record in sorted_files:
            created_at = datetime.fromisoformat(file_record["created_at"])
            markdown_content += f"| {filename} | {file_record.get('data_type', 'unknown')} | {format_size(file_record.get('file_size', 0))} | {created_at.strftime('%Y-%m-%d %H:%M')} | `{file_record.get('md5_hash', 'N/A')[:8]}...` |\n"

        # Add download history section
        if metadata["download_history"]:
            markdown_content += "\n## Download History\n\n"
            recent_history = sorted(
                metadata["download_history"][-10:],  # Last 10 records
                key=lambda x: x["timestamp"],
                reverse=True,
            )

            for record in recent_history:
                timestamp = datetime.fromisoformat(record["timestamp"])
                action = record.get("action", "unknown")
                if action == "file_created":
                    markdown_content += f"- **{timestamp.strftime('%Y-%m-%d %H:%M')}**: Created {record.get('filename', 'unknown')} ({record.get('data_type', 'unknown')})\n"
                elif action == "download_failed":
                    markdown_content += f"- **{timestamp.strftime('%Y-%m-%d %H:%M')}**: Failed to download {record.get('data_type', 'unknown')} - {record.get('error_message', 'Unknown error')}\n"

        markdown_content += f"\n---\n*Generated by my_finance spider system at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

    def rebuild_metadata_from_files(self, source: str, ticker: str) -> None:
        """Rebuild metadata from existing files in directory."""
        ticker_dir = os.path.join(self.base_data_dir, source, ticker)
        if not os.path.exists(ticker_dir):
            return

        metadata = {
            "ticker": ticker,
            "source": source,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "files": {},
            "download_history": [],
        }

        # Scan all JSON files in the directory
        for filename in os.listdir(ticker_dir):
            if filename.endswith(".json") and filename != self.metadata_filename:
                filepath = os.path.join(ticker_dir, filename)
                file_size = os.path.getsize(filepath)
                md5_hash = self.calculate_file_md5(filepath)

                # Parse filename to extract data type
                parts = filename.split("_")
                data_type = parts[2] if len(parts) >= 3 else "unknown"

                file_record = {
                    "filename": filename,
                    "filepath": filepath,
                    "data_type": data_type,
                    "file_size": file_size,
                    "md5_hash": md5_hash,
                    "created_at": datetime.fromtimestamp(os.path.getctime(filepath)).isoformat(),
                    "config_info": {},
                }

                metadata["files"][filename] = file_record

        # Add rebuild history record
        history_record = {
            "timestamp": datetime.now().isoformat(),
            "action": "metadata_rebuilt",
            "files_found": len(metadata["files"]),
        }
        metadata["download_history"].append(history_record)

        self.save_metadata(source, ticker, metadata)
        self.generate_markdown_index(source, ticker)

    def cleanup_orphaned_metadata(self, source: str, ticker: str) -> None:
        """Remove metadata entries for files that no longer exist."""
        metadata = self.load_metadata(source, ticker)
        files_to_remove = []

        for filename, file_record in metadata["files"].items():
            filepath = file_record["filepath"]
            if not os.path.exists(filepath):
                files_to_remove.append(filename)

        for filename in files_to_remove:
            del metadata["files"][filename]

        if files_to_remove:
            history_record = {
                "timestamp": datetime.now().isoformat(),
                "action": "cleanup_orphaned",
                "removed_files": files_to_remove,
            }
            metadata["download_history"].append(history_record)
            self.save_metadata(source, ticker, metadata)
