#!/usr/bin/env python3
"""
请先安装 lxml 库：
    pip install lxml

以下是7姐妹（7大科技公司）的 CIK 号码：
  - Apple (AAPL):       0000320193
  - Microsoft (MSFT):   0000789019
  - Amazon (AMZN):      0001018724
  - Alphabet (GOOGL):   0001652044
  - Facebook (FB, Meta):0001326801
  - Tesla (TSLA):       0001318605
  - Netflix (NFLX):     0001065280

建议在配置文件中直接使用上述 CIK 号码替代股票代码（ticker），
这样程序将直接使用 CIK 查询 filings 数据，避免内部转换时请求 /files/company_tickers.json 导致的错误。
"""

import warnings

from bs4 import XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

import json
import logging
import os
import time
from datetime import datetime, timedelta

import yaml
from secedgar import FilingType, filings
from tqdm import tqdm
from common.metadata_manager import MetadataManager

# 设置日志输出级别为 DEBUG
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# 定义保存数据的基础目录：data/original/sec-edgar/
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORIGINAL_DATA_DIR = os.path.join(BASE_DIR, "data", "original", "sec-edgar")
if not os.path.exists(ORIGINAL_DATA_DIR):
    os.makedirs(ORIGINAL_DATA_DIR)


def is_file_recent(filepath, hours=1):
    """
    检查文件是否在过去指定的小时内被修改
    参数：
      filepath: 文件路径
      hours: 小时数
    """
    if os.path.exists(filepath):
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        return datetime.now() - mtime < timedelta(hours=hours)
    return False


def run_job(config_path):
    """
    主任务：从 YAML 配置文件加载配置，并依次处理每个 CIK 与 filing 类型，
    直接调用 secedgar.filings 对象的 save() 方法保存 filings 数据。
    数据将保存在：data/original/sec-edgar/<CIK>/<filing_type>/ 目录下。
    参数：
      config_path: 配置文件路径
    """
    logging.info(f"加载配置文件: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 直接使用 CIK 号码（例如 "0000320193"）
    cik_list = config.get("tickers", [])
    count = config.get("count", 8)
    file_types = config.get("file_types", ["10K", "10Q", "13F", "8K"])
    email = config.get("email", "ZitianSG (wangzitian0@gmail.com)")

    # Initialize metadata manager
    metadata_manager = MetadataManager(ORIGINAL_DATA_DIR)
    
    total_tasks = len(cik_list) * len(file_types)
    logging.info(f"开始处理任务, 总计 {total_tasks} 个任务")
    pbar = tqdm(total=total_tasks, desc="Tickers Progress", unit="task")

    filing_type_map = {
        "10K": FilingType.FILING_10K,
        "10Q": FilingType.FILING_10Q,
        "13F": FilingType.FILING_13F,
        "8K": FilingType.FILING_8K,
    }

    for cik in cik_list:
        logging.info(f"直接使用 CIK 查询: {cik}")
        cik_dir = os.path.join(ORIGINAL_DATA_DIR, cik)
        if not os.path.exists(cik_dir):
            os.makedirs(cik_dir)
        for ft in file_types:
            logging.info(f"开始处理 {cik} 的 {ft} filings")
            filing_type_enum = filing_type_map.get(ft)
            if filing_type_enum is None:
                logging.error(f"不支持的 filing 类型: {ft}，CIK: {cik}")
                pbar.update(1)
                continue

            # Create config info for this request
            config_info = {
                "filing_type": ft,
                "count": count,
                "email": email
            }
            
            # Check if recent data exists using metadata manager (check for 7 days for SEC filings)
            if metadata_manager.check_file_exists_recent("sec-edgar", cik, ft.lower(), config_info, hours=168):  # 7 days
                logging.info(f"CIK {cik} {ft} filings: Recent data exists (skipped).")
            else:
                output_dir = os.path.join(cik_dir, ft.lower())
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

            try:
                filings_obj = filings(cik_lookup=cik,
                                      filing_type=filing_type_enum,
                                      count=count,
                                      user_agent=email)
                # 直接设置 cik_lookup 内部映射，避免调用 /files/company_tickers.json
                filings_obj.cik_lookup._lookup_dict = {cik: cik}
                filings_obj.save(output_dir)
                logging.info(f"成功保存 {cik} {ft} filings 至 {output_dir}")
                
                # Update metadata for all downloaded files
                if os.path.exists(output_dir):
                    for filename in os.listdir(output_dir):
                        filepath = os.path.join(output_dir, filename)
                        if os.path.isfile(filepath):
                            metadata_manager.add_file_record("sec-edgar", cik, filepath, ft.lower(), config_info)
                    metadata_manager.generate_markdown_index("sec-edgar", cik)
                    
            except Exception as e:
                error_msg = str(e)
                metadata_manager.mark_download_failed("sec-edgar", cik, ft.lower(), config_info, error_msg)
                logging.exception(f"处理 {cik} {ft} filings 时出错: {e}")
                logging.info("请检查 /files/company_tickers.json 的访问权限，若仍有问题请手动下载该文件。")
            pbar.update(1)
            time.sleep(3)

    pbar.close()
    logging.info("所有任务处理完成")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        logging.error("Usage: python run_job.py <config_file_path>")
        sys.exit(1)
    config_file = sys.argv[1]
    if not os.path.exists(config_file):
        logging.error(f"配置文件 {config_file} 不存在。")
        sys.exit(1)
    run_job(config_file)
