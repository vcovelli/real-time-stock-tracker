# Real-Time Stock Tracker

This project is a real-time stock tracking application that fetches stock data, streams it to Kafka, and stores it in a PostgreSQL database. The data pipeline allows you to monitor stock prices in real-time, making it ideal for financial analysis, trading insights, and data visualizations.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Technologies Used](#technologies-used)
- [Setup](#setup)
- [Usage](#usage)
- [Future Enhancements](#future-enhancements)

## Architecture

1. **Producer Script (`fetch_stock_data.py`)**: Fetches stock data from Yahoo Finance API and streams it to a Kafka topic (`stock-data`).
2. **Kafka Broker**: Receives data from the producer and holds it until the consumer retrieves it.
3. **Consumer Script (`kafka_to_postgres.py`)**: Reads data from the Kafka topic and stores it in a PostgreSQL table.
4. **PostgreSQL Database**: Stores historical stock data for analysis and visualization.

## Technologies Used

- **Python**: Core programming language.
- **Kafka & Kafka-Python**: Message broker for streaming data.
- **PostgreSQL**: Database for data storage.
- **Docker & Docker-Compose**: Containerization and orchestration.

## Setup

### Prerequisites

Ensure you have the following installed:
- **Docker** and **Docker-Compose**
- **Python 3** and required libraries (`kafka-python`, `psycopg2`, `yfinance`)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/real-time-stock-tracker.git
   cd real-time-stock-tracker

2. **Install Python Dependencies**

	pip install -r requirements.txt

3. **Start Docker Services**
	Start Zookeeper, Kafka, and PostgreSQL with Docker Compose:

	docker-compose up -d

4. **Initialize the PostgreSQL Database**
	Access PostgreSQL in the Docker container:

	docker exec -it postgres psql -U stock_user -d stock_data

	Create the table schema:

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

## Usage

1. **Start the Kafka Producer**: This script fetches stock data and sends it to Kafka.
   ```bash
   python3 fetch_stock_data.py

2. **Start the Kafka Consumer**: This script read data from Kafka and inserts it into PostgreSQl

	python3 kafka_to_postgres.py

3. **Query Data in PostgreSQL**: After running both scripts, you can query data in PostgreSQL to view real-time stock updates:

	SELECT * FROM stock_prices LIMIT 5;

## Future Enhancements

- **Real-Time Dashboard**: Add a visualization tool (e.g., Tableau, Grafana) to monitor real-time stock data.
- **Data Analysis**: Implement statistical analyses or machine learning models to gain insights from historical stock data.
- **Additional Symbols**: Extend the script to fetch data for multiple stock symbols.

