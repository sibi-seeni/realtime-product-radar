import json
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer
from quixstreams import Application

# Config
KAFKA_BROKERS = "localhost:9092"
INPUT_TOPIC = "raw-tech-events"
OUTPUT_TOPIC = "processed-tech-events"
MODEL_PATH = "model_onnx/model_quantized.onnx"
TOKENIZER_ID = "distilbert-base-uncased-finetuned-sst-2-english"

def create_processor():
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_ID)
    session = ort.InferenceSession(MODEL_PATH)

    app = Application(broker_address=KAFKA_BROKERS)
    input_topic = app.topic(INPUT_TOPIC)
    output_topic = app.topic(OUTPUT_TOPIC)

    def process_sentiment(record):
        text = record.get("text", "")
        if not text:
            return record

        # Tokenize
        inputs = tokenizer(text, return_tensors="np", padding=True, truncation=True, max_length=512)
        input_ids = inputs["input_ids"].astype(np.int64)
        attention_mask = inputs["attention_mask"].astype(np.int64)

        # Inference
        ort_inputs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask
        }
        logits = session.run(None, ort_inputs)[0]
        
        # Label
        sentiment_class = int(np.argmax(logits, axis=1)[0])
        confidence = float(np.max(np.exp(logits) / np.sum(np.exp(logits), axis=1))[0])

        record["sentiment_class"] = sentiment_class
        record["confidence"] = confidence
        return record

    app.dataframe(input_topic).map(process_sentiment).produce(output_topic)
    
    app.run()

if __name__ == "__main__":
    create_processor()
