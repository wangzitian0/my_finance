# get_data/init_db.py

from get_data.common import ensure_common_tables, safe_call
from get_data.init_schema import init_db_schema
from get_data import fetch_historical, fetch_info, fetch_quarterly

def main():
    # 1) 初始化: 公共表 + 业务表
    ensure_common_tables()
    init_db_schema()

    # 2) 选定要抓的标的
    ticker_symbol = "AAPL"

    # 3) 逐个调用抓取(带 safe_call 包装，若出错自动记录失败)
    #    或者你可以不用 safe_call，自己写 try-except...
    #    这里示例先拉日线，再拉info，再拉季度财报
    safe_call(fetch_historical.fetch_historical, ticker_symbol, period="1y", interval="1d", cooldown_minutes=60)
    safe_call(fetch_info.fetch_info, ticker_symbol, cooldown_minutes=60)
    safe_call(fetch_quarterly.fetch_quarterly_balance, ticker_symbol, cooldown_minutes=60)

    # 你也可以在此循环多只股票、或多频率:
    # symbols = ["AAPL", "MSFT"]
    # for sym in symbols:
    #     safe_call(fetch_historical.fetch_historical, sym, interval="1wk")
    #     safe_call(fetch_info.fetch_info, sym)
    #     safe_call(fetch_quarterly.fetch_quarterly_balance, sym)

    print("[DONE] All tasks completed.")

if __name__ == "__main__":
    main()

