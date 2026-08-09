# Real-Time Product Launch Sentiment Radar

## Architecture Overview
This project is an event-driven, real-time streaming pipeline that ingests social commentary (Bluesky Firehose), runs low-latency INT8 ONNX sentiment inference, computes sliding time-window aggregations, and persists results in ClickHouse for Grafana visualization.

## Stack & Tech Choices
- **Broker:** Redpanda (via Docker Compose)
- **Ingestion:** Async Python (`websockets`, `aiohttp`) -> Redpanda
- **Stream Engine:** Python (`quixstreams` or `bytewax`)
- **Inference Engine:** `onnxruntime` with INT8 quantized DistilBERT / FinBERT
- **Sink / Database:** ClickHouse (Columnar OLAP)
- **Monitoring:** Grafana

## Directory Structure

```

realtime-product-radar/
├── docker/
│   ├── docker-compose.yml
│   └── clickhouse/
│       └── init.sql
├── src/
│   ├── producer/
│   │   └── bluesky_producer.py
│   ├── model/
│   │   ├── export_onnx.py
│   │   └── sentiment_onnx.py
│   └── processor/
│       └── stream_processor.py
├── tests/
└── requirements.txt

```

## Conventions & Rules
- Do NOT use heavy PyTorch runtimes in the stream processing worker; use `onnxruntime` exclusively for low-latency batch inference.
- Write clean, asynchronous, type-annotated Python code (Python 3.10+).
- Ensure all streaming producers handle WebSocket disconnects with graceful exponential backoff.
- Keep stream message payloads in JSON schema format containing `[text, timestamp, source, keyword, sentiment_class, confidence]`.