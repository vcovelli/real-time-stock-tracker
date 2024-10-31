import yfinance as yf
import json
import datetime
from kafka import KafkaProducer
import time

# Kafka Producer configuration
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_stock_data(ticker):
    data = yf.Ticker(ticker).history(period="1d", interval="1m")  # Get minute-by-minute data for today
    if not data.empty:
        latest_data = data.iloc[-1]
        record = {
            "symbol": ticker,
            "timestamp": datetime.datetime.now().isoformat(),
            "open": latest_data["Open"],
            "high": latest_data["High"],
            "low": latest_data["Low"],
            "close": latest_data["Close"],
            "volume": latest_data["Volume"]
        }
        print(record)  # Print for debugging
        producer.send('stock-data', value=record)
    else:
        print(f"No data found for {ticker}. Retrying...")

ticker_symbol = "AAPL"  # Replace with any valid stock symbol

# Fetch stock data every minute
while True:
    fetch_stock_data(ticker_symbol)
    time.sleep(60)  # Wait for 1 minute

