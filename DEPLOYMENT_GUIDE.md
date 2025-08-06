# 🚀 SûrLink Deployment Guide

Complete guide to deploy the Anti-Phishing Scanner using Hugging Face Spaces (Backend) + Netlify (Frontend).

## 📋 Prerequisites

- GitHub account
- Hugging Face account
- Netlify account
- Python 3.8+

## 🔧 Step 1: Prepare Your Repository

### 1.1 Push to GitHub

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit: Anti-Phishing Scanner"
git branch -M main
git remote add origin https://github.com/your-username/anti-phishing-scanner.git
git push -u origin main
```

### 1.2 Repository Structure

Your repository should look like this:

```
anti-phishing-scanner/
├── app.py                    # Hugging Face Spaces backend
├── requirements.txt          # Python dependencies
├── README_HF.md             # Backend documentation
├── frontend/                # Netlify frontend
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── README.md
└── DEPLOYMENT_GUIDE.md      # This file
```

## 🎯 Step 2: Deploy Backend to Hugging Face Spaces

### 2.1 Create a New Space

1. Go to [huggingface.co](https://huggingface.co)
2. Click "New Space"
3. Choose settings:
   - **Owner**: Your username
   - **Space name**: `anti-phishing-scanner` (or your preferred name)
   - **Space SDK**: `Gradio`
   - **License**: MIT
   - **Visibility**: Public

### 2.2 Configure Space Settings

In your Space settings, change:
- **Space SDK**: `Docker`
- **Hardware**: `CPU` (free tier)

### 2.3 Upload Files

Upload these files to your Space:
- `app.py`
- `requirements.txt`

### 2.4 Configure Space

Create a `.gitattributes` file in your Space:

```
*.py linguist-language=Python
```

### 2.5 Deploy

The Space will automatically build and deploy. You can monitor the build logs in the Space interface.

### 2.6 Get Your Space URL

Your Space URL will be:
```
https://your-username-anti-phishing-scanner.hf.space
```

## 🌐 Step 3: Deploy Frontend to Netlify

### 3.1 Deploy via Netlify UI

1. Go to [netlify.com](https://netlify.com)
2. Click "New site from Git"
3. Connect your GitHub repository
4. Configure build settings:
   - **Base directory**: (leave empty)
   - **Build command**: (leave empty)
   - **Publish directory**: `frontend`
5. Click "Deploy site"

### 3.2 Update API URL

After deployment, update the API URL in `frontend/script.js`:

```javascript
// Replace with your actual Hugging Face Spaces URL
let apiUrl = "https://your-username-anti-phishing-scanner.hf.space";
```

### 3.3 Redeploy

After updating the API URL, redeploy your Netlify site.

## 🔗 Step 4: Connect Frontend to Backend

### 4.1 Test the Connection

1. Open your Netlify site
2. Check the API status indicator in the sidebar
3. Try scanning a test message

### 4.2 Troubleshooting

If the connection fails:

1. **Check CORS**: Ensure your Hugging Face Space has CORS enabled
2. **Check URL**: Verify the API URL is correct
3. **Check Space Status**: Ensure your Space is running
4. **Check Network**: Use browser dev tools to debug network requests

## 🧪 Step 5: Testing

### 5.1 Test Messages

Try these test messages:

**Phishing Examples:**
- "Your account has been suspended. Click here to verify immediately."
- "Congratulations! You've won $1000. Claim your prize now."
- "Your package is ready for pickup. Click to confirm delivery."

**Safe Examples:**
- "Thank you for your order. Your confirmation number is 12345."
- "Your monthly newsletter is ready to read."
- "Welcome to our service! Here's your account information."

### 5.2 Monitor Performance

- Check response times
- Monitor error rates
- Verify statistics tracking
- Test mobile responsiveness

## 🔧 Step 6: Customization

### 6.1 Update Branding

Edit `frontend/index.html`:
```html
<title>🛡️ Your Brand Name - Anti-Phishing Scanner</title>
```

### 6.2 Update Colors

Edit `frontend/style.css`:
```css
/* Update gradient colors */
background: linear-gradient(135deg, #your-color1 0%, #your-color2 100%);
```

### 6.3 Add Features

- Custom domain setup
- Analytics integration
- Additional security features
- Enhanced UI components

## 📊 Step 7: Monitoring

### 7.1 Hugging Face Spaces

- Monitor Space logs
- Check resource usage
- Review error messages
- Monitor API performance

### 7.2 Netlify

- Monitor site performance
- Check deployment status
- Review analytics
- Monitor form submissions

## 🚨 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure CORS is enabled in your Space
   - Check API URL format

2. **Model Loading Issues**
   - Check Space logs for errors
   - Verify model dependencies

3. **Frontend Not Loading**
   - Check Netlify deployment status
   - Verify file paths

4. **API Connection Issues**
   - Check Space status
   - Verify API endpoints
   - Test with curl/Postman

### Debug Commands

```bash
# Test API locally
curl -X POST http://localhost:7860/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "test message"}'

# Test Hugging Face Space
curl -X POST https://your-space.hf.space/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "test message"}'
```

## 📈 Step 8: Optimization

### 8.1 Performance

- Enable caching
- Optimize images
- Minify CSS/JS
- Use CDN

### 8.2 Security

- Enable HTTPS
- Set security headers
- Implement rate limiting
- Add input validation

### 8.3 Analytics

- Google Analytics
- Error tracking
- Performance monitoring
- User behavior analysis

## 🎉 Success!

Your Anti-Phishing Scanner is now deployed and ready to use!

**Backend**: Hugging Face Spaces
**Frontend**: Netlify
**Features**: Real-time phishing detection, statistics, history, responsive design

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section
2. Review Space and Netlify logs
3. Test with simple examples
4. Verify all URLs and configurations

## 🔄 Updates

To update your deployment:

1. **Backend**: Push changes to your Hugging Face Space
2. **Frontend**: Push changes to GitHub (Netlify auto-deploys)
3. **Test**: Verify functionality after updates

---

**Happy Deploying! 🚀** 