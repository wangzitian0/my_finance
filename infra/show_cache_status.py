#!/usr/bin/env python3
"""
Display comprehensive caching status for Podman and dependencies
Shows what's cached vs what needs downloading
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List

def run_cmd(cmd: str) -> tuple[bool, str]:
    """Run command and return success + output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)

def check_podman_caches() -> Dict:
    """Check Podman's native caching status"""
    cache_info = {
        "installation": "❓ Unknown",
        "machine_cache": "❓ Unknown", 
        "image_cache": "❓ Unknown",
        "storage_size": "❓ Unknown",
        "details": []
    }
    
    # Check installation
    success, version = run_cmd("podman version --format '{{.Client.Version}}' 2>/dev/null")
    binary_success, binary_path = run_cmd("which podman")
    
    if binary_success:
        if success:
            cache_info["installation"] = f"✅ Installed (v{version})"
        else:
            # Binary exists but version fails (probably no machine)
            cache_info["installation"] = "⚠️ Installed but needs machine setup"
        cache_info["details"].append(f"Binary: {binary_path}")
    else:
        cache_info["installation"] = "❌ Not installed"
        return cache_info
    
    # Check machine cache
    home = Path.home()
    machine_dir = home / ".local/share/containers/podman/machine"
    if machine_dir.exists():
        machines = list(machine_dir.iterdir())
        if machines:
            cache_info["machine_cache"] = f"✅ {len(machines)} machine(s) cached"
            for machine in machines:
                if machine.is_dir():
                    cache_info["details"].append(f"Machine: {machine.name}")
        else:
            cache_info["machine_cache"] = "📁 Cache dir exists, no machines"
    else:
        cache_info["machine_cache"] = "❌ No machine cache"
    
    # Check image storage
    storage_dir = home / ".local/share/containers/storage"
    if storage_dir.exists():
        success, size_output = run_cmd(f"du -sh {storage_dir} 2>/dev/null || echo '0B'")
        cache_info["storage_size"] = size_output.split()[0] if success else "Unknown"
        
        # Try to get image count
        success, images = run_cmd("podman images --format json 2>/dev/null")
        if success and images:
            try:
                image_list = json.loads(images)
                cache_info["image_cache"] = f"✅ {len(image_list)} images cached"
                for img in image_list[:3]:  # Show first 3
                    names = img.get('Names', ['<none>'])
                    name = names[0] if names else '<none>'
                    cache_info["details"].append(f"Image: {name}")
                if len(image_list) > 3:
                    cache_info["details"].append(f"... and {len(image_list) - 3} more")
            except json.JSONDecodeError:
                cache_info["image_cache"] = "⚠️ Can't parse image list"
        else:
            cache_info["image_cache"] = "📁 Storage exists, no accessible images"
    else:
        cache_info["image_cache"] = "❌ No image storage"
    
    return cache_info

def check_brew_cache() -> Dict:
    """Check Homebrew caching for Podman"""
    cache_info = {
        "podman_cached": "❓ Unknown",
        "cache_size": "❓ Unknown",
        "details": []
    }
    
    # Check if podman is installed via brew
    success, _ = run_cmd("brew list podman >/dev/null 2>&1")
    if success:
        cache_info["podman_cached"] = "✅ Cached in Homebrew"
        
        # Get cache size
        success, cellar_info = run_cmd("brew --cellar podman")
        if success:
            cellar_path = Path(cellar_info.strip())
            if cellar_path.exists():
                success, size = run_cmd(f"du -sh {cellar_path}")
                cache_info["cache_size"] = size.split()[0] if success else "Unknown"
                cache_info["details"].append(f"Location: {cellar_path}")
    else:
        cache_info["podman_cached"] = "❌ Not installed via Homebrew"
    
    return cache_info

def check_custom_caches() -> Dict:
    """Check our custom cache markers"""
    cache_info = {
        "setup_marker": "❓ Unknown",
        "env_marker": "❓ Unknown",
        "details": []
    }
    
    cache_dir = Path.home() / ".cache/my-finance"
    
    if cache_dir.exists():
        cache_info["details"].append(f"Cache dir: {cache_dir}")
        
        # Check setup markers
        setup_marker = cache_dir / "podman-machine-ready"
        env_marker = cache_dir / "environment-ready"
        
        cache_info["setup_marker"] = "✅ Present" if setup_marker.exists() else "❌ Missing"
        cache_info["env_marker"] = "✅ Present" if env_marker.exists() else "❌ Missing"
        
        # List all cached files
        cached_files = list(cache_dir.glob("*"))
        if cached_files:
            cache_info["details"].append(f"Cached files: {len(cached_files)}")
            for f in cached_files:
                cache_info["details"].append(f"  - {f.name}")
    else:
        cache_info["setup_marker"] = "❌ No cache dir"
        cache_info["env_marker"] = "❌ No cache dir"
    
    return cache_info

def main():
    """Main function"""
    print("🗄️  Comprehensive Caching Status Report")
    print("=" * 60)
    
    # Podman native caches
    print("\n📦 Podman Native Caching:")
    podman_cache = check_podman_caches()
    print(f"   Installation: {podman_cache['installation']}")
    print(f"   Machine Cache: {podman_cache['machine_cache']}")
    print(f"   Image Cache: {podman_cache['image_cache']}")
    print(f"   Storage Size: {podman_cache['storage_size']}")
    
    # Homebrew caches
    print("\n🍺 Homebrew Caching:")
    brew_cache = check_brew_cache()
    print(f"   Podman Package: {brew_cache['podman_cached']}")
    print(f"   Package Size: {brew_cache['cache_size']}")
    
    # Custom caches
    print("\n🔧 Project Caching:")
    custom_cache = check_custom_caches()
    print(f"   Setup Marker: {custom_cache['setup_marker']}")
    print(f"   Environment Marker: {custom_cache['env_marker']}")
    
    # Detailed info
    print("\n📋 Details:")
    all_details = (
        podman_cache['details'] + 
        brew_cache['details'] + 
        custom_cache['details']
    )
    
    for detail in all_details:
        print(f"   {detail}")
    
    print(f"\n💡 Cache Summary:")
    print(f"   - Podman itself: {'✅ Cached via Homebrew' if brew_cache['podman_cached'].startswith('✅') else '❌ Not cached'}")
    print(f"   - Container images: {'✅ ' + podman_cache['storage_size'] if podman_cache['storage_size'] != '❓ Unknown' else '❌ No storage'}")
    print(f"   - Machine setup: {'✅ Ready' if custom_cache['env_marker'].startswith('✅') else '❌ Needs setup'}")

if __name__ == "__main__":
    main()
