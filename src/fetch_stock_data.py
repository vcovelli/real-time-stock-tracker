import os
import json
import websocket
from kafka import KafkaProducer

# Load environment variables
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "stock-data")

# WebSocket URL for real-time stock data
STREAM_URL = "wss://stream.data.alpaca.markets/v2/iex"

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def on_message(ws, message):
    """Handle incoming WebSocket messages and send to Kafka"""
    data = json.loads(message)

    for event in data:
        if event["T"] == "t":  # Trade update
            stock_record = {
                "symbol": event["S"],  # Stock symbol
                "timestamp": event["t"],  # Event timestamp
                "price": event["p"],  # Trade price
                "size": event["s"]  # Trade size
            }

            print(f"📡 Sending to Kafka: {stock_record}")
            producer.send(KAFKA_TOPIC, stock_record)

def on_error(ws, error):
    """Handle WebSocket errors"""
    print("❌ WebSocket Error:", error)

def on_close(ws, close_status_code, close_msg):
    """Handle WebSocket disconnections"""
    print("🔄 WebSocket closed, reconnecting...")
    start_streaming()

def on_open(ws):
    """Authenticate and subscribe to Alpaca WebSocket"""
    auth_message = {
        "action": "auth",
        "key": ALPACA_API_KEY,
        "secret": ALPACA_SECRET_KEY
    }
    ws.send(json.dumps(auth_message))

    subscribe_message = {
        "action": "subscribe",
        "trades": ["AAPL", "GOOG", "TSLA"]  # Add more stocks if needed
    }
    ws.send(json.dumps(subscribe_message))

def start_streaming():
    """Start WebSocket connection"""
    ws = websocket.WebSocketApp(
        STREAM_URL,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()

if __name__ == "__main__":
    start_streaming()
