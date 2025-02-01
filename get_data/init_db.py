from common import ensure_common_tables
from fetch_historical import fetch_historical

def main():
    ensure_common_tables()
    # 在此添加其他初始化逻辑，例如拉取特定股票的数据
    result = fetch_historical("AAPL")
    print(result)

if __name__ == "__main__":
    main()

