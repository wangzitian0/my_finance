import yfinance as yf

# Using Apple Inc. AAPL as example
ticker = yf.Ticker("AAPL")

# Get historical data for past year, default daily
data = ticker.history(period="1y")
print(data)
