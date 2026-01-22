# 🚀 Deployment Guide - YouTube to Blog Converter

This guide covers how to deploy your YouTube to Blog Converter application to various hosting platforms.

## 📋 Pre-Deployment Checklist

### ✅ Required Setup
- [ ] All environment variables configured in `.env`
- [ ] `NEBIUS_API_KEY` obtained from [Nebius AI Studio](https://studio.nebius.ai/)
- [ ] Optional: `YOUTUBE_API_KEY` from [Google Cloud Console](https://console.cloud.google.com/)
- [ ] Test application locally with `python run_server.py`
- [ ] Verify all features work (video conversion, template switching, progressive loading)

### ✅ Repository Preparation
- [ ] All files committed to Git
- [ ] `.env` file excluded (included in `.gitignore`)
- [ ] Dependencies listed in `requirements.txt`
- [ ] README.md updated with correct URLs

## 🏗️ Backend Deployment Options

### Option 1: Railway (Recommended)
Railway provides excellent Python support with automatic deployments.

1. **Create Railway Account**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   ```

2. **Deploy Backend**
   ```bash
   # In your project directory
   railway init
   railway add --service backend
   
   # Set environment variables
   railway variables set NEBIUS_API_KEY=your_key_here
   railway variables set YOUTUBE_API_KEY=your_key_here
   railway variables set HOST=0.0.0.0
   railway variables set PORT=8000
   
   # Deploy
   railway up
   ```

3. **Configure Startup**
   Create `Procfile` in project root:
   ```
   web: python run_server.py
   ```

### Option 2: Heroku
1. **Install Heroku CLI**
2. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set NEBIUS_API_KEY=your_key_here
   heroku config:set YOUTUBE_API_KEY=your_key_here
   heroku config:set HOST=0.0.0.0
   heroku config:set PORT=$PORT
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

### Option 3: DigitalOcean App Platform
1. **Connect GitHub Repository**
2. **Configure Build Settings**
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `python run_server.py`
3. **Set Environment Variables** in the dashboard
4. **Deploy**

## 🌐 Frontend Deployment Options

### Option 1: Vercel (Recommended)
Perfect for static site hosting with excellent performance.

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Create `vercel.json`**
   ```json
   {
     "functions": {
       "backend/main.py": {
         "runtime": "@vercel/python"
       }
     },
     "routes": [
       {
         "src": "/api/(.*)",
         "dest": "/backend/main.py"
       },
       {
         "src": "/(.*)",
         "dest": "/$1"
       }
     ]
   }
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

### Option 2: Netlify
1. **Connect GitHub Repository**
2. **Build Settings**
   - Build command: (leave empty)
   - Publish directory: `/` (root)
3. **Environment Variables**
   - Add your API keys in Netlify dashboard
4. **Deploy**

### Option 3: GitHub Pages
1. **Create `gh-pages` branch**
2. **Enable GitHub Pages** in repository settings
3. **Update API URLs** to point to your backend deployment

## 🔧 Environment Configuration

### Production Environment Variables
```bash
# Required
NEBIUS_API_KEY=your_nebius_api_key

# Optional (with fallbacks)
YOUTUBE_API_KEY=your_youtube_api_key

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# CORS (Update with your frontend domain)
CORS_ORIGINS=["https://your-frontend-domain.com"]
```

### Frontend Configuration
Update the API base URL in `index.html`:

```javascript
// Development
const API_BASE_URL = 'http://localhost:8000';

// Production (replace with your backend URL)
const API_BASE_URL = 'https://your-backend.railway.app';
```

## 🌍 Full-Stack Deployment (Recommended Architecture)

### Recommended Setup:
- **Backend**: Railway or Heroku
- **Frontend**: Vercel or Netlify
- **Domain**: Custom domain pointing to frontend
- **CDN**: Automatic with Vercel/Netlify

### Step-by-Step:

1. **Deploy Backend First**
   ```bash
   # Deploy to Railway
   railway up
   # Note the deployment URL: https://your-app.railway.app
   ```

2. **Update Frontend API URL**
   ```javascript
   const API_BASE_URL = 'https://your-app.railway.app';
   ```

3. **Deploy Frontend**
   ```bash
   # Deploy to Vercel
   vercel --prod
   # Get URL: https://your-app.vercel.app
   ```

4. **Update CORS Settings**
   ```bash
   # On Railway, update environment variables
   railway variables set CORS_ORIGINS=["https://your-app.vercel.app"]
   ```

## 🔒 Security Considerations

### Production Security
- [ ] Use HTTPS for all deployments
- [ ] Set specific CORS origins (not `["*"]`)
- [ ] Enable rate limiting
- [ ] Monitor API usage
- [ ] Keep API keys secure

### Environment Security
```bash
# Never commit these to Git
NEBIUS_API_KEY=keep_this_secret
YOUTUBE_API_KEY=keep_this_secret
```

## 📊 Monitoring & Analytics

### Health Monitoring
- Set up health check endpoints: `/api/health`
- Monitor response times and error rates
- Use services like UptimeRobot for monitoring

### Analytics Integration
Update the analytics tracking in `index.html`:
```javascript
// Google Analytics
gtag('config', 'GA_MEASUREMENT_ID');

// Plausible Analytics
plausible('pageview');
```

## 🚀 CI/CD Automation

### GitHub Actions (Optional)
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to Railway
      run: railway up
      env:
        RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

## 🔧 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Update `CORS_ORIGINS` in backend configuration
   - Ensure frontend URL is included

2. **API Key Issues**
   - Verify environment variables are set correctly
   - Check API key validity

3. **Build Failures**
   - Ensure `requirements.txt` is up to date
   - Check Python version compatibility

4. **Performance Issues**
   - Enable compression
   - Use CDN for static assets
   - Optimize images

### Debug Commands
```bash
# Check environment variables
railway variables

# View logs
railway logs

# Local testing
python run_server.py
```

## ✅ Post-Deployment Checklist

- [ ] All features working in production
- [ ] Analytics tracking properly
- [ ] Error monitoring set up
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active
- [ ] Performance optimized
- [ ] Backup strategy in place

## 📞 Support

For deployment issues:
1. Check the troubleshooting section
2. Review platform-specific documentation
3. Create an issue in the GitHub repository
4. Contact the community for help

---

**Happy Deploying! 🚀**

Your YouTube to Blog Converter is ready to serve users worldwide! 