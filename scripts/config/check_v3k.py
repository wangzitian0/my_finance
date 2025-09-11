#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common.orthogonal_config import orthogonal_config

# Load V3K stock list
stock_list = orthogonal_config.load_stock_list("v3k")

print(f"V3K companies: {len(stock_list.tickers)}")
print(f"Description: {stock_list.description}")
print(f"First 10 tickers: {stock_list.tickers[:10]}")
print(f"Last 10 tickers: {stock_list.tickers[-10:]}")
