#!/usr/bin/env python3
"""
Release Management System for my_finance project

Handles creation and management of releases, pushing build artifacts
to the my_finance_data repository for version control and distribution.

Migrated from scripts/release_manager.py as part of infrastructure modularization.
"""
import argparse
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ReleaseManager:
    """Manages release creation and distribution to my_finance_data repository."""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_repo_url = "https://github.com/wangzitian0/my_finance_data.git"
        self.data_repo_name = "my_finance_data"

    def get_latest_build(self) -> Optional[Path]:
        """Find the most recent build directory."""
        build_dir = self.project_root / "data" / "stage_99_build"
        if not build_dir.exists():
            return None

        build_dirs = [d for d in build_dir.iterdir() if d.is_dir() and d.name.startswith("build_")]
        if not build_dirs:
            return None

        # Sort by creation time, get most recent
        return max(build_dirs, key=lambda x: x.stat().st_mtime)

    def collect_release_artifacts(self, build_path: Path) -> Dict[str, List[Path]]:
        """Collect all artifacts for a release from build directory."""
        artifacts = {
            "reports": [],
            "manifests": [],
            "quality_reports": [],
            "llm_responses": [],
            "semantic_results": [],
            "configs": [],
        }

        # Collect build manifests
        for manifest_file in build_path.glob("BUILD_MANIFEST.*"):
            artifacts["manifests"].append(manifest_file)

        # Collect quality reports
        quality_dir = self.project_root / "data" / "quality_reports"
        if quality_dir.exists():
            build_timestamp = build_path.name.replace("build_", "")
            quality_build_dir = quality_dir / build_timestamp
            if quality_build_dir.exists():
                artifacts["quality_reports"].extend(quality_build_dir.rglob("*"))

        # Collect LLM responses
        responses_dir = self.project_root / "data" / "llm" / "responses"
        if responses_dir.exists():
            artifacts["llm_responses"].extend(responses_dir.glob("*.md"))

        # Collect semantic results
        semantic_dir = self.project_root / "data" / "llm" / "semantic_results"
        if semantic_dir.exists():
            artifacts["semantic_results"].extend(semantic_dir.glob("*.json"))

        # Collect configuration files
        config_dir = self.project_root / "data" / "config"
        if config_dir.exists():
            artifacts["configs"].extend(config_dir.glob("*.yml"))

        return artifacts

    def generate_release_manifest(
        self, artifacts: Dict[str, List[Path]], release_id: str, build_path: Path
    ) -> Dict:
        """Generate comprehensive release manifest."""
        manifest = {
            "release_info": {
                "release_id": release_id,
                "timestamp": datetime.now().isoformat(),
                "source_build": str(build_path),
                "my_finance_version": self.get_git_commit_hash(),
                "created_by": "my_finance Release Manager",
            },
            "artifacts": {},
            "statistics": {},
            "validation": {"checksum": {}, "file_counts": {}},
        }

        # Process each artifact category
        for category, files in artifacts.items():
            manifest["artifacts"][category] = []
            total_size = 0

            for file_path in files:
                if file_path.is_file():
                    file_info = {
                        "name": file_path.name,
                        "path": str(file_path.relative_to(self.project_root)),
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    }
                    manifest["artifacts"][category].append(file_info)
                    total_size += file_info["size"]

            manifest["statistics"][category] = {
                "count": len(manifest["artifacts"][category]),
                "total_size": total_size,
            }
            manifest["validation"]["file_counts"][category] = len(manifest["artifacts"][category])

        # Overall statistics
        manifest["statistics"]["total_files"] = sum(len(files) for files in artifacts.values())
        manifest["statistics"]["total_size"] = sum(
            stat["total_size"] for stat in manifest["statistics"].values() if isinstance(stat, dict)
        )

        return manifest

    def get_git_commit_hash(self) -> str:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=self.project_root, capture_output=True, text=True
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

    def create_release_package(
        self, artifacts: Dict[str, List[Path]], manifest: Dict, release_id: str
    ) -> Path:
        """Create compressed release package."""
        temp_dir = Path(tempfile.mkdtemp())
        release_dir = temp_dir / f"release_{release_id}"
        release_dir.mkdir()

        # Copy artifacts by category
        for category, files in artifacts.items():
            if files:
                category_dir = release_dir / category
                category_dir.mkdir()

                for file_path in files:
                    if file_path.is_file():
                        shutil.copy2(file_path, category_dir / file_path.name)

        # Save manifest
        manifest_path = release_dir / "RELEASE_MANIFEST.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        # Create README for release
        readme_path = release_dir / "README.md"
        self.create_release_readme(readme_path, manifest)

        # Create compressed archive
        archive_path = temp_dir / f"release_{release_id}.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(release_dir, arcname=f"release_{release_id}")

        return archive_path

    def create_release_readme(self, readme_path: Path, manifest: Dict):
        """Create README file for the release."""
        content = f"""# My Finance Release {manifest['release_info']['release_id']}

Generated on: {manifest['release_info']['timestamp']}
Source Build: {manifest['release_info']['source_build']}
My Finance Version: {manifest['release_info']['my_finance_version']}

## Release Contents

"""

        for category, stats in manifest["statistics"].items():
            if isinstance(stats, dict) and stats.get("count", 0) > 0:
                content += f"### {category.title()}\n"
                content += f"- Files: {stats['count']}\n"
                content += f"- Total Size: {stats['total_size']:,} bytes\n\n"

        content += f"""

## Validation

- Total Files: {manifest['statistics']['total_files']}
- Total Size: {manifest['statistics']['total_size']:,} bytes

## Usage

This release contains build artifacts from the my_finance project including:
- DCF analysis reports and LLM responses
- Quality assessment reports
- Semantic retrieval results
- Configuration snapshots

For detailed artifact information, see RELEASE_MANIFEST.json
"""

        with open(readme_path, "w") as f:
            f.write(content)

    def create_release(
        self, release_name: Optional[str] = None, build_path: Optional[Path] = None
    ) -> Tuple[str, Dict]:
        """Create a complete release without external repository integration."""
        # Determine build path
        if build_path is None:
            build_path = self.get_latest_build()
            if build_path is None:
                raise ValueError("No build directory found")

        # Generate release ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        build_id = build_path.name.replace("build_", "")
        release_id = release_name or f"{timestamp}_build_{build_id}"

        print(f"🚀 Creating release: {release_id}")
        print(f"📁 Source build: {build_path}")

        # Collect artifacts
        print("📦 Collecting release artifacts...")
        artifacts = self.collect_release_artifacts(build_path)

        # Generate manifest
        print("📋 Generating release manifest...")
        manifest = self.generate_release_manifest(artifacts, release_id, build_path)

        # Create local release directory
        release_dir = self.project_root / "releases" / f"release_{release_id}"
        release_dir.mkdir(parents=True, exist_ok=True)

        print(f"📤 Creating local release in: {release_dir}")

        # Copy artifacts by category
        for category, files in artifacts.items():
            if files:
                category_dir = release_dir / category
                category_dir.mkdir(exist_ok=True)

                for file_path in files:
                    if file_path.is_file():
                        shutil.copy2(file_path, category_dir / file_path.name)

        # Save manifest
        manifest_path = release_dir / "RELEASE_MANIFEST.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        # Create README for release
        readme_path = release_dir / "README.md"
        self.create_release_readme(readme_path, manifest)

        print(f"✅ Release {release_id} created successfully!")
        print(f"📁 Location: {release_dir}")
        print(
            f"📊 Statistics: {manifest['statistics']['total_files']} files, {manifest['statistics']['total_size']:,} bytes"
        )

        return release_id, manifest

    def list_releases(self) -> List[str]:
        """List available releases from local releases directory."""
        releases_dir = self.project_root / "releases"
        if not releases_dir.exists():
            return []

        release_dirs = [
            d.name.replace("release_", "")
            for d in releases_dir.iterdir()
            if d.is_dir() and d.name.startswith("release_")
        ]

        return sorted(release_dirs, reverse=True)

    def validate_release(self, release_id: str) -> bool:
        """Validate a specific release in the local releases directory."""
        release_dir = self.project_root / "releases" / f"release_{release_id}"

        if not release_dir.exists():
            print(f"❌ Release directory not found: {release_dir}")
            return False

        # Check for required files
        manifest_path = release_dir / "RELEASE_MANIFEST.json"
        readme_path = release_dir / "README.md"

        if not manifest_path.exists():
            print(f"❌ Missing manifest file: {manifest_path}")
            return False

        if not readme_path.exists():
            print(f"❌ Missing README file: {readme_path}")
            return False

        try:
            # Validate manifest
            with open(manifest_path) as f:
                manifest = json.load(f)

            # Check file counts match manifest
            for category, expected_count in manifest["validation"]["file_counts"].items():
                category_dir = release_dir / category
                if category_dir.exists():
                    actual_count = len([f for f in category_dir.glob("*") if f.is_file()])
                    if actual_count != expected_count:
                        print(
                            f"❌ File count mismatch for {category}: expected {expected_count}, found {actual_count}"
                        )
                        return False
                elif expected_count > 0:
                    print(f"❌ Missing category directory: {category}")
                    return False

            print(f"✅ Release {release_id} validation passed")
            return True

        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False


def main():
    """Command line interface for release management."""
    parser = argparse.ArgumentParser(description="My Finance Release Manager")
    parser.add_argument(
        "command", choices=["create", "list", "validate"], help="Command to execute"
    )
    parser.add_argument("--name", help="Release name (for create command)")
    parser.add_argument("--build-path", help="Specific build path (for create command)")
    parser.add_argument("--release-id", help="Release ID (for validate command)")

    args = parser.parse_args()

    manager = ReleaseManager()

    try:
        if args.command == "create":
            build_path = Path(args.build_path) if args.build_path else None
            release_id, manifest = manager.create_release(args.name, build_path)
            print(f"\n🎉 Release created: {release_id}")

        elif args.command == "list":
            releases = manager.list_releases()
            if releases:
                print("\n📋 Available releases:")
                for release in releases:
                    print(f"  - {release}")
            else:
                print("\n📭 No releases found")

        elif args.command == "validate":
            if not args.release_id:
                print("❌ --release-id required for validate command")
                return 1

            is_valid = manager.validate_release(args.release_id)
            if not is_valid:
                return 1

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
