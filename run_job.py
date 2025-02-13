#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import glob
import subprocess


def main():
    config_dir = os.path.join(os.getcwd(), "data", "config")
    config_files = glob.glob(os.path.join(config_dir, "*.yml"))
    if not config_files:
        print("未找到配置文件，请先在 data/config/ 目录下创建任务配置文件。")
        sys.exit(1)

    print("Found configuration files:")
    for idx, cf in enumerate(config_files, start=1):
        print(f"{idx}. {os.path.basename(cf)}")

    # 根据命令行参数选择配置文件，否则默认选择第一个
    if len(sys.argv) > 1:
        chosen = sys.argv[1]
        config_file = os.path.join(config_dir, chosen)
        if not os.path.exists(config_file):
            print(f"配置文件 {chosen} 不存在。")
            sys.exit(1)
    else:
        config_file = config_files[0]

    config_basename = os.path.basename(config_file).lower()

    # 根据配置文件前缀决定调用哪个 spider 脚本
    if config_basename.startswith("sec_edgar"):
        spider_file = os.path.join("spider", "sec_edgar_spider.py")
    elif config_basename.startswith("yfinance_nasdaq"):
        spider_file = os.path.join("spider", "yfinance_spider.py")
    else:
        spider_file = os.path.join("spider", "yfinance_spider.py")

    print(f"Starting job with config: {os.path.basename(config_file)}")
    print(f"Executing spider: {spider_file}")
    print("Data will be saved under: data/original/<source>/<ticker>/")
    print("Logs will be stored under: data/log/<job_id>/<date_str>.txt")

    cmd = ["python3", spider_file, config_file]
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
