# SûrLink Frontend - Netlify Deployment

This is the frontend for the Anti-Phishing Scanner, designed to be deployed on Netlify.

## Features

- **Modern UI**: Clean, responsive design with gradient backgrounds
- **Real-time Analysis**: Connect to Hugging Face Spaces backend
- **Statistics Tracking**: Local storage for scan statistics
- **History Management**: Recent scan history with visual indicators
- **API Status Monitoring**: Real-time backend connection status
- **Mobile Responsive**: Works on all device sizes

## Deployment to Netlify

### Option 1: Deploy via Netlify UI

1. Go to [netlify.com](https://netlify.com) and sign up/login
2. Click "New site from Git"
3. Connect your GitHub repository
4. Set build settings:
   - Build command: (leave empty - static site)
   - Publish directory: `frontend`
5. Click "Deploy site"

### Option 2: Deploy via Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Navigate to frontend directory
cd frontend

# Deploy
netlify deploy --prod
```

### Option 3: Drag & Drop

1. Zip the `frontend` folder
2. Go to [netlify.com](https://netlify.com)
3. Drag and drop the zip file to deploy

## Configuration

### Update API URL

After deploying your Hugging Face Spaces backend, update the API URL in `script.js`:

```javascript
// Replace with your actual Hugging Face Spaces URL
let apiUrl = "https://your-username-your-space-name.hf.space";
```

### Environment Variables (Optional)

You can set environment variables in Netlify:

1. Go to Site settings > Environment variables
2. Add variables if needed for different environments

## Local Development

To run locally:

```bash
cd frontend
python -m http.server 8000
# or
npx serve .
```

Then open `http://localhost:8000`

## File Structure

```
frontend/
├── index.html          # Main HTML file
├── style.css           # Styles and responsive design
├── script.js           # JavaScript functionality
└── README.md           # This file
```

## Features

### Chat Interface
- Real-time message analysis
- Typing indicators
- Progress bars
- Message history

### Statistics Dashboard
- Total scans counter
- Phishing detection count
- Safe message count
- Local storage persistence

### API Integration
- Health check monitoring
- Automatic reconnection
- Error handling
- Status indicators

### Responsive Design
- Mobile-first approach
- Tablet optimization
- Desktop enhancement
- Touch-friendly interface

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Performance

- Optimized for fast loading
- Minimal dependencies
- Efficient DOM manipulation
- Local storage for persistence

## Security

- CORS-enabled API calls
- Input sanitization
- Error boundary handling
- Secure communication with backend 