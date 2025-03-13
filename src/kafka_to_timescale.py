import os
from kafka import KafkaConsumer
import psycopg2
import redis
import json
import datetime

# Load environment variables
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")  # Default to localhost if not set
POSTGRES_DB = os.getenv("POSTGRES_DB", "stock_data")
POSTGRES_USER = os.getenv("POSTGRES_USER", "stock_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "stock_password")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Kafka Consumer Configuration
consumer = KafkaConsumer(
    'stock-data',
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# PostgreSQL (TimescaleDB) Connection Configuration
pg_connection = psycopg2.connect(
    host=POSTGRES_HOST,
    database=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD
)
pg_connection.autocommit = True

# Redis Connection
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

pg_cursor = pg_connection.cursor()

# Create table (if not exists)
pg_cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_prices (
        symbol VARCHAR(10),
        timestamp TIMESTAMPTZ NOT NULL,
        open NUMERIC(10, 2),
        high NUMERIC(10, 2),
        low NUMERIC(10, 2),
        close NUMERIC(10, 2),
        volume BIGINT,
        PRIMARY KEY (symbol, timestamp)
    );
""")

# Check if stock_prices is already a hypertable
pg_cursor.execute("""
    SELECT COUNT(*) FROM timescaledb_information.hypertables WHERE hypertable_name = 'stock_prices';
""")
is_hypertable = pg_cursor.fetchone()[0]

# Create hypertable ONLY if it does not exist
if is_hypertable == 0:
    print("Creating TimescaleDB hypertable...")
    pg_cursor.execute("SELECT create_hypertable('stock_prices', 'timestamp');")
else:
    print("✅ TimescaleDB hypertable already exists, skipping creation.")


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

