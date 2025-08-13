from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import torch
import requests
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    AutoModelForCausalLM,
    AutoConfig,
)
from gradio_client import Client

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

# Remote Space configuration (defaults provided by user)
REMOTE_EXPLAINER_SPACE = os.environ.get(
    'REMOTE_EXPLAINER_SPACE',
    'X-014/HuggingFaceH4-zephyr-7b-beta'
).strip()
REMOTE_API_NAME = os.environ.get('REMOTE_API_NAME', '/predict').strip()
REMOTE_PREDICT_URL = os.environ.get(
    'REMOTE_PREDICT_URL',
    'https://X-014-HuggingFaceH4-zephyr-7b-beta.hf.space/run/predict'
).strip()
HF_TOKEN = os.environ.get('HF_TOKEN')

remote_client: Client | None = None
try:
    if REMOTE_EXPLAINER_SPACE:
        remote_client = Client(REMOTE_EXPLAINER_SPACE, hf_token=HF_TOKEN)
        logger.info(f"Initialized remote Space client for: {REMOTE_EXPLAINER_SPACE}")
except Exception as e:
    logger.error(f"Failed to initialize remote Space client: {e}")
    remote_client = None

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

def _build_explanation_prompt(message: str, label: str) -> str:
    return (
        f"Task: Provide a short rationale (2-3 sentences) for why the message is classified as {label}.\n"
        "Rules:\n"
        "- Do not repeat or quote the original message.\n"
        "- Mention concrete cues (urgency, credential requests, suspicious links/domains, poor grammar, sender spoofing).\n"
        "- Be concise.\n"
        f"Message:\n{message}\n"
        "Rationale:"
    )

def generate_explanation_remote(message: str, label: str) -> str | None:
    """Attempt to get an explanation from the configured remote Space.

    Tries gradio_client first (with several common api_names), then falls back
    to direct POST to /run/predict if available.
    """
    prompt = _build_explanation_prompt(message, label)

    # Try gradio_client across common endpoints
    if remote_client is not None:
        api_candidates = [REMOTE_API_NAME, '/predict', '/chat', '/generate', '/infer']
        tried = set()
        for api_name in api_candidates:
            if not api_name or api_name in tried:
                continue
            tried.add(api_name)
            try:
                out = remote_client.predict(prompt, api_name=api_name)
                if isinstance(out, dict):
                    # Common keys in Spaces
                    for key in ("text", "explanation", "output", "result"):
                        if key in out and isinstance(out[key], str):
                            return out[key].strip()
                    # Fallback string conversion
                    return str(out).strip()
                if isinstance(out, (list, tuple)) and out:
                    return str(out[0]).strip()
                return str(out).strip()
            except Exception as e:
                logger.debug(f"Remote Space predict failed for {api_name}: {e}")

    # Fallback: direct HTTP to /run/predict (gradio HTTP API)
    try:
        if REMOTE_PREDICT_URL:
            resp = requests.post(
                REMOTE_PREDICT_URL,
                json={"data": [prompt]},
                timeout=60
            )
            if resp.ok:
                payload = resp.json()
                # Try common shapes
                if isinstance(payload, dict):
                    if 'data' in payload and payload['data']:
                        return str(payload['data'][0]).strip()
                    for key in ("text", "explanation", "output", "result"):
                        if key in payload and isinstance(payload[key], str):
                            return payload[key].strip()
                # Fallback to string conversion
                return str(payload).strip()
    except Exception as e:
        logger.error(f"Remote HTTP predict error: {e}")

    return None
    try:
        prompt = (
            f"Task: Provide a short rationale (2-3 sentences) for why the message is classified as {label}.\n"
            "Rules:\n"
            "- Do not repeat or quote the original message.\n"
            "- Mention concrete cues (urgency, credential requests, suspicious links/domains, poor grammar, sender spoofing).\n"
            "- Be concise.\n"
            f"Message:\n{message}\n"
            "Rationale:"
        )

        gen_kwargs = dict(
            max_new_tokens=120,
            do_sample=False,           # deterministic
            num_beams=4,               # improves adherence to instructions
            no_repeat_ngram_size=5,    # avoid copying long spans
            repetition_penalty=1.15,
            length_penalty=1.0,
            early_stopping=True,
            top_p=1.0,
            temperature=0.0,           # ignored when do_sample=False, but explicit
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

        # Remove prompt echo for causal LMs
        if not explanation_is_encoder_decoder and generated.startswith(prompt):
            generated = generated[len(prompt):]

        # Light cleanup to avoid prefixed markers
        generated = generated.replace("Rationale:", "").replace("Explanation:", "").strip()

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

        # Prefer remote Space if configured, with local as fallback
        explanation = generate_explanation_remote(message, label)
        if not explanation:
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
    app.run(debug=True, host="0.0.0.0", port=7861)
