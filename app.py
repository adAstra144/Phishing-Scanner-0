from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Set environment variables
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'

# Global variables for model and tokenizer
tokenizer = None
model = None
EXPLAINER_API_URL = os.environ.get('EXPLAINER_API_URL', '').strip()

def load_model():
    """Load the phishing detection model"""
    global tokenizer, model
    try:
        logger.info("Loading phishing detection model...")
        model_name = "ealvaradob/bert-finetuned-phishing"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        model.eval()  # Set to evaluation mode
        logger.info("Model loaded successfully!")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

def predict_phishing(text):
    """Predict if text is phishing or safe"""
    try:
        # Tokenize the input text
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        
        # Get prediction
        with torch.no_grad():
            outputs = model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
            confidence, predicted_class = torch.max(probabilities, dim=1)
        
        # Convert to human-readable format
        label = "Phishing" if predicted_class.item() == 1 else "Safe"
        confidence_percent = round(confidence.item() * 100, 1)
        
        return label, confidence_percent
    except Exception as e:
        logger.error(f"Error in prediction: {e}")
        raise

def fetch_explanation(message: str, label: str):
    """Call external explainer Space to generate an explanation.

    Expects EXPLAINER_API_URL env to point to a POST JSON endpoint that accepts
    {"message": str, "label": str} and returns JSON containing an explanation.

    Returns explanation string or None on failure/not configured.
    """
    if not EXPLAINER_API_URL:
        return None
    try:
        payload = {"message": message, "label": label}
        resp = requests.post(EXPLAINER_API_URL, json=payload, timeout=20)
        resp.raise_for_status()
        # Try to parse a few common shapes
        data = resp.json() if 'application/json' in resp.headers.get('Content-Type', '') else {}
        if isinstance(data, dict):
            for key in ("explanation", "reason", "detail", "output", "text"):
                if key in data and isinstance(data[key], str) and data[key].strip():
                    return data[key].strip()
            # HF Spaces gradio typical: { "data": ["..."] }
            if "data" in data and isinstance(data["data"], list):
                joined = "\n\n".join([str(x) for x in data["data"] if isinstance(x, (str, int, float))])
                if joined.strip():
                    return joined.strip()
        # Fallback to text
        text = resp.text.strip()
        return text if text else None
    except Exception as e:
        logger.error(f"Error calling explainer: {e}")
        return None

@app.route("/", methods=["GET"])
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Anti-Phishing Scanner API",
        "endpoints": {
            "/analyze": "POST - Analyze text for phishing",
            "/explain": "POST - Analyze and explain classification (if explainer configured)",
            "/health": "GET - Health check"
        }
    })

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "explainer_configured": bool(EXPLAINER_API_URL)
    })

@app.route("/analyze", methods=["POST"])
def analyze():
    """Analyze text for phishing detection"""
    try:
        # Get JSON data
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Missing 'message' field"}), 400
        
        message = data["message"]
        if not message or not message.strip():
            return jsonify({"error": "Message cannot be empty"}), 400
        include_explanation = bool(data.get("include_explanation"))
        
        # Make prediction
        label, confidence = predict_phishing(message.strip())
        explanation = None
        if include_explanation:
            explanation = fetch_explanation(message.strip(), label)
        
        resp = {
            "result": label,
            "confidence": f"{confidence}%",
            "message": message
        }
        if include_explanation:
            resp["explanation"] = explanation or ""
        return jsonify(resp)
    
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/explain", methods=["POST"])
def analyze_and_explain():
    """Analyze text and attempt to generate an explanation via external Space."""
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Missing 'message' field"}), 400

        message = data["message"]
        if not message or not message.strip():
            return jsonify({"error": "Message cannot be empty"}), 400

        # Allow client to pass a prior label; otherwise classify first
        prior_label = data.get("label")
        if prior_label and prior_label not in ("Safe", "Phishing"):
            prior_label = None
        if not prior_label:
            prior_label, confidence = predict_phishing(message.strip())
        else:
            _, confidence = predict_phishing(message.strip())

        explanation = fetch_explanation(message.strip(), prior_label)
        return jsonify({
            "result": prior_label,
            "confidence": f"{confidence}%",
            "message": message,
            "explanation": explanation or ""
        })
    except Exception as e:
        logger.error(f"Error in explain endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Load model on startup
if __name__ == "__main__":
    load_model()
    app.run(debug=False, host="0.0.0.0", port=7860)
else:
    # For Hugging Face Spaces
    load_model() 