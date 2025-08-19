import yfinance as yf

# Using Apple Inc. AAPL as example
ticker = yf.Ticker("AAPL")

# Get historical data for the past year, default unit is daily
data = ticker.history(period="1y")
print(data)
