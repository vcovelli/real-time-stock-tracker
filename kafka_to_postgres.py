from kafka import KafkaConsumer
import psycopg2
import json
import datetime

# Kafka Consumer Configuration
consumer = KafkaConsumer(
    'stock-data',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# PostgreSQL connection configuration
pg_connection = psycopg2.connect(
    host='localhost',
    database='stock_data',
    user='stock_user',
    password='stock_password'
)
pg_connection.autocommit = True

# Function to insert stock data into PostgreSQL
def insert_into_postgres(record):
    cursor = pg_connection.cursor()
    try:
        # Convert 'timestamp' to a datetime object if it's a string
        if isinstance(record['timestamp'], str):
            record['timestamp'] = datetime.datetime.fromisoformat(record['timestamp'])
        
        # Insert the record into PostgreSQL
        cursor.execute("""
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
        print(f"Inserted data: {record}")
    except Exception as e:
        print(f"Failed to insert data: {e}")
    finally:
        cursor.close()

# Main loop to consume messages from Kafka and insert them into PostgreSQL
print("Starting Kafka consumer...")
for message in consumer:
    record = message.value
    print("Received data:", record)  # Inspect the incoming data
    insert_into_postgres(record)

# Close the PostgreSQL connection when done
pg_connection.close()

