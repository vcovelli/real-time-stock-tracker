import asyncio
import websockets
import json
import random
import datetime

async def stock_data(websocket, path):
    while True:
        data = {
            "symbol": "AAPL",
            "timestamp": str(datetime.datetime.utcnow()),
            "open": round(random.uniform(140, 150), 2),
            "high": round(random.uniform(150, 155), 2),
            "low": round(random.uniform(138, 145), 2),
            "close": round(random.uniform(140, 150), 2),
            "volume": random.randint(500, 2000)
        }
        await websocket.send(json.dumps(data))
        await asyncio.sleep(1)  # Simulate 1-second market updates

start_server = websockets.serve(stock_data, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
