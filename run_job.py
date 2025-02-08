#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import glob
import subprocess


def main():
    # Locate configuration files in data/config/
    config_dir = os.path.join(os.getcwd(), "data", "config")
    config_files = glob.glob(os.path.join(config_dir, "*.yml"))
    if not config_files:
        print("No configuration files found. Please create a config file in data/config/")
        sys.exit(1)

    print("Found configuration files:")
    for idx, f in enumerate(config_files, start=1):
        print(f"{idx}. {os.path.basename(f)}")

    # Use the provided configuration filename (if any) or default to the first.
    if len(sys.argv) > 1:
        chosen = sys.argv[1]
        config_file = os.path.join(config_dir, chosen)
        if not os.path.exists(config_file):
            print(f"Config file {chosen} does not exist.")
            sys.exit(1)
    else:
        config_file = config_files[0]

    print(f"Starting job with config: {os.path.basename(config_file)}")
    print("Data will be saved under: data/original/<source>/<ticker>/")
    print("Logs will be stored under: data/log/<job_id>/<date_str>.txt")

    # Call the spider script with the chosen configuration file.
    cmd = ["python3", os.path.join("spider", "yfinance_spider.py"), config_file]
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
