#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import subprocess
import sys


def main():
    config_dir = os.path.join(os.getcwd(), "data", "config")
    config_files = glob.glob(os.path.join(config_dir, "*.yml"))
    if not config_files:
        print("Configuration file not found. Please create task configuration files in data/config/ directory first.")
        sys.exit(1)

    print("Found configuration files:")
    for idx, cf in enumerate(config_files, start=1):
        print(f"{idx}. {os.path.basename(cf)}")

    # Select configuration file based on command line arguments, otherwise default to the first one
    if len(sys.argv) > 1:
        chosen = sys.argv[1]
        config_file = os.path.join(config_dir, chosen)
        if not os.path.exists(config_file):
            print(f"Configuration file {chosen} does not exist.")
            sys.exit(1)
    else:
        config_file = config_files[0]

    config_basename = os.path.basename(config_file).lower()

    # Decide which spider script to call based on configuration file prefix
    if config_basename.startswith("sec_edgar"):
        spider_file = os.path.join("spider", "sec_edgar_spider.py")
    elif config_basename.startswith("yfinance_nasdaq"):
        spider_file = os.path.join("spider", "yfinance_spider.py")
    else:
        spider_file = os.path.join("spider", "yfinance_spider.py")

    print(f"Starting job with config: {os.path.basename(config_file)}")
    print(f"Executing spider: {spider_file}")
    print("Data will be saved under: data/stage_00_original/<source>/<ticker>/")
    print("Logs will be stored under: data/log/<job_id>/<date_str>.txt")

    cmd = ["python3", spider_file, config_file]
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
