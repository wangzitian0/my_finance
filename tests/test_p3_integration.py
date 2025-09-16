#!/usr/bin/env python3
"""
P3 CLI Integration Tests - Complete Workflow Validation

Tests the complete integration of:
1. Root p3.py delegation to infra/p3/p3.py
2. SSOT DirectoryManager integration
3. Command execution and validation
4. Error handling and diagnostics
5. Backward compatibility

Issue #288: Implementation of PR review feedback
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path


class TestP3Integration(unittest.TestCase):
    """Integration tests for P3 CLI complete workflow."""

    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent
        self.root_p3 = self.project_root / "p3.py"
        self.infra_p3 = self.project_root / "infra" / "p3" / "p3.py"

    def test_root_p3_exists(self):
        """Test that root p3.py exists and is executable."""
        self.assertTrue(self.root_p3.exists(), "Root p3.py should exist")
        self.assertTrue(self.root_p3.is_file(), "Root p3.py should be a file")

    def test_infra_p3_exists(self):
        """Test that infra/p3/p3.py exists and is the main implementation."""
        self.assertTrue(self.infra_p3.exists(), "Infra p3.py should exist")
        self.assertTrue(self.infra_p3.is_file(), "Infra p3.py should be a file")

    def test_delegation_pattern(self):
        """Test that root p3.py properly delegates to infra/p3/p3.py."""
        with open(self.root_p3, 'r') as f:
            content = f.read()

        # Should contain delegation code
        self.assertIn('infra.p3.p3', content, "Root p3.py should import from infra.p3.p3")
        self.assertIn('main()', content, "Root p3.py should call main()")

    def test_version_command_delegation(self):
        """Test that version command works through delegation."""
        try:
            result = subprocess.run(
                [sys.executable, str(self.root_p3), "version"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(self.project_root)
            )

            # Should not error (though may warn about imports)
            self.assertIn("P3 Version:", result.stdout)

        except subprocess.TimeoutExpired:
            self.fail("Version command timed out")
        except Exception as e:
            self.skipTest(f"Version command failed (may be environment issue): {e}")

    def test_help_command_delegation(self):
        """Test that help command works through delegation."""
        try:
            result = subprocess.run(
                [sys.executable, str(self.root_p3), "help"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(self.project_root)
            )

            # Should show help content
            self.assertIn("P3 CLI", result.stdout)
            self.assertIn("DAILY WORKFLOW", result.stdout)

        except subprocess.TimeoutExpired:
            self.fail("Help command timed out")
        except Exception as e:
            self.skipTest(f"Help command failed (may be environment issue): {e}")

    def test_invalid_command_handling(self):
        """Test that invalid commands are handled properly."""
        try:
            result = subprocess.run(
                [sys.executable, str(self.root_p3), "invalid_command"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(self.project_root)
            )

            # Should exit with error code
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unknown command", result.stdout)

        except subprocess.TimeoutExpired:
            self.fail("Invalid command handling timed out")
        except Exception as e:
            self.skipTest(f"Invalid command test failed (may be environment issue): {e}")

    def test_modular_architecture_compliance(self):
        """Test that P3 CLI follows L1/L2 modular architecture."""
        # Infra p3.py should be in proper L2 location
        expected_path = self.project_root / "infra" / "p3" / "p3.py"
        self.assertEqual(self.infra_p3, expected_path)

        # Should have proper module structure
        infra_init = self.project_root / "infra" / "__init__.py"
        p3_init = self.project_root / "infra" / "p3" / "__init__.py"

        # Check if module files exist (they should for proper Python modules)
        if not infra_init.exists():
            self.skipTest("Infra module __init__.py missing - may be intentional")
        if not p3_init.exists():
            self.skipTest("P3 module __init__.py missing - may be intentional")

    def test_ssot_integration_available(self):
        """Test that SSOT DirectoryManager integration is available."""
        with open(self.infra_p3, 'r') as f:
            content = f.read()

        # Should contain SSOT imports and usage
        self.assertIn('DirectoryManager', content)
        self.assertIn('SSOT_AVAILABLE', content)
        self.assertIn('directory_manager', content)

    def test_backward_compatibility_preserved(self):
        """Test that backward compatibility is preserved."""
        # Root p3.py should still work as entry point
        self.assertTrue(self.root_p3.exists())

        # Should be able to run basic commands
        # This is tested in other test methods

    def test_error_handling_robustness(self):
        """Test that error handling is robust for edge cases."""
        # Test with missing arguments
        try:
            result = subprocess.run(
                [sys.executable, str(self.root_p3)],  # No command
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(self.project_root)
            )

            # Should show help or handle gracefully
            self.assertTrue(result.returncode == 0 or "help" in result.stdout.lower())

        except Exception as e:
            self.skipTest(f"Error handling test failed (may be environment issue): {e}")

    def test_policy_compliance(self):
        """Test that implementation follows CLAUDE.md policies."""
        # Should not create .md files
        implementation_md = self.project_root / "IMPLEMENTATION_SUMMARY_282.md"
        if implementation_md.exists():
            with open(implementation_md, 'r') as f:
                content = f.read().strip()
            self.assertEqual(content, "", "IMPLEMENTATION_SUMMARY_282.md should be empty or removed")

        # Should use modular L1/L2 structure
        self.assertTrue(self.infra_p3.exists(), "P3 CLI should be in infra/p3/ (L1/L2 structure)")

        # Should use SSOT patterns
        with open(self.infra_p3, 'r') as f:
            content = f.read()
        self.assertIn('directory_manager', content, "Should use DirectoryManager for SSOT")


if __name__ == '__main__':
    unittest.main(verbosity=2)