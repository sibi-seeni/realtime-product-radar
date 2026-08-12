import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from optimum.onnxruntime import ORTModelForSequenceClassification, ORTQuantizer
from optimum.onnxruntime.config import QuantizationConfig

MODEL_ID = "distilbert-base-uncased-finetuned-sst-2-english"
EXPORT_PATH = "model_onnx"
MODEL_FILE = "model.onnx"

def export_and_quantize():
    # Load model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    
    # Export to ONNX
    model = ORTModelForSequenceClassification.from_pretrained(MODEL_ID, export=True)
    model.save_pretrained(EXPORT_PATH)

    # Apply INT8 Dynamic Quantization
    quantizer = ORTQuantizer.from_pretrained(MODEL_ID)
    dqconfig = QuantizationConfig(is_static=False, method="arm64") # Default dynamic
    quantizer.quantize(save_dir=EXPORT_PATH, quantization_config=dqconfig)
    
    print(f"Model exported and quantized to {EXPORT_PATH}")

if __name__ == "__main__":
    export_and_quantize()
