from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import logging

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

@app.route("/", methods=["GET"])
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Anti-Phishing Scanner API",
        "endpoints": {
            "/analyze": "POST - Analyze text for phishing",
            "/health": "GET - Health check"
        }
    })

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None
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
        
        # Make prediction
        label, confidence = predict_phishing(message.strip())
        
        return jsonify({
            "result": label,
            "confidence": f"{confidence}%",
            "message": message
        })
    
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}")
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