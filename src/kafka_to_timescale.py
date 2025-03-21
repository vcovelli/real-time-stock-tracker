import os
from dotenv import load_dotenv
import json
import time
import psycopg2
import redis
from kafka import KafkaConsumer
import datetime

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
KAFKA_BROKER_DOCKER = os.getenv("KAFKA_BROKER_DOCKER")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
KAFKA_TOPIC_OHLC = os.getenv("KAFKA_TOPIC_OHLC", "ohlc-data")

# Redis Connection
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def insert_into_timescaledb(record):
    try:
        record = {k.lower(): v for k, v in record.items()}
        required_fields = {'symbol_value', 'bucket_start', 'open', 'high', 'low', 'close', 'volume'}
        if not required_fields.issubset(record):
            return

        timestamp_seconds = datetime.datetime.utcfromtimestamp(record['bucket_start'] / 1000)

        sql_query = """
            INSERT INTO stock_prices (symbol, "timestamp", open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, "timestamp") 
            DO UPDATE 
            SET open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low, close = EXCLUDED.close, volume = EXCLUDED.volume;
        """
        sql_params = (
            record['symbol_value'],
            timestamp_seconds,
            float(record['open']),
            float(record['high']),
            float(record['low']),
            float(record['close']),
            int(record['volume'])
        )

        with psycopg2.connect(
            host=POSTGRES_HOST,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_query, sql_params)
                conn.commit()

        redis_key = f"stock_price:{record['symbol_value']}"
        redis_value = json.dumps({
            "timestamp": timestamp_seconds.isoformat(),
            "open": record['open'],
            "high": record['high'],
            "low": record['low'],
            "close": record['close'],
            "volume": record['volume']
        })
        redis_client.set(redis_key, redis_value)

        print(f"✅ {record['symbol_value']} @ {timestamp_seconds}: stored & cached")

    except psycopg2.Error as db_error:
        print(f"❌ DB error: {db_error}")
    except Exception as e:
        print(f"❌ Error: {e}")

def start_kafka_consumer():
    while True:
        try:
            print("🔄 Kafka consumer started...")

            consumer = KafkaConsumer(
                KAFKA_TOPIC_OHLC,
                bootstrap_servers=KAFKA_BROKER_DOCKER,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )

            for message in consumer:
                insert_into_timescaledb(message.value)

        except Exception as e:
            print(f"⚠️ Kafka error: {e}, retrying in 5s...")
            time.sleep(5)
        finally:
            consumer.close()

if __name__ == "__main__":
    start_kafka_consumer()
