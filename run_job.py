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

    print("找到以下任务配置文件：")
    for idx, cf in enumerate(config_files, start=1):
        print(f"{idx}. {os.path.basename(cf)}")

    # 如果运行时传入参数则使用对应文件，否则默认使用第一个
    if len(sys.argv) > 1:
        chosen = sys.argv[1]
        config_file = os.path.join(config_dir, chosen)
        if not os.path.exists(config_file):
            print(f"配置文件 {chosen} 不存在。")
            sys.exit(1)
    else:
        config_file = config_files[0]

    print(f"启动任务配置文件：{os.path.basename(config_file)}")
    cmd = ["python3", os.path.join("spider", "yfinance_spider.py"), config_file]
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
