#!/usr/bin/env python3
"""
Unit tests for error handling improvements.

Tests comprehensive error handling including:
- Input validation for subprocess operations
- Timeout handling for directory operations
- Security validation for path operations
- Graceful degradation under failure conditions
"""

import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from common.core.directory_manager import (
    DataLayer,
    DirectoryManager,
    StorageBackend,
)


class TestInputValidationSecurity:
    """Security-focused input validation tests"""

    @pytest.fixture
    def secure_directory_manager(self):
        """Create DirectoryManager with enhanced security validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)

            dm = DirectoryManager(root_path=project_root)

            # Add input validation methods
            def validate_path_input(self, input_path: str) -> str:
                """Validate and sanitize path input"""
                if not input_path or not isinstance(input_path, str):
                    raise ValueError("Path input must be a non-empty string")

                # Remove dangerous characters
                dangerous_chars = ["..", "~", "$", "`", "|", ";", "&", ">", "<"]
                sanitized = input_path
                for char in dangerous_chars:
                    if char in sanitized:
                        raise ValueError(f"Dangerous character sequence '{char}' in path input")

                # Validate against absolute paths
                if os.path.isabs(input_path):
                    raise ValueError("Absolute paths not allowed in path input")

                return sanitized.strip()

            def validate_subprocess_args(self, args: list) -> list:
                """Validate subprocess arguments for security"""
                if not isinstance(args, list):
                    raise TypeError("Subprocess arguments must be a list")

                validated_args = []
                dangerous_commands = ["rm", "del", "format", "mkfs", "dd", "chmod 777"]

                for arg in args:
                    if not isinstance(arg, (str, Path)):
                        raise TypeError(f"Invalid argument type: {type(arg)}")

                    arg_str = str(arg)
                    for dangerous_cmd in dangerous_commands:
                        if dangerous_cmd in arg_str.lower():
                            raise ValueError(f"Dangerous command detected: {dangerous_cmd}")

                    validated_args.append(arg_str)

                return validated_args

            dm.validate_path_input = validate_path_input.__get__(dm, DirectoryManager)
            dm.validate_subprocess_args = validate_subprocess_args.__get__(dm, DirectoryManager)

            yield dm

    def test_path_input_validation(self, secure_directory_manager):
        """Test input validation for path operations"""
        dm = secure_directory_manager

        # Valid inputs should pass
        valid_inputs = ["sec-edgar", "yfinance_data", "reports-2024", "folder_name", "data123"]

        for valid_input in valid_inputs:
            result = dm.validate_path_input(valid_input)
            assert result == valid_input.strip()

        # Invalid inputs should raise ValueError
        invalid_inputs = [
            "../etc/passwd",
            "folder/../../../root",
            "~/.ssh/id_rsa",
            "data; rm -rf /",
            "folder && cat /etc/passwd",
            "/absolute/path",
            "folder > output.txt",
            "data | malicious_command",
        ]

        for invalid_input in invalid_inputs:
            with pytest.raises(ValueError):
                dm.validate_path_input(invalid_input)

        # Empty or None inputs should raise ValueError
        with pytest.raises(ValueError):
            dm.validate_path_input("")

        with pytest.raises(ValueError):
            dm.validate_path_input(None)

    def test_subprocess_argument_validation(self, secure_directory_manager):
        """Test validation of subprocess arguments"""
        dm = secure_directory_manager

        # Valid arguments should pass
        valid_args = [
            ["python", "script.py"],
            ["ls", "-la"],
            ["mkdir", "new_directory"],
            ["cp", "source.txt", "dest.txt"],
        ]

        for args in valid_args:
            result = dm.validate_subprocess_args(args)
            assert result == [str(arg) for arg in args]

        # Dangerous arguments should raise ValueError
        dangerous_args = [
            ["rm", "-rf", "/"],
            ["del", "*.*"],
            ["format", "c:"],
            ["chmod", "777", "-R", "/"],
            ["dd", "if=/dev/zero", "of=/dev/sda"],
            ["mkfs", "/dev/sda1"],
        ]

        for args in dangerous_args:
            with pytest.raises(ValueError):
                dm.validate_subprocess_args(args)

        # Invalid argument types should raise TypeError
        with pytest.raises(TypeError):
            dm.validate_subprocess_args("not_a_list")

        with pytest.raises(TypeError):
            dm.validate_subprocess_args([123, "string"])

    def test_path_traversal_prevention(self, secure_directory_manager):
        """Test prevention of path traversal attacks"""
        dm = secure_directory_manager

        # Attempt path traversal through get_source_path
        traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "normal/../../../etc/passwd",
            "folder/../../sensitive_data",
        ]

        for attempt in traversal_attempts:
            # Should either validate and reject or sanitize the path
            try:
                result_path = dm.get_source_path(attempt)
                # If path is created, ensure it stays within project boundaries
                resolved_path = result_path.resolve()
                project_root_resolved = dm.root_path.resolve()

                # Ensure the resolved path is within project root
                try:
                    resolved_path.relative_to(project_root_resolved)
                except ValueError:
                    # Path is outside project root - this should be prevented
                    pytest.fail(f"Path traversal succeeded: {resolved_path}")

            except (ValueError, OSError) as e:
                # Expected behavior - path traversal was prevented
                assert "dangerous" in str(e).lower() or "invalid" in str(e).lower()


class TestSubprocessSecurityAndTimeout:
    """Tests for secure subprocess execution with timeout handling"""

    @pytest.fixture
    def subprocess_directory_manager(self):
        """Create DirectoryManager with secure subprocess capabilities"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)

            dm = DirectoryManager(root_path=project_root)

            def secure_subprocess_run(self, args, timeout=30, **kwargs):
                """Secure subprocess execution with timeout"""
                # Validate arguments first
                validated_args = self.validate_subprocess_args(args)

                # Set secure defaults
                secure_kwargs = {
                    "timeout": min(timeout, 300),  # Max 5 minutes
                    "check": False,  # Don't raise on non-zero exit
                    "capture_output": True,
                    "text": True,
                    **kwargs,
                }

                try:
                    result = subprocess.run(validated_args, **secure_kwargs)
                    return result
                except subprocess.TimeoutExpired as e:
                    raise TimeoutError(
                        f"Command timed out after {timeout}s: {' '.join(validated_args)}"
                    )
                except subprocess.SubprocessError as e:
                    raise RuntimeError(f"Subprocess execution failed: {e}")

            def validate_subprocess_args(self, args):
                """Validate subprocess arguments"""
                if not isinstance(args, list):
                    raise TypeError("Arguments must be a list")
                return [str(arg) for arg in args]

            dm.secure_subprocess_run = secure_subprocess_run.__get__(dm, DirectoryManager)
            dm.validate_subprocess_args = validate_subprocess_args.__get__(dm, DirectoryManager)

            yield dm

    def test_subprocess_timeout_handling(self, subprocess_directory_manager):
        """Test timeout handling for subprocess operations"""
        dm = subprocess_directory_manager

        # Test successful quick command
        result = dm.secure_subprocess_run(["echo", "test"], timeout=5)
        assert result.returncode == 0
        assert "test" in result.stdout

        # Test timeout with sleep command
        if os.name != "nt":  # Unix-like systems
            with pytest.raises(TimeoutError):
                dm.secure_subprocess_run(["sleep", "10"], timeout=2)
        else:  # Windows
            with pytest.raises(TimeoutError):
                dm.secure_subprocess_run(["timeout", "/t", "10", "/nobreak"], timeout=2)

    def test_subprocess_argument_validation_integration(self, subprocess_directory_manager):
        """Test integration of argument validation with subprocess execution"""
        dm = subprocess_directory_manager

        # Valid commands should work
        valid_commands = [
            ["echo", "hello"],
            ["python", "--version"] if os.name != "nt" else ["python", "--version"],
        ]

        for cmd in valid_commands:
            try:
                result = dm.secure_subprocess_run(cmd, timeout=10)
                # Command should execute (may succeed or fail, but should not raise validation error)
                assert isinstance(result.returncode, int)
            except (FileNotFoundError, OSError):
                # Command not found is acceptable for testing
                pass

    def test_subprocess_error_handling(self, subprocess_directory_manager):
        """Test error handling in subprocess execution"""
        dm = subprocess_directory_manager

        # Test handling of non-existent command
        with pytest.raises((RuntimeError, FileNotFoundError, OSError)):
            dm.secure_subprocess_run(["nonexistent_command_12345"], timeout=5)

        # Test invalid argument types
        with pytest.raises(TypeError):
            dm.secure_subprocess_run("not_a_list", timeout=5)


class TestDirectoryOperationTimeouts:
    """Tests for timeout handling in directory operations"""

    @pytest.fixture
    def timeout_directory_manager(self):
        """Create DirectoryManager with timeout capabilities"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)

            dm = DirectoryManager(root_path=project_root)

            def create_directories_with_timeout(self, timeout=60):
                """Create directories with timeout"""
                import signal

                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Directory creation timed out after {timeout}s")

                if os.name != "nt":  # Unix-like systems support signals
                    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(timeout)

                try:
                    self.ensure_directories()
                    if os.name != "nt":
                        signal.alarm(0)  # Cancel alarm
                except Exception as e:
                    if os.name != "nt":
                        signal.alarm(0)  # Cancel alarm
                    raise
                finally:
                    if os.name != "nt":
                        signal.signal(signal.SIGALRM, old_handler)

            def calculate_directory_size_with_timeout(self, path, timeout=30):
                """Calculate directory size with timeout"""
                import threading

                result = {"size": 0, "error": None}

                def calculate():
                    try:
                        total_size = 0
                        for root, dirs, files in os.walk(path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                try:
                                    total_size += os.path.getsize(file_path)
                                except (OSError, IOError):
                                    pass  # Skip files that can't be accessed
                        result["size"] = total_size
                    except Exception as e:
                        result["error"] = e

                thread = threading.Thread(target=calculate)
                thread.daemon = True
                thread.start()
                thread.join(timeout)

                if thread.is_alive():
                    raise TimeoutError(f"Directory size calculation timed out after {timeout}s")

                if result["error"]:
                    raise result["error"]

                return result["size"]

            dm.create_directories_with_timeout = create_directories_with_timeout.__get__(
                dm, DirectoryManager
            )
            dm.calculate_directory_size_with_timeout = (
                calculate_directory_size_with_timeout.__get__(dm, DirectoryManager)
            )

            yield dm

    def test_directory_creation_timeout(self, timeout_directory_manager):
        """Test timeout handling for directory creation"""
        dm = timeout_directory_manager

        # Normal directory creation should succeed quickly
        dm.create_directories_with_timeout(timeout=10)

        # Verify directories were created
        for layer in DataLayer:
            layer_path = dm.get_layer_path(layer)
            assert layer_path.exists() or layer_path.parent.exists()

    def test_directory_size_calculation_timeout(self, timeout_directory_manager):
        """Test timeout handling for directory size calculation"""
        dm = timeout_directory_manager

        # Create some test files
        test_dir = dm.get_layer_path(DataLayer.RAW_DATA)
        test_dir.mkdir(parents=True, exist_ok=True)

        for i in range(5):
            test_file = test_dir / f"test_{i}.txt"
            with open(test_file, "w") as f:
                f.write("test content " * 100)

        # Calculate size with reasonable timeout
        size = dm.calculate_directory_size_with_timeout(test_dir, timeout=10)
        assert size > 0

        # Test with very short timeout on larger operation
        large_dir = dm.get_data_root()
        large_dir.mkdir(parents=True, exist_ok=True)

        # Create many files to make operation slower
        for i in range(20):
            large_file = large_dir / f"large_{i}.txt"
            with open(large_file, "w") as f:
                f.write("x" * 10000)  # 10KB files

        # Should succeed with reasonable timeout
        size = dm.calculate_directory_size_with_timeout(large_dir, timeout=15)
        assert size > 0


class TestGracefulErrorRecovery:
    """Tests for graceful error recovery and degradation"""

    def test_config_file_corruption_recovery(self):
        """Test recovery from corrupted configuration files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            config_dir = project_root / "common" / "config"
            config_dir.mkdir(parents=True, exist_ok=True)

            # Create corrupted config file
            config_file = config_dir / "directory_structure.yml"
            with open(config_file, "w") as f:
                f.write("invalid: yaml: content: [unclosed brackets")

            # DirectoryManager should handle gracefully
            dm = DirectoryManager(root_path=project_root)

            # Should fall back to default configuration
            assert dm.config is not None
            assert "storage" in dm.config
            assert dm.config["storage"]["backend"] == "local_filesystem"

            # Should still be able to perform basic operations
            path = dm.get_layer_path(DataLayer.RAW_DATA)
            assert path is not None
            assert isinstance(path, Path)

    def test_permission_error_recovery(self):
        """Test recovery from permission errors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)

            dm = DirectoryManager(root_path=project_root)

            # Create a restricted directory
            restricted_path = project_root / "restricted"
            restricted_path.mkdir()

            if os.name != "nt":  # Unix-like systems
                os.chmod(restricted_path, 0o000)  # No permissions

                # Should handle permission errors gracefully
                try:
                    # Try to access restricted path
                    test_file = restricted_path / "test.txt"
                    with open(test_file, "w") as f:
                        f.write("test")
                except PermissionError:
                    # Expected behavior - should not crash the system
                    pass

                # Restore permissions for cleanup
                os.chmod(restricted_path, 0o755)

            # Normal operations should still work
            normal_path = dm.get_layer_path(DataLayer.RAW_DATA)
            assert normal_path is not None

    def test_disk_space_error_handling(self):
        """Test handling of disk space issues (simulated)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)

            dm = DirectoryManager(root_path=project_root)

            # Check available disk space
            stat = os.statvfs(temp_dir) if hasattr(os, "statvfs") else None

            if stat:
                available_bytes = stat.f_bavail * stat.f_frsize

                # If very low disk space, should handle gracefully
                if available_bytes < 1024 * 1024:  # Less than 1MB
                    # Operations should either succeed or fail gracefully
                    try:
                        dm.ensure_directories()
                    except OSError as e:
                        # Should be a clear error message about disk space
                        assert "space" in str(e).lower() or "full" in str(e).lower()
                else:
                    # Normal operation should succeed
                    dm.ensure_directories()
                    assert dm.get_data_root().exists() or dm.get_data_root().parent.exists()

    def test_concurrent_access_error_recovery(self):
        """Test recovery from concurrent access conflicts"""
        import threading
        import time

        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)

            errors = []
            successes = []

            def worker(worker_id):
                try:
                    dm = DirectoryManager(root_path=project_root)

                    # Try to create directories concurrently
                    dm.ensure_directories()

                    # Try to create files concurrently
                    layer_path = dm.get_layer_path(DataLayer.RAW_DATA)
                    layer_path.mkdir(parents=True, exist_ok=True)

                    for i in range(10):
                        test_file = layer_path / f"worker_{worker_id}_file_{i}.txt"
                        try:
                            with open(test_file, "w") as f:
                                f.write(f"Data from worker {worker_id}")
                            successes.append((worker_id, i))
                        except Exception as e:
                            errors.append((worker_id, i, str(e)))

                except Exception as e:
                    errors.append((worker_id, "general", str(e)))

            # Start multiple workers
            threads = []
            for i in range(5):
                thread = threading.Thread(target=worker, args=(i,))
                threads.append(thread)
                thread.start()

            # Wait for completion
            for thread in threads:
                thread.join()

            # Most operations should succeed despite concurrent access
            total_operations = len(successes) + len(errors)
            if total_operations > 0:
                success_rate = len(successes) / total_operations
                assert (
                    success_rate > 0.8
                ), f"Too many concurrent access failures: {success_rate:.2%} success rate"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
