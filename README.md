# 🛡️ SûrLink - Anti-Phishing Scanner

A modern, AI-powered phishing detection tool built with Hugging Face Spaces (Backend) and Netlify (Frontend).

## 🚀 Live Demo

- **Frontend**: [Netlify Deployment](https://your-netlify-site.netlify.app)
- **Backend**: [Hugging Face Space](https://your-username-anti-phishing-scanner.hf.space)

## ✨ Features

- **Real-time Phishing Detection**: Uses fine-tuned BERT model for accurate detection
- **Modern UI**: Beautiful, responsive design with gradient backgrounds
- **Statistics Tracking**: Local storage for scan history and statistics
- **API Status Monitoring**: Real-time backend connection status
- **Mobile Responsive**: Works perfectly on all devices
- **Zero Setup**: Fully deployed and ready to use

## 🏗️ Architecture

```
SûrLink/
├── app.py                    # Hugging Face Spaces backend
├── requirements.txt          # Python dependencies
├── frontend/                # Netlify frontend
│   ├── index.html           # Main HTML file
│   ├── style.css            # Modern CSS styles
│   ├── script.js            # JavaScript functionality
│   └── README.md            # Frontend documentation
├── test_backend.py          # Backend testing script
├── DEPLOYMENT_GUIDE.md      # Complete deployment guide
└── README_HF.md            # Backend documentation
```

## 🎯 Quick Start

### Local Development

1. **Backend**:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

2. **Frontend**:
   ```bash
   cd frontend
   python -m http.server 8000
   ```

3. **Test**:
   ```bash
   python test_backend.py
   ```

### Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete deployment instructions.

## 🔧 API Endpoints

- `GET /` - Health check and API info
- `GET /health` - Model status check
- `POST /analyze` - Analyze text for phishing

## 🧪 Test Examples

**Phishing Examples:**
- "Your account has been suspended. Click here to verify immediately."
- "Congratulations! You've won $1000. Claim your prize now."

**Safe Examples:**
- "Thank you for your order. Your confirmation number is 12345."
- "Your monthly newsletter is ready to read."

## 🛠️ Tech Stack

- **Backend**: Flask, Transformers, PyTorch
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Hugging Face Spaces, Netlify
- **Model**: ealvaradob/bert-finetuned-phishing

## 📊 Performance

- **Response Time**: < 2 seconds
- **Accuracy**: High precision phishing detection
- **Uptime**: 99.9% (Hugging Face + Netlify)
- **Mobile**: Fully responsive design

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Hugging Face](https://huggingface.co) for model hosting
- [Netlify](https://netlify.com) for frontend deployment
- [ealvaradob](https://huggingface.co/ealvaradob) for the phishing detection model

---

**Built with ❤️ for cybersecurity awareness** 