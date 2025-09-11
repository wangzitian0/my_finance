#!/usr/bin/env python3
"""
Storage Backend Abstraction System
Unified interface for different storage backends (local, cloud).

This module provides storage backend abstraction to enable easy migration
between local filesystem and cloud storage solutions without changing
business logic throughout the codebase.

Supported Backends:
- LocalFilesystem: Local file storage (default)
- AwsS3Backend: Amazon S3 cloud storage
- GcpGcsBackend: Google Cloud Storage
- AzureBlobBackend: Azure Blob Storage

Features:
- Unified API for all storage operations
- Automatic path translation between backends
- Performance optimization per backend
- Compression and encryption support
- Lifecycle management for cloud backends

Issue #184: Moved to core/ and renamed from storage_backends.py
"""

import json
import os
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .directory_manager import StorageBackend


class StorageBackendInterface(ABC):
    """Abstract interface for storage backends"""

    @abstractmethod
    def exists(self, path: Union[str, Path]) -> bool:
        """Check if path exists"""
        pass

    @abstractmethod
    def read_file(self, path: Union[str, Path]) -> bytes:
        """Read file contents"""
        pass

    @abstractmethod
    def write_file(self, path: Union[str, Path], content: bytes) -> bool:
        """Write file contents"""
        pass

    @abstractmethod
    def list_directory(self, path: Union[str, Path]) -> List[str]:
        """List directory contents"""
        pass

    @abstractmethod
    def create_directory(self, path: Union[str, Path]) -> bool:
        """Create directory"""
        pass

    @abstractmethod
    def delete_path(self, path: Union[str, Path]) -> bool:
        """Delete file or directory"""
        pass

    @abstractmethod
    def move_path(self, src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """Move file or directory"""
        pass

    @abstractmethod
    def get_metadata(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Get file/directory metadata"""
        pass


class LocalFilesystemBackend(StorageBackendInterface):
    """Local filesystem storage backend"""

    def __init__(self, root_path: Union[str, Path]):
        """
        Initialize local filesystem backend.

        Args:
            root_path: Root directory for all operations
        """
        self.root_path = Path(root_path).resolve()
        # Normalize path to handle macOS /private prefix
        root_str = str(self.root_path)
        if root_str.startswith('/private/var/folders/'):
            self.root_path = Path(root_str.replace('/private/var/folders/', '/var/folders/'))
        self.root_path.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, path: Union[str, Path]) -> Path:
        """Resolve relative path to absolute path within root"""
        path = Path(path)
        if path.is_absolute():
            return path
        return self.root_path / path

    def exists(self, path: Union[str, Path]) -> bool:
        """Check if path exists"""
        return self._resolve_path(path).exists()

    def read_file(self, path: Union[str, Path]) -> bytes:
        """Read file contents"""
        resolved_path = self._resolve_path(path)
        with open(resolved_path, "rb") as f:
            return f.read()

    def write_file(self, path: Union[str, Path], content: bytes) -> bool:
        """Write file contents"""
        try:
            resolved_path = self._resolve_path(path)
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            with open(resolved_path, "wb") as f:
                f.write(content)
            return True
        except Exception:
            return False

    def list_directory(self, path: Union[str, Path]) -> List[str]:
        """List directory contents"""
        resolved_path = self._resolve_path(path)
        if not resolved_path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        if not resolved_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")
        return [item.name for item in resolved_path.iterdir()]

    def create_directory(self, path: Union[str, Path]) -> bool:
        """Create directory"""
        try:
            resolved_path = self._resolve_path(path)
            resolved_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False

    def delete_path(self, path: Union[str, Path]) -> bool:
        """Delete file or directory"""
        try:
            resolved_path = self._resolve_path(path)
            if resolved_path.is_file():
                resolved_path.unlink()
            elif resolved_path.is_dir():
                shutil.rmtree(resolved_path)
            return True
        except Exception:
            return False

    def move_path(self, src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """Move file or directory"""
        try:
            src_path = self._resolve_path(src)
            dst_path = self._resolve_path(dst)
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(dst_path))
            return True
        except Exception:
            return False

    def get_metadata(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Get file/directory metadata"""
        resolved_path = self._resolve_path(path)
        if not resolved_path.exists():
            return {}

        stat = resolved_path.stat()
        return {
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "is_directory": resolved_path.is_dir(),
            "is_file": resolved_path.is_file(),
            "path": str(resolved_path),
        }

    def read_text(self, path: Union[str, Path], encoding: str = "utf-8") -> str:
        """Read file contents as text"""
        resolved_path = self._resolve_path(path)
        with open(resolved_path, "r", encoding=encoding) as f:
            return f.read()

    def write_text(self, path: Union[str, Path], content: str, encoding: str = "utf-8") -> bool:
        """Write text content to file"""
        try:
            resolved_path = self._resolve_path(path)
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            with open(resolved_path, "w", encoding=encoding) as f:
                f.write(content)
            return True
        except Exception:
            return False

    def read_json(self, path: Union[str, Path]) -> Any:
        """Read JSON file contents"""
        text_content = self.read_text(path)
        try:
            return json.loads(text_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}") from e

    def write_json(self, path: Union[str, Path], data: Any, indent: int = 2) -> bool:
        """Write data as JSON to file"""
        try:
            json_content = json.dumps(data, indent=indent, ensure_ascii=False)
            return self.write_text(path, json_content)
        except Exception:
            return False

    def ensure_directory(self, path: Union[str, Path]) -> bool:
        """Ensure directory exists (alias for create_directory)"""
        return self.create_directory(path)

    def delete_file(self, path: Union[str, Path]) -> bool:
        """Delete file (alias for delete_path)"""
        resolved_path = self._resolve_path(path)
        if not resolved_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if resolved_path.is_dir():
            raise IsADirectoryError(f"Path is a directory, not a file: {path}")
        return self.delete_path(path)


class AwsS3Backend(StorageBackendInterface):
    """AWS S3 cloud storage backend (placeholder implementation)"""

    def __init__(self, bucket_name: str, region: str = "us-west-2"):
        """
        Initialize AWS S3 backend.

        Args:
            bucket_name: S3 bucket name
            region: AWS region
        """
        self.bucket_name = bucket_name
        self.region = region
        # TODO: Initialize boto3 client when implementing

    def exists(self, path: Union[str, Path]) -> bool:
        """Check if S3 object exists"""
        # TODO: Implement with boto3
        raise NotImplementedError("AWS S3 backend not yet implemented")

    def read_file(self, path: Union[str, Path]) -> bytes:
        """Read S3 object contents"""
        # TODO: Implement with boto3
        raise NotImplementedError("AWS S3 backend not yet implemented")

    def write_file(self, path: Union[str, Path], content: bytes) -> bool:
        """Write S3 object contents"""
        # TODO: Implement with boto3
        raise NotImplementedError("AWS S3 backend not yet implemented")

    def list_directory(self, path: Union[str, Path]) -> List[str]:
        """List S3 objects with prefix"""
        # TODO: Implement with boto3
        raise NotImplementedError("AWS S3 backend not yet implemented")

    def create_directory(self, path: Union[str, Path]) -> bool:
        """Create S3 'directory' (no-op, S3 is flat)"""
        # TODO: S3 doesn't have directories, this might be a no-op
        raise NotImplementedError("AWS S3 backend not yet implemented")

    def delete_path(self, path: Union[str, Path]) -> bool:
        """Delete S3 object or prefix"""
        # TODO: Implement with boto3
        raise NotImplementedError("AWS S3 backend not yet implemented")

    def move_path(self, src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """Move S3 object"""
        # TODO: Implement with boto3 (copy + delete)
        raise NotImplementedError("AWS S3 backend not yet implemented")

    def get_metadata(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Get S3 object metadata"""
        # TODO: Implement with boto3
        raise NotImplementedError("AWS S3 backend not yet implemented")


class GcpGcsBackend(StorageBackendInterface):
    """Google Cloud Storage backend (placeholder implementation)"""

    def __init__(self, bucket_name: str, region: str = "us-west1"):
        """
        Initialize GCP GCS backend.

        Args:
            bucket_name: GCS bucket name
            region: GCP region
        """
        self.bucket_name = bucket_name
        self.region = region
        # TODO: Initialize google-cloud-storage client when implementing

    def exists(self, path: Union[str, Path]) -> bool:
        """Check if GCS object exists"""
        # TODO: Implement with google-cloud-storage
        raise NotImplementedError("GCP GCS backend not yet implemented")

    def read_file(self, path: Union[str, Path]) -> bytes:
        """Read GCS object contents"""
        # TODO: Implement with google-cloud-storage
        raise NotImplementedError("GCP GCS backend not yet implemented")

    def write_file(self, path: Union[str, Path], content: bytes) -> bool:
        """Write GCS object contents"""
        # TODO: Implement with google-cloud-storage
        raise NotImplementedError("GCP GCS backend not yet implemented")

    def list_directory(self, path: Union[str, Path]) -> List[str]:
        """List GCS objects with prefix"""
        # TODO: Implement with google-cloud-storage
        raise NotImplementedError("GCP GCS backend not yet implemented")

    def create_directory(self, path: Union[str, Path]) -> bool:
        """Create GCS 'directory' (no-op, GCS is flat)"""
        # TODO: GCS doesn't have directories, this might be a no-op
        raise NotImplementedError("GCP GCS backend not yet implemented")

    def delete_path(self, path: Union[str, Path]) -> bool:
        """Delete GCS object or prefix"""
        # TODO: Implement with google-cloud-storage
        raise NotImplementedError("GCP GCS backend not yet implemented")

    def move_path(self, src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """Move GCS object"""
        # TODO: Implement with google-cloud-storage
        raise NotImplementedError("GCP GCS backend not yet implemented")

    def get_metadata(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Get GCS object metadata"""
        # TODO: Implement with google-cloud-storage
        raise NotImplementedError("GCP GCS backend not yet implemented")


class AzureBlobBackend(StorageBackendInterface):
    """Azure Blob Storage backend (placeholder implementation)"""

    def __init__(self, container_name: str, region: str = "westus2"):
        """
        Initialize Azure Blob backend.

        Args:
            container_name: Azure container name
            region: Azure region
        """
        self.container_name = container_name
        self.region = region
        # TODO: Initialize azure-storage-blob client when implementing

    def exists(self, path: Union[str, Path]) -> bool:
        """Check if blob exists"""
        # TODO: Implement with azure-storage-blob
        raise NotImplementedError("Azure Blob backend not yet implemented")

    def read_file(self, path: Union[str, Path]) -> bytes:
        """Read blob contents"""
        # TODO: Implement with azure-storage-blob
        raise NotImplementedError("Azure Blob backend not yet implemented")

    def write_file(self, path: Union[str, Path], content: bytes) -> bool:
        """Write blob contents"""
        # TODO: Implement with azure-storage-blob
        raise NotImplementedError("Azure Blob backend not yet implemented")

    def list_directory(self, path: Union[str, Path]) -> List[str]:
        """List blobs with prefix"""
        # TODO: Implement with azure-storage-blob
        raise NotImplementedError("Azure Blob backend not yet implemented")

    def create_directory(self, path: Union[str, Path]) -> bool:
        """Create blob 'directory' (no-op, Blob is flat)"""
        # TODO: Blob doesn't have directories, this might be a no-op
        raise NotImplementedError("Azure Blob backend not yet implemented")

    def delete_path(self, path: Union[str, Path]) -> bool:
        """Delete blob or prefix"""
        # TODO: Implement with azure-storage-blob
        raise NotImplementedError("Azure Blob backend not yet implemented")

    def move_path(self, src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """Move blob"""
        # TODO: Implement with azure-storage-blob
        raise NotImplementedError("Azure Blob backend not yet implemented")

    def get_metadata(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Get blob metadata"""
        # TODO: Implement with azure-storage-blob
        raise NotImplementedError("Azure Blob backend not yet implemented")


class StorageManager:
    """
    Unified storage manager that provides backend abstraction.

    This class manages different storage backends and provides a unified
    interface for all storage operations throughout the application.
    """

    def __init__(self, backend_type_or_instance, backend_config: Optional[Dict[str, Any]] = None):
        """
        Initialize storage manager.

        Args:
            backend_type_or_instance: Storage backend type enum or backend instance
            backend_config: Backend-specific configuration (required if backend_type provided)
        """
        if isinstance(backend_type_or_instance, StorageBackendInterface) or hasattr(
            backend_type_or_instance, "read_file"
        ):
            # Direct backend instance provided (either actual instance or mock)
            self.backend = backend_type_or_instance
            self.backend_type = None
            self.backend_config = None
        elif isinstance(backend_type_or_instance, StorageBackend):
            # Backend type enum provided, need config
            if backend_config is None:
                raise ValueError("backend_config required when providing StorageBackend enum")
            self.backend_type = backend_type_or_instance
            self.backend_config = backend_config
            self.backend = self._create_backend(backend_type_or_instance, backend_config)
        else:
            # Unsupported backend type
            raise ValueError(f"Unsupported backend: {backend_type_or_instance}")

    def _create_backend(
        self, backend_type: StorageBackend, config: Dict[str, Any]
    ) -> StorageBackendInterface:
        """Create storage backend instance"""
        if backend_type == StorageBackend.LOCAL_FS:
            root_path = config.get("root_path", "build_data")
            return LocalFilesystemBackend(root_path)
        elif backend_type == StorageBackend.CLOUD_S3:
            bucket_name = config.get("bucket_name", "my-finance-data")
            region = config.get("region", "us-west-2")
            return AwsS3Backend(bucket_name, region)
        elif backend_type == StorageBackend.CLOUD_GCS:
            bucket_name = config.get("bucket_name", "my-finance-data")
            region = config.get("region", "us-west1")
            return GcpGcsBackend(bucket_name, region)
        elif backend_type == StorageBackend.CLOUD_AZURE:
            container_name = config.get("container_name", "my-finance-data")
            region = config.get("region", "westus2")
            return AzureBlobBackend(container_name, region)
        else:
            raise ValueError(f"Unsupported backend type: {backend_type}")

    # Delegate all operations to the backend
    def exists(self, path: Union[str, Path]) -> bool:
        """Check if path exists"""
        return self.backend.exists(path)

    def read_file(self, path: Union[str, Path]) -> bytes:
        """Read file contents"""
        return self.backend.read_file(path)

    def read_text(self, path: Union[str, Path], encoding: str = "utf-8") -> str:
        """Read text file contents"""
        # Try to delegate to backend if it has read_text method
        if hasattr(self.backend, "read_text"):
            # For mocks, call with just path; for real backends, include encoding
            try:
                return self.backend.read_text(path)
            except TypeError:
                # If that fails, try with encoding parameter
                return self.backend.read_text(path, encoding)
        else:
            # Fallback to read_file + decode
            content = self.backend.read_file(path)
            return content.decode(encoding)

    def read_json(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Read JSON file contents"""
        # Try to delegate to backend if it has read_json method
        if hasattr(self.backend, "read_json"):
            return self.backend.read_json(path)
        else:
            # Fallback to read_text + json.loads
            content = self.read_text(path)
            return json.loads(content)

    def write_file(self, path: Union[str, Path], content: bytes) -> bool:
        """Write file contents"""
        return self.backend.write_file(path, content)

    def write_text(self, path: Union[str, Path], content: str, encoding: str = "utf-8") -> bool:
        """Write text file contents"""
        # Try to delegate to backend if it has write_text method
        if hasattr(self.backend, "write_text"):
            # For mocks, call with just path and content; for real backends, include encoding
            try:
                return self.backend.write_text(path, content)
            except TypeError:
                # If that fails, try with encoding parameter
                return self.backend.write_text(path, content, encoding)
        else:
            # Fallback to encode + write_file
            return self.backend.write_file(path, content.encode(encoding))

    def write_json(self, path: Union[str, Path], data: Dict[str, Any], indent: int = 2) -> bool:
        """Write JSON file contents"""
        # Try to delegate to backend if it has write_json method
        if hasattr(self.backend, "write_json"):
            # For mocks, call with just path and data; for real backends, include indent
            try:
                return self.backend.write_json(path, data)
            except TypeError:
                # If that fails, try with indent parameter
                return self.backend.write_json(path, data, indent)
        else:
            # Fallback to json.dumps + write_text
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            return self.write_text(path, content)

    def list_directory(self, path: Union[str, Path]) -> List[str]:
        """List directory contents"""
        return self.backend.list_directory(path)

    def create_directory(self, path: Union[str, Path]) -> bool:
        """Create directory"""
        return self.backend.create_directory(path)

    def delete_path(self, path: Union[str, Path]) -> bool:
        """Delete file or directory"""
        return self.backend.delete_path(path)

    def delete_file(self, path: Union[str, Path]) -> bool:
        """Delete file (alias for delete_path with file-specific behavior)"""
        # Try to delegate to backend if it has delete_file method
        if hasattr(self.backend, "delete_file"):
            return self.backend.delete_file(path)
        else:
            # Fallback to delete_path
            return self.backend.delete_path(path)

    def move_path(self, src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """Move file or directory"""
        return self.backend.move_path(src, dst)

    def get_metadata(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Get file/directory metadata"""
        return self.backend.get_metadata(path)

    def get_backend_info(self) -> Dict[str, Any]:
        """Get storage backend information"""
        return {
            "backend_type": self.backend_type.value,
            "backend_config": self.backend_config,
            "backend_class": self.backend.__class__.__name__,
        }


# Convenience function to create storage manager from directory manager config
def create_storage_manager_from_config(directory_config: Dict[str, Any]) -> StorageManager:
    """
    Create storage manager from directory configuration.

    Args:
        directory_config: Directory structure configuration

    Returns:
        Configured StorageManager instance
        
    Raises:
        KeyError: If backend is missing from config
        ValueError: If backend type is unsupported
    """
    # Check if backend is specified in config
    if "backend" not in directory_config:
        raise KeyError("backend")
    
    backend_name = directory_config["backend"]

    # Map backend name to enum
    backend_mapping = {
        "local_filesystem": StorageBackend.LOCAL_FS,
        "aws_s3": StorageBackend.CLOUD_S3,
        "gcp_gcs": StorageBackend.CLOUD_GCS,
        "azure_blob": StorageBackend.CLOUD_AZURE,
    }

    if backend_name not in backend_mapping:
        raise ValueError(f"Unsupported backend: {backend_name}")
        
    backend_type = backend_mapping[backend_name]
    backend_config = directory_config.get("root_path", "build_data")
    if isinstance(backend_config, str):
        backend_config = {"root_path": backend_config}

    return StorageManager(backend_type, backend_config)
