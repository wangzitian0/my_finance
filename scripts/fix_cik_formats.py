#!/usr/bin/env python3
"""
Script to fix CIK format issues in configuration files.
Ensures all CIK values are strings with proper padding.
"""

from pathlib import Path

import yaml


def fix_cik_formats():
    """Fix CIK format issues in all configuration files"""
    config_files = [
        "list_magnificent_7.yml",
        "list_nasdaq_100.yml",
        "list_vti_3500.yml",
    ]

    config_dir = Path(__file__).parent.parent / "data" / "config"

    for config_file in config_files:
        config_path = config_dir / config_file
        print(f"📋 Processing: {config_file}")

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        changes = 0
        if "companies" in config:
            for ticker, company_data in config["companies"].items():
                if "cik" in company_data and company_data["cik"] is not None:
                    original_cik = company_data["cik"]

                    # Convert to string and pad with zeros
                    if isinstance(original_cik, int):
                        cik_str = str(original_cik).zfill(10)
                        company_data["cik"] = cik_str
                        changes += 1
                        print(f"  Fixed {ticker}: {original_cik} -> {cik_str}")
                    elif isinstance(original_cik, str) and len(original_cik) < 10:
                        cik_str = original_cik.zfill(10)
                        company_data["cik"] = cik_str
                        changes += 1
                        print(f"  Padded {ticker}: {original_cik} -> {cik_str}")

        if changes > 0:
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(
                    config, f, default_flow_style=False, sort_keys=False, allow_unicode=True
                )
            print(f"  ✅ Saved {changes} changes")
        else:
            print(f"  ✅ No changes needed")


if __name__ == "__main__":
    fix_cik_formats()
