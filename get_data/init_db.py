# get_data/init_db.py

from get_data.common import ensure_fetch_log_table
from get_data.init_schema import init_db_schema
from get_data import fetch_historical, fetch_info, fetch_quarterly

def main():
    # 1) 初始化所有数据库表 (fetch_log、stock_price、stock_info等)
    ensure_fetch_log_table()
    init_db_schema()

    # 2) 定义要抓取的标的
    # 例如只抓 AAPL, 你可以改为 ["AAPL", "MSFT", "GOOGL"] 做批量
    ticker_symbol = "AAPL"

    # 3) 调用各模块抓取（会自动检查1小时内是否拉过）
    #    你可以视情况组合顺序或频率
    fetch_info.run(ticker_symbol)
    fetch_historical.run(ticker_symbol, period="1y")
    fetch_quarterly.run_quarterly_balance(ticker_symbol)
    # 其他季度财表等:
    # fetch_quarterly.run_quarterly_cashflow(ticker_symbol)
    # fetch_quarterly.run_quarterly_financials(ticker_symbol)
    # fetch_quarterly.run_quarterly_earnings(ticker_symbol)

    print("[DONE] All tasks completed.")

if __name__ == "__main__":
    main()

