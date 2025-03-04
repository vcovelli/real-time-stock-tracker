from kafka import KafkaConsumer
import psycopg2
import redis
import json
import datetime

# Kafka Consumer Configuration
consumer = KafkaConsumer(
    'stock-data',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# PostgreSQL (TimescaleDB) Connection Configuration
pg_connection = psycopg2.connect(
    host='timescaledb', # Change to 'localhost' if running locally
    database='stock_data',
    user='stock_user',
    password='stock_password'
)
pg_connection.autocommit = True

# Redis Connection
redis_client = redis.Redis(host='redis', port 6379, db=0)

# Ensure the table exists
pg_cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_prices (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(10),
        timestamp TIMESTAMPTZ NOT NULL,
        open NUMERIC(10, 2),
        high NUMERIC(10, 2),
        low NUMERIC(10, 2),
        close NUMERIC(10, 2),
        volume BIGINT
    );
""")
pg_cursor.execute("SELECT create_hypertable('stock_prices', 'timestamp') ON CONFLICT DO NOTHING;")

# Function to insert stock data into TimescaleDB and cache latest price in Redis
def insert_into_timescaledb(record):
    try:
        pg_cursor.execute("""
            INSERT INTO stock_prices (symbol, timestamp, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            record['symbol'],
            record['timestamp'],
            record['open'],
            record['high'],
            record['low'],
            record['close'],
            record['volume']
        ))

        # Cache the latest stock price in Redis (symbol: latest price)
        redis_client.set(record['symbol'], json.dumps(record))

        print(f"Inserted into TimescaleDB & Cached in Redis: {record}")
    except Exception as e:
        print(f"Error inserting into TimescaleDB: {e}")

# Start consuming Kafka messages
print("Starting Kafka consumer...")
for message in consumer:
    record = message.value
    print("Received data:", record)  # Inspect the incoming data
    insert_into_timescaledb(record)

# Cleanup
pg_cursor.close()
pg_connection.close()

