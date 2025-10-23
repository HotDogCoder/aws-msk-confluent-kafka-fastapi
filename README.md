# FastAPI + AWS MSK (Kafka) Service

A minimal FastAPI service that produces to and consumes from Kafka using the high-performance `confluent-kafka` client. Designed to work with AWS MSK or Confluent Cloud via environment configuration.

## Features
- POST `/publish` endpoint to send messages (string or JSON) to a topic
- Background consumer that logs messages from configured topics
- Health check endpoint `/health` that verifies Kafka connectivity
- Environment-driven configuration (TLS, SASL, CA certs)

## Requirements
- Python 3.10+
- Network access to your AWS MSK or Kafka cluster
- For MSK with TLS: Amazon Root CA (`AmazonRootCA1.pem`) if needed

## Setup
1. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment:
   - Copy `.env.example` to `.env` and update values
   - Typical MSK TLS-only:
     - `KAFKA_SECURITY_PROTOCOL=SSL`
     - `KAFKA_SSL_CA_LOCATION=./certs/AmazonRootCA1.pem`
   - MSK/Confluent with SASL:
     - `KAFKA_SECURITY_PROTOCOL=SASL_SSL`
     - `KAFKA_SASL_MECHANISM=PLAIN` (or `SCRAM-SHA-512`)
     - `KAFKA_SASL_USERNAME` and `KAFKA_SASL_PASSWORD`

## Run
```bash
uvicorn app.main:app --reload
```
Open Swagger UI: http://localhost:8000/docs

## Publish Example
- Request:
  ```json
  {
    "topic": "events",
    "key": "user-123",
    "value": {"action": "signup", "timestamp": "2025-01-01T00:00:00Z"},
    "headers": {"source": "api"},
    "sync": false
  }
  ```
- Response:
  ```json
  {"topic":"events","status":"enqueued"}
  ```
Set `sync=true` to block until delivery confirmation.

## Notes for AWS MSK
- This project uses `confluent-kafka` (librdkafka). For MSK with TLS, set `KAFKA_SECURITY_PROTOCOL=SSL` and CA location to the Amazon Root CA if your system trust store does not include it.
- MSK IAM (SASL/OAUTHBEARER) auth is not configured here; prefer TLS or SASL/SCRAM/PLAIN.
- Ensure the app runs in the same VPC or has connectivity to MSK brokers.

## Files
- `app/config.py`: Env-driven settings and Kafka configs
- `app/kafka/producer.py`: Producer helper with optional synchronous delivery
- `app/kafka/consumer.py`: Background consumer thread with graceful shutdown
- `app/main.py`: FastAPI app and endpoints
- `.env.example`: Template for environment variables
- `requirements.txt`: Dependencies

## Troubleshooting
- If `pip install confluent-kafka` fails on macOS, install librdkafka:
  ```bash
  brew install librdkafka
  ```
- Verify broker reachability and ports (typically `9092` for PLAINTEXT, `9094` for SSL/SASL_SSL).
- Check group.id uniqueness per environment.