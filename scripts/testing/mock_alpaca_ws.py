import os
import asyncio
import websockets
import json
import random
import datetime

KAFKA_BROKER = os.getenv("KAFKA_BROKER_LOCAL", "localhost:9092")

print(f"🔗 Connecting to Kafka at {KAFKA_BROKER}")

async def mock_alpaca(websocket, path):
    """Simulates Alpaca WebSocket trade data"""
    symbols = ["AAPL"]
    while True:
        trade_event = {
            "T": "t",
            "S": random.choice(symbols),
            "t": datetime.datetime.utcnow().isoformat(),
            "p": round(random.uniform(100, 300), 2),  # Random price
            "s": random.randint(1, 500)  # Random size
        }
        await websocket.send(json.dumps([trade_event]))  # Alpaca sends as a list
        await asyncio.sleep(1)  # Simulate real-time updates

# Start the WebSocket server
start_server = websockets.serve(mock_alpaca, "localhost", 8765)

print("📡 Mock Alpaca WebSocket running on ws://localhost:8765")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
