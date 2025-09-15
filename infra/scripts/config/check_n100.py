#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common.etl_loader import load_stock_list

# Load N100 stock list
stock_list = load_stock_list("n100")

print(f"N100 companies: {len(stock_list.tickers)}")
print(f"Description: {stock_list.description}")
print(f"Tickers: {stock_list.tickers}")
