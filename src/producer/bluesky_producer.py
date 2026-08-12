import asyncio
import json
import logging
import websockets
from quixstreams import Application

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
JETSTREAM_URL = "wss://jetstream.atproto.tools/subscribe?wantedCollections=app.bsky.feed.post"
KAFKA_BROKERS = "localhost:9092"
TOPIC_NAME = "raw-tech-events"
TARGET_KEYWORDS = {"#AppleEvent", "iPhone", "Rivian", "OpenAI"}

async def produce_events():
    app = Application(broker_address=KAFKA_BROKERS)
    tp = app.topic(TOPIC_NAME)

    while True:
        try:
            logger.info(f"Connecting to Bluesky Jetstream: {JETSTREAM_URL}")
            async with websockets.connect(JETSTREAM_URL) as ws:
                logger.info("Connected to Bluesky Jetstream")
                while True:
                    message = await ws.recv()
                    data = json.loads(message)
                    
                    # Extract post text from Jetstream payload
                    text = data.get("post", {}).get("record", {}).get("text", "")
                    if not text:
                        continue

                    if any(keyword.lower() in text.lower() for keyword in TARGET_KEYWORDS):
                        payload = {
                            "text": text,
                            "timestamp": data.get("timestamp"),
                            "source": "bluesky",
                            "keyword": next((k for k in TARGET_KEYWORDS if k.lower() in text.lower()), "unknown"),
                        }
                        tp.produce(value=json.dumps(payload).encode('utf-8'))
                        logger.info(f"Published event for keyword: {payload['keyword']}")

        except (websockets.ConnectionClosed, Exception) as e:
            logger.error(f"Connection error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(produce_events())
    except KeyboardInterrupt:
        pass
