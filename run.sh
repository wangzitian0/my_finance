#!/usr/bin/env bash

# 使脚本在出现错误时退出
set -e

# 进入脚本所在目录（以防万一）
cd "$(dirname "$0")"

echo "[INFO] Activating Python (pipenv/venv) if needed, or rely on system Python..."
# 如果你使用 pipenv:
# pipenv shell
# 如果你使用 venv:
# source venv/bin/activate
# 或者如果直接全局 python, 可以不需要以上步骤

echo "[INFO] Running init_db.py to fetch data..."
python get_data/init_db.py

echo "[INFO] Done. Check data/yfinance_data.db for results."

