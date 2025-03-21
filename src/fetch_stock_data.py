import os
import json
import websocket
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

# Load environment variables
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092") # Default to localhost

# Dynamically select topic
KAFKA_TOPIC_TRADES = os.getenv("KAFKA_TOPIC_TRADES", "stock-data")

# Toggle between Alpaca and Mock WebSocket
USE_MOCK = True  # Set to False to switch back to Alpaca

# WebSocket URL
if USE_MOCK:
    STREAM_URL = "ws://host.docker.internal:8765"  # Mock server
else:
    STREAM_URL = "wss://stream.data.alpaca.markets/v2/iex"  # Real Alpaca WebSocket

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
                "symbol": event["S"],
                "timestamp": event["t"],
                "price": event["p"],
                "size": event["s"]
            }

            print(f"📡 Sending to Kafka: {stock_record}")
            producer.send(KAFKA_TOPIC_TRADES, stock_record)

def on_error(ws, error):
    """Handle WebSocket errors"""
    print("❌ WebSocket Error:", error)

def on_close(ws, close_status_code, close_msg):
    """Handle WebSocket disconnections"""
    print("🔄 WebSocket closed, reconnecting...")
    start_streaming()

def on_open(ws):
    """Authenticate and subscribe (only needed for Alpaca)"""
    if not USE_MOCK:
        auth_message = {
            "action": "auth",
            "key": os.getenv("ALPACA_API_KEY"),
            "secret": os.getenv("ALPACA_SECRET_KEY")
        }
        ws.send(json.dumps(auth_message))

        subscribe_message = {
            "action": "subscribe",
            "trades": ["AAPL"]
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
