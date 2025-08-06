# Anti-Phishing Scanner - Hugging Face Spaces Backend

This is the backend API for the Anti-Phishing Scanner, deployed on Hugging Face Spaces.

## Features

- **Phishing Detection**: Uses a fine-tuned BERT model to detect phishing attempts in text
- **RESTful API**: Simple POST endpoint for text analysis
- **CORS Enabled**: Ready for frontend integration
- **Error Handling**: Comprehensive error handling and logging

## API Endpoints

### Health Check
```
GET /
```
Returns API status and available endpoints.

### Analyze Text
```
POST /analyze
Content-Type: application/json

{
  "message": "Your text to analyze here"
}
```

**Response:**
```json
{
  "result": "Phishing|Safe",
  "confidence": "85.2%",
  "message": "Your text to analyze here"
}
```

## Model

Uses the `ealvaradob/bert-finetuned-phishing` model for phishing detection.

## Deployment

This is configured for Hugging Face Spaces deployment. The app will automatically:

1. Load the model on startup
2. Serve the API on port 7860
3. Handle CORS for frontend integration

## Local Development

To run locally:

```bash
pip install -r requirements.txt
python app.py
```

The API will be available at `http://localhost:7860`

## Frontend Integration

The frontend should make POST requests to `/analyze` with JSON data containing a "message" field. 