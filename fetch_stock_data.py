import yfinance as yf
from kafka import KafkaProducer
import json
import time

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_stock_data(ticker):
    data = ticker.history(period="1d", interval="1m")  # Get minute-by-minute data for today
    if not data.empty:
        latest_data = data.tail(1).to_dict(orient="records")[0]  # Get only the latest data point
        print(latest_data)  # Print the data to verify it’s working
        producer.send('stock-data', latest_data)  # Send data to Kafka
    else:
        print(f"No data found for {ticker}. Retrying...")

if __name__ == "__main__":
    ticker_symbol = "AAPL"  # Replace with any valid stock symbol
    ticker = yf.Ticker(ticker_symbol)

    # Fetch stock data every minute
    while True:
        fetch_stock_data(ticker)
        time.sleep(60)  # Wait for 1 minute

    # Close the producer when done
    producer.close()

