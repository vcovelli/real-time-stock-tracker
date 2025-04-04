# Real-Time Stock Tracker

A scalable real-time stock tracking platform that fetches market data from Alpaca, streams it through Kafka, and stores it in PostgreSQL for analysis. Designed for financial insight, algorithmic trading, and future-ready dashboards.
---
## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Technologies Used](#technologies-used)
- [Setup](#setup)
- [Usage](#usage)
- [Future Enhancements](#future-enhancements)
---
## Features
- Real-time stock price ingestion via **Alpaca API**
- Streamed data using **Kafka** (websocket + mock support)
- Stored in **PostgreSQL (TimescaleDB)** for time-series optimization
- Candlestick chart data generated using **ksqlDB**
- Monitoring with **Prometheus + Grafana**
- Dockerized microservices
- Kubernetes-ready deployments
- Local mock market generator for testing
---
## Architecture
- Alpaca WebSocket ➝ Producer ➝ Kafka ➝ Consumer ➝ PostgreSQL 
- Optional flow: Kafka ➝ ksqlDB ➝ OHLC ➝ PostgreSQL
---
## Technologies Used

- **Python**: Core programming language.
- **Kafka & Kafka-Python**: Message broker for streaming data.
- **PostgreSQL**: Database for data storage.
- **Docker & Docker-Compose**: Containerization and orchestration.
---
## Setup

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Alpaca API credentials (optional for live data)

### Clone the Repository

```
   git clone https://github.com/yourusername/real-time-stock-tracker.git
```
```
   cd real-time-stock-tracker
```

### Start Services
```
	docker-compose up -d
```
Includes Zookeeper, Kafka, PostgreSQL, and mock producer setup.
---
## Usage

### Producer (WebSocket or Mock)
```
python3 scripts/fetch_stock_data.py
```
Can switch between Alpaca and mock websocket via .env flag USE_MOCK=True

### Consumer (Kafka ➝ Postgres)
```
python3 scripts/kafka_to_postgres.py
```
Streams real-time prices into the stock_prices table
---
## PostgreSQL Schema
```
CREATE TABLE stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10),
    timestamp TIMESTAMPTZ NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT
);
```
```
SELECT create_hypertable('stock_prices', 'timestamp');
```
Enable TimescaleDB
---
## Monitoring
- Prometheus scrapes service metrics
- Grafana dashboards visualize Kafka health, consumer lag, and DB writes
- Setup lives in config/monitoring/
---
## Testing
- Run mock_market_generator.py to simulate closed market conditions
- Switch between test and production configs using .env
---
## Future Enhancements

- Live candlestick chart visualizations in React or Streamlit
- ML models for anomaly detection and strategy backtesting
- RBAC for dashboard access control
- Web UI for selecting stock symbols on the fly
- Level 2 market data
---