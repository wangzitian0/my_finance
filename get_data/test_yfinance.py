import yfinance as yf

# 以苹果公司 AAPL 为例
ticker = yf.Ticker("AAPL")

# 获取过去一年的历史数据，默认以天为单位
data = ticker.history(period="1y") 
print(data)

