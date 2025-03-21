#!/bin/bash

cat <<EOF > deployments/stock-tracker-env.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: stock-tracker-env
data:
  POSTGRES_HOST: "timescaledb"
  POSTGRES_DB: "stock_data"
  POSTGRES_USER: "stock_user"
  POSTGRES_PASSWORD: "*****************"
  KAFKA_BROKER: "kafka:####"
  REDIS_HOST: "redis"
  REDIS_PORT: "####"
EOF

echo "✅ Generated deployments/stock-tracker-env.yaml"
