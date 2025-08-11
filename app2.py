from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    AutoModelForCausalLM,
    AutoConfig,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Disable HF telemetry
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'

# Explainer model globals
explanation_tokenizer = None
explanation_model = None
explanation_is_encoder_decoder = None

EXPLAINER_MODEL_NAME = os.environ.get(
    'EXPLAINER_MODEL_NAME',
    'google/flan-t5-small'
).strip()

EXPLAINER_TRUST_REMOTE_CODE = os.environ.get(
    'EXPLAINER_TRUST_REMOTE_CODE', '0'
).strip() in ('1', 'true', 'True')

def load_explainer():
    global explanation_tokenizer, explanation_model, explanation_is_encoder_decoder
    if not EXPLAINER_MODEL_NAME:
        logger.warning("EXPLAINER_MODEL_NAME not set.")
        return
    try:
        logger.info(f"Loading explainer model: {EXPLAINER_MODEL_NAME} ...")
        config = AutoConfig.from_pretrained(EXPLAINER_MODEL_NAME,
                                            trust_remote_code=EXPLAINER_TRUST_REMOTE_CODE)
        explanation_is_encoder_decoder = getattr(config, 'is_encoder_decoder', False)

        explanation_tokenizer = AutoTokenizer.from_pretrained(
            EXPLAINER_MODEL_NAME, trust_remote_code=EXPLAINER_TRUST_REMOTE_CODE
        )

        model_cls = AutoModelForSeq2SeqLM if explanation_is_encoder_decoder else AutoModelForCausalLM
        explanation_model = model_cls.from_pretrained(
            EXPLAINER_MODEL_NAME,
            trust_remote_code=EXPLAINER_TRUST_REMOTE_CODE,
            torch_dtype=torch.float32,        # Force FP32
            device_map="auto",                # Use GPU if available
            low_cpu_mem_usage=False           # Avoid extra optimizations that change outputs
        )

        explanation_model.eval()
        arch = 'seq2seq' if explanation_is_encoder_decoder else 'causal'
        logger.info(f"Explainer model loaded successfully! Architecture: {arch}")

    except Exception as e:
        logger.error(f"Error loading explainer model: {e}")
        explanation_tokenizer = None
        explanation_model = None
        explanation_is_encoder_decoder = None

def generate_explanation_local(message: str, label: str) -> str | None:
    if not explanation_model or not explanation_tokenizer:
        return None
    try:
        prompt = (
    f"Instruction: Explain in 2-3 sentences why the following message is '{label}'. "
    f"Message: {message}\n"
    f"Explanation:"
)

        gen_kwargs = dict(
            max_new_tokens=100,
            temperature=0.7,
            do_sample=False,
            top_p=1.0,
        )

        if explanation_is_encoder_decoder:
            inputs = explanation_tokenizer(
                prompt, return_tensors="pt",
                truncation=True, padding=True, max_length=512
            ).to(explanation_model.device)
        else:
            inputs = explanation_tokenizer(
                prompt, return_tensors="pt",
                truncation=True, padding=True, max_length=1024
            ).to(explanation_model.device)
            gen_kwargs["pad_token_id"] = explanation_tokenizer.eos_token_id or explanation_tokenizer.pad_token_id

        with torch.no_grad():
            output_ids = explanation_model.generate(**inputs, **gen_kwargs)

        generated = explanation_tokenizer.decode(output_ids[0], skip_special_tokens=True)

        if not explanation_is_encoder_decoder and generated.startswith(prompt):
            generated = generated[len(prompt):]

        return generated.strip()

    except Exception as e:
        logger.error(f"Error generating local explanation: {e}")
        return None

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "healthy",
        "message": "Anti-Phishing Explanation API",
        "endpoints": {
            "/explain": "POST - Generate explanation for a classification",
            "/health": "GET - Health check"
        }
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "explainer_loaded": explanation_model is not None,
        "architecture": 'seq2seq' if explanation_is_encoder_decoder else ('causal' if explanation_model else None)
    })

@app.route("/explain", methods=["POST"])
def explain():
    try:
        data = request.get_json()
        if not data or "message" not in data or "label" not in data:
            return jsonify({"error": "Missing 'message' or 'label'"}), 400

        message = data["message"].strip()
        label = data["label"]
        if not message or label not in ("Safe", "Phishing"):
            return jsonify({"error": "Invalid 'message' or 'label'"}), 400

        explanation = generate_explanation_local(message, label)
        return jsonify({
            "label": label,
            "message": message,
            "explanation": explanation or ""
        })
    except Exception as e:
        logger.error(f"Error in explain endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Preload model before Flask runs to avoid Hugging Face Space timeout
load_explainer()

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=7861)
