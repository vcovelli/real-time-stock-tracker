import os
import json
import time
from kafka import KafkaProducer
import random

# Load environment variables
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC_OHLC = os.getenv("KAFKA_TOPIC_OHLC", "ohlc-data")

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Function to generate random OHLC data for multiple stocks
def generate_ohlc_data():
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
    
    while True:
        for symbol in symbols:
            ohlc_data = {
                "symbol": symbol,
                "BUCKET_START": int(time.time() * 1000),  # Timestamp in ms
                "OPEN": round(random.uniform(100, 300), 2),
                "HIGH": round(random.uniform(250, 350), 2),
                "LOW": round(random.uniform(100, 200), 2),
                "CLOSE": round(random.uniform(120, 330), 2),
                "VOLUME": random.randint(1000, 50000)
            }

            print(f"📡 Sending OHLC Data: {ohlc_data}")
            producer.send(KAFKA_TOPIC_OHLC, ohlc_data)
        
        time.sleep(5)  # Generate data every 5 seconds

if __name__ == "__main__":
    generate_ohlc_data()
