#!/bin/sh
echo "Waiting for Kafka..."
sleep 10

echo "Creating topics..."
docker exec -it kafka kafka-topics.sh --bootstrap-server kafka:9092 --create --if-not-exists --topic ohlc-data --partitions 2 --replication-factor 1 --config retention.ms=604800000
docker exec -it kafka kafka-topics.sh --bootstrap-server kafka:9092 --create --if-not-exists --topic stock-data --partitions 2 --replication-factor 1 --config retention.ms=604800000
echo "Kafka topics created."
