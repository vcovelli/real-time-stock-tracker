-- Create raw_trades stream
CREATE STREAM raw_trades (
    symbol STRING,
    timestamp STRING,
    price DOUBLE,
    "size" BIGINT
) 
WITH (
    KAFKA_TOPIC = 'stock-data',
    VALUE_FORMAT = 'JSON'
);

-- Create the OHLC table using CTAS (symbol is the primary key automatically)
CREATE TABLE ohlc_candles WITH (
    KAFKA_TOPIC = 'ohlc-data',
    VALUE_FORMAT = 'JSON',
    PARTITIONS = 2,
    REPLICAS = 1
) AS
    SELECT
        symbol,  -- PRIMARY KEY
        WINDOWSTART AS bucket_start,
        EARLIEST_BY_OFFSET(price) AS open,
        MAX(price) AS high,
        MIN(price) AS low,
        LATEST_BY_OFFSET(price) AS close,
        SUM("size") AS volume
    FROM raw_trades
    WINDOW TUMBLING (SIZE 1 MINUTE)
    GROUP BY symbol;
