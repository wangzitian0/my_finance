#!/usr/bin/env python3
"""
Unit tests for storage_manager.py - Storage Backend Abstraction Layer
Tests local filesystem operations and cloud storage abstractions.
"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, mock_open, patch

import pytest

from common.core.directory_manager import StorageBackend
from common.core.storage_manager import (
    LocalFilesystemBackend,
    StorageBackendInterface,
    StorageManager,
    create_storage_manager_from_config,
)


class TestStorageBackendInterface:
    """Test the storage backend interface contract."""

    def test_interface_methods_exist(self):
        """Test that interface defines required methods."""
        # Check that abstract methods exist on the class
        assert hasattr(StorageBackendInterface, "read_file")
        assert hasattr(StorageBackendInterface, "write_file")
        assert hasattr(StorageBackendInterface, "exists")
        assert hasattr(StorageBackendInterface, "list_directory")
        assert hasattr(StorageBackendInterface, "create_directory")
        assert hasattr(StorageBackendInterface, "delete_path")
        assert hasattr(StorageBackendInterface, "move_path")
        assert hasattr(StorageBackendInterface, "get_metadata")

    def test_interface_not_implemented(self):
        """Test that we cannot instantiate abstract interface directly."""
        # Abstract classes should not be instantiable
        with pytest.raises(TypeError):
            StorageBackendInterface()


@pytest.mark.core
class TestLocalFilesystemBackend:
    """Test local filesystem storage backend."""

    def test_initialization(self, temp_dir: Path):
        """Test backend initialization."""
        backend = LocalFilesystemBackend(root_path=temp_dir)
        # Use resolve() to handle symlinks like /var -> /private/var on macOS
        assert backend.root_path.resolve() == temp_dir.resolve()

    def test_initialization_with_string_path(self, temp_dir: Path):
        """Test backend initialization with string path."""
        backend = LocalFilesystemBackend(root_path=str(temp_dir))
        # Use resolve() to handle symlinks like /var -> /private/var on macOS
        assert backend.root_path.resolve() == temp_dir.resolve()

    def test_resolve_path(self, temp_dir: Path):
        """Test path resolution."""
        backend = LocalFilesystemBackend(root_path=temp_dir)

        # Test absolute path resolution
        resolved = backend._resolve_path(Path("subfolder/file.txt"))
        expected = temp_dir / "subfolder" / "file.txt"
        # Use resolve() to handle symlinks like /var -> /private/var on macOS
        assert resolved.resolve() == expected.resolve()

        # Test relative path resolution
        resolved = backend._resolve_path(Path("./relative/file.txt"))
        expected = temp_dir / "relative" / "file.txt"
        # Use resolve() to handle symlinks like /var -> /private/var on macOS
        assert resolved.resolve() == expected.resolve()

    def test_read_text_success(self, temp_dir: Path):
        """Test successful text file reading."""
        backend = LocalFilesystemBackend(root_path=temp_dir)

        # Create test file
        test_file = temp_dir / "test.txt"
        test_content = "Hello, World!"
        test_file.write_text(test_content)

        # Test reading
        result = backend.read_text(Path("test.txt"))
        assert result == test_content

    def test_read_text_file_not_found(self, temp_dir: Path):
        """Test reading non-existent file raises FileNotFoundError."""
        backend = LocalFilesystemBackend(root_path=temp_dir)

        with pytest.raises(FileNotFoundError):
            backend.read_text(Path("nonexistent.txt"))

    def test_write_text_success(self, temp_dir: Path):
        """Test successful text file writing."""
        backend = LocalFilesystemBackend(root_path=temp_dir)

        test_content = "Test content"
        backend.write_text(Path("output.txt"), test_content)

        # Verify file was created and content is correct
        output_file = temp_dir / "output.txt"
        assert output_file.exists()
        assert output_file.read_text() == test_content

    def test_write_text_creates_directory(self, temp_dir: Path):
        """Test writing creates parent directories."""
        backend = LocalFilesystemBackend(root_path=temp_dir)

        test_content = "Test content"
        backend.write_text(Path("nested/folder/file.txt"), test_content)

        # Verify nested directories were created
        output_file = temp_dir / "nested" / "folder" / "file.txt"
        assert output_file.exists()
        assert output_file.read_text() == test_content

    def test_read_json_success(self, temp_dir: Path):
        """Test successful JSON file reading."""
        backend = LocalFilesystemBackend(root_path=temp_dir)

        # Create test JSON file
        test_data = {"key": "value", "number": 42}
        test_file = temp_dir / "test.json"
        test_file.write_text(json.dumps(test_data))

        # Test reading
        result = backend.read_json(Path("test.json"))
        assert result == test_data

    def test_read_json_invalid_json(self, temp_dir: Path):
        """Test reading invalid JSON raises ValueError."""
        backend = LocalFilesystemBackend(root_path=temp_dir)

        # Create invalid JSON file
        test_file = temp_dir / "invalid.json"
        test_file.write_text("invalid json content")

        with pytest.raises(ValueError, match="Invalid JSON"):
            backend.read_json(Path("invalid.json"))

    def test_write_json_success(self, temp_dir: Path):
        """Test successful JSON file writing."""
        backend = LocalFilesystemBackend(root_path=temp_dir)

        test_data = {"key": "value", "array": [1, 2, 3]}
        backend.write_json(Path("output.json"), test_data)

        # Verify file was created and content is correct
        output_file = temp_dir / "output.json"
        assert output_file.exists()
        loaded_data = json.loads(output_file.read_text())
        assert loaded_data == test_data

    def test_exists_true(self, temp_dir: Path):
        """Test exists returns True for existing files."""
        backend = LocalFilesystemBackend(root_path=temp_dir)

        # Create test file
        test_file = temp_dir / "exists.txt"
        test_file.write_text("content")

        assert backend.exists(Path("exists.txt")) is True

    def test_exists_false(self, temp_dir: Path):
        """Test exists returns False for non-existent files."""
        backend = LocalFilesystemBackend(root_path=temp_dir)

        assert backend.exists(Path("nonexistent.txt")) is False

    def test_list_directory_success(self, temp_dir: Path):
        """Test successful directory listing."""
        backend = LocalFilesystemBackend(root_path=temp_dir)

        # Create test files
        (temp_dir / "file1.txt").write_text("content1")
        (temp_dir / "file2.json").write_text('{"key": "value"}')
        (temp_dir / "subfolder").mkdir()

        result = backend.list_directory(Path("."))
        assert "file1.txt" in result
        assert "file2.json" in result
        assert "subfolder" in result

    def test_list_directory_empty(self, temp_dir: Path):
        """Test listing empty directory."""
        backend = LocalFilesystemBackend(root_path=temp_dir)

        # Create empty subfolder
        empty_folder = temp_dir / "empty"
        empty_folder.mkdir()

        result = backend.list_directory(Path("empty"))
        assert result == []

    def test_list_directory_not_found(self, temp_dir: Path):
        """Test listing non-existent directory raises FileNotFoundError."""
        backend = LocalFilesystemBackend(root_path=temp_dir)

        with pytest.raises(FileNotFoundError):
            backend.list_directory(Path("nonexistent"))

    def test_ensure_directory_new(self, temp_dir: Path):
        """Test creating new directory."""
        backend = LocalFilesystemBackend(root_path=temp_dir)

        backend.ensure_directory(Path("new/nested/folder"))

        created_dir = temp_dir / "new" / "nested" / "folder"
        assert created_dir.exists()
        assert created_dir.is_dir()

    def test_ensure_directory_existing(self, temp_dir: Path):
        """Test ensuring existing directory doesn't raise error."""
        backend = LocalFilesystemBackend(root_path=temp_dir)

        existing_dir = temp_dir / "existing"
        existing_dir.mkdir()

        # Should not raise error
        backend.ensure_directory(Path("existing"))
        assert existing_dir.exists()

    def test_delete_file_success(self, temp_dir: Path):
        """Test successful file deletion."""
        backend = LocalFilesystemBackend(root_path=temp_dir)

        # Create test file
        test_file = temp_dir / "delete_me.txt"
        test_file.write_text("content")
        assert test_file.exists()

        # Delete file
        backend.delete_file(Path("delete_me.txt"))
        assert not test_file.exists()

    def test_delete_file_not_found(self, temp_dir: Path):
        """Test deleting non-existent file raises FileNotFoundError."""
        backend = LocalFilesystemBackend(root_path=temp_dir)

        with pytest.raises(FileNotFoundError):
            backend.delete_file(Path("nonexistent.txt"))


@pytest.mark.core
class TestStorageManager:
    """Test the StorageManager orchestration class."""

    def test_initialization_with_backend_instance(self, mock_storage_backend):
        """Test initialization with backend instance."""
        manager = StorageManager(mock_storage_backend)
        assert manager.backend == mock_storage_backend

    def test_initialization_with_backend_enum(self, temp_dir: Path):
        """Test initialization with backend enum."""
        config = {"root_path": str(temp_dir)}
        manager = StorageManager(StorageBackend.LOCAL_FS, config)

        assert isinstance(manager.backend, LocalFilesystemBackend)
        assert manager.backend.root_path == temp_dir

    def test_initialization_unsupported_backend(self):
        """Test initialization with unsupported backend raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported backend"):
            StorageManager("unsupported_backend")

    def test_read_text_delegates(self, mock_storage_backend):
        """Test read_text delegates to backend."""
        mock_storage_backend.read_text.return_value = "file content"
        manager = StorageManager(mock_storage_backend)

        result = manager.read_text(Path("test.txt"))

        assert result == "file content"
        mock_storage_backend.read_text.assert_called_once_with(Path("test.txt"))

    def test_write_text_delegates(self, mock_storage_backend):
        """Test write_text delegates to backend."""
        manager = StorageManager(mock_storage_backend)

        manager.write_text(Path("test.txt"), "content")

        mock_storage_backend.write_text.assert_called_once_with(Path("test.txt"), "content")

    def test_read_json_delegates(self, mock_storage_backend):
        """Test read_json delegates to backend."""
        mock_data = {"key": "value"}
        mock_storage_backend.read_json.return_value = mock_data
        manager = StorageManager(mock_storage_backend)

        result = manager.read_json(Path("test.json"))

        assert result == mock_data
        mock_storage_backend.read_json.assert_called_once_with(Path("test.json"))

    def test_write_json_delegates(self, mock_storage_backend):
        """Test write_json delegates to backend."""
        test_data = {"key": "value"}
        manager = StorageManager(mock_storage_backend)

        manager.write_json(Path("test.json"), test_data)

        mock_storage_backend.write_json.assert_called_once_with(Path("test.json"), test_data)

    def test_exists_delegates(self, mock_storage_backend):
        """Test exists delegates to backend."""
        mock_storage_backend.exists.return_value = True
        manager = StorageManager(mock_storage_backend)

        result = manager.exists(Path("test.txt"))

        assert result is True
        mock_storage_backend.exists.assert_called_once_with(Path("test.txt"))

    def test_list_directory_delegates(self, mock_storage_backend):
        """Test list_directory delegates to backend."""
        mock_files = ["file1.txt", "file2.json"]
        mock_storage_backend.list_directory.return_value = mock_files
        manager = StorageManager(mock_storage_backend)

        result = manager.list_directory(Path("folder"))

        assert result == mock_files
        mock_storage_backend.list_directory.assert_called_once_with(Path("folder"))


@pytest.mark.core
class TestStorageManagerCreation:
    """Test storage manager factory functions."""

    def test_create_storage_manager_local_fs(self, temp_dir: Path):
        """Test creating LocalFilesystem storage manager."""
        config = {"backend": "local_filesystem", "root_path": str(temp_dir)}

        manager = create_storage_manager_from_config(config)

        assert isinstance(manager, StorageManager)
        assert isinstance(manager.backend, LocalFilesystemBackend)
        assert manager.backend.root_path == temp_dir

    def test_create_storage_manager_missing_backend(self):
        """Test creating storage manager with missing backend raises KeyError."""
        config = {"root_path": "/tmp"}

        with pytest.raises(KeyError, match="backend"):
            create_storage_manager_from_config(config)

    def test_create_storage_manager_unsupported_backend(self):
        """Test creating storage manager with unsupported backend."""
        config = {"backend": "unsupported", "root_path": "/tmp"}

        with pytest.raises(ValueError, match="Unsupported backend"):
            create_storage_manager_from_config(config)

    def test_create_storage_manager_default_config(self):
        """Test creating storage manager with default config."""
        config = {"backend": "local_filesystem"}

        manager = create_storage_manager_from_config(config)

        assert isinstance(manager, StorageManager)
        assert isinstance(manager.backend, LocalFilesystemBackend)
        # Should use default root_path
        assert "build_data" in str(manager.backend.root_path)


@pytest.mark.integration
class TestStorageManagerIntegration:
    """Integration tests for StorageManager with real filesystem operations."""

    def test_end_to_end_file_operations(self, temp_dir: Path):
        """Test complete file operation workflow."""
        # Create storage manager
        config = {"root_path": str(temp_dir)}
        manager = StorageManager(StorageBackend.LOCAL_FS, config)

        # Test directory creation and file writing
        test_path = Path("integration/test/file.txt")
        test_content = "Integration test content"

        manager.write_text(test_path, test_content)

        # Test file existence
        assert manager.exists(test_path)

        # Test file reading
        read_content = manager.read_text(test_path)
        assert read_content == test_content

        # Test directory listing
        files = manager.list_directory(Path("integration/test"))
        assert "file.txt" in files

        # Test file deletion
        manager.delete_file(test_path)
        assert not manager.exists(test_path)

    def test_json_operations_integration(self, temp_dir: Path):
        """Test JSON file operations integration."""
        config = {"root_path": str(temp_dir)}
        manager = StorageManager(StorageBackend.LOCAL_FS, config)

        # Test data
        test_data = {"integration": True, "data": [1, 2, 3], "nested": {"key": "value"}}

        # Write JSON
        json_path = Path("data/test.json")
        manager.write_json(json_path, test_data)

        # Read and verify JSON
        loaded_data = manager.read_json(json_path)
        assert loaded_data == test_data

        # Verify file exists and can be read as text too
        assert manager.exists(json_path)
        json_text = manager.read_text(json_path)
        assert "integration" in json_text
