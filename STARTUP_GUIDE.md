# 🚀 YT2Blog Pro - Startup Guide

## Quick Start (3 Steps)

### Step 1: Start the Server
```bash
python run_enhanced_server.py
```

### Step 2: Test the API (in another terminal)
```bash
python test_features.py
```

### Step 3: Open the Application
- **Main App**: http://localhost:8000
- **Debug Version**: http://localhost:8000/debug_frontend.html
- **API Docs**: http://localhost:8000/docs

---

## Troubleshooting

### ❌ "Connection Refused" Error

**Problem**: The test script shows connection errors like:
```
Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it
```

**Solution**:
1. **Start the server first**:
   ```bash
   python run_enhanced_server.py
   ```
2. **Wait for the server to fully start** (you should see "Uvicorn running on...")
3. **Then run tests in another terminal**:
   ```bash
   python test_features.py
   ```

### ❌ Frontend Not Working

**Problem**: UI loads but buttons don't work or JavaScript errors

**Solutions**:
1. **Check browser console** (F12 → Console tab)
2. **Try the debug version**: http://localhost:8000/debug_frontend.html
3. **Clear browser cache** (Ctrl+F5)
4. **Check if server is running** on http://localhost:8000/api/health

### ❌ API Key Issues

**Problem**: "LLM Service Unavailable" or "NEBIUS_API_KEY not configured"

**Solution**:
1. **Check your .env file**:
   ```bash
   # Make sure .env exists and has:
   NEBIUS_API_KEY=your_actual_api_key_here
   ```
2. **Restart the server** after updating .env
3. **Test without API key** (basic features will work, blog generation won't)

### ❌ Import Errors

**Problem**: "ModuleNotFoundError" or import issues

**Solution**:
```bash
# Install all dependencies
pip install -r requirements.txt

# If still issues, try:
pip install fastapi uvicorn openai pytube youtube-transcript-api python-dotenv pydantic
```

---

## File Structure Check

Make sure you have these files:
```
your-project/
├── backend/
│   ├── main.py ✅
│   ├── config.py ✅
│   ├── youtube_service.py ✅
│   └── llm_service.py ✅
├── utils/
│   └── blog_generator.py ✅
├── index.html ✅
├── debug_frontend.html ✅
├── run_enhanced_server.py ✅
├── test_features.py ✅
├── requirements.txt ✅
├── .env (create from .env.example) ✅
└── .env.example ✅
```

---

## Testing Workflow

### 1. Basic Server Test
```bash
# Terminal 1: Start server
python run_enhanced_server.py

# Terminal 2: Test health
curl http://localhost:8000/api/health
```

### 2. API Endpoints Test
```bash
# Run comprehensive tests
python test_features.py
```

### 3. Frontend Test
1. Open http://localhost:8000
2. Try entering a YouTube URL
3. Check browser console for errors (F12)

### 4. Debug Mode Test
1. Open http://localhost:8000/debug_frontend.html
2. Click "Test Health" button
3. Click "Test Languages" button
4. Try "Test Video Info" with a YouTube URL

---

## Expected Behavior

### ✅ Server Startup
```
🎥 YT2Blog Pro - Enhanced AI-Powered YouTube to Blog Converter
============================================================
🚀 Starting server...
🌟 Enhanced Features Available:
   • Multi-language blog generation (8 languages)
   • Advanced content cleanup and humanization
   • Code tutorial detection and formatting
   • Rich text editor with export options
   • Project workspace and credit system

==================================================
🎯 Server starting at: http://localhost:8000
📖 API Documentation: http://localhost:8000/docs
🧪 Test with: python test_features.py (in another terminal)
==================================================

INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
```

### ✅ Test Results
```
🧪 Testing Enhanced YT2Blog API Features
==================================================
🔍 Checking if server is running...
✅ Server is running!

1. Testing health check...
✅ Health check passed
   Status: healthy
   YouTube Service: operational
   Blog Generator: operational

2. Testing languages endpoint...
✅ Languages endpoint working
   Available languages: 8
   - 🇺🇸 English (en)
   - 🇮🇳 Hindi (hi)
   - 🇪🇸 Spanish (es)

3. Testing templates endpoint...
✅ Templates endpoint working
   Available templates: 4
   - Article: Standard blog article format with introduction...
   - Tutorial: Step-by-step guide format with structured...
   - Review: Comprehensive review format with ratings...
   - Summary: Concise summary format with key highlights...
```

---

## Common Issues & Solutions

### Issue: Port Already in Use
```bash
# Kill process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9
```

### Issue: Python Path Problems
```bash
# Make sure you're in the project root directory
cd /path/to/your/project
python run_enhanced_server.py
```

### Issue: Browser Cache
- Clear browser cache (Ctrl+F5)
- Try incognito/private mode
- Try different browser

---

## Development Mode

For development with auto-reload:
```bash
# Start with auto-reload
uvicorn backend.main:app --host localhost --port 8000 --reload

# Or use the enhanced startup script
python run_enhanced_server.py
```

---

## Production Deployment

For production deployment:
1. Set `DEBUG=False` in .env
2. Use proper CORS origins
3. Use production ASGI server
4. Set up proper API keys

---

## Getting Help

If you're still having issues:

1. **Check the logs** in the terminal where you started the server
2. **Try the debug frontend** at http://localhost:8000/debug_frontend.html
3. **Check browser console** for JavaScript errors (F12)
4. **Verify your .env file** has the correct API keys
5. **Make sure all dependencies are installed**: `pip install -r requirements.txt`

---

## Success Indicators

You know everything is working when:
- ✅ Server starts without errors
- ✅ http://localhost:8000 loads the UI
- ✅ http://localhost:8000/api/health returns "healthy"
- ✅ test_features.py shows all green checkmarks
- ✅ You can enter a YouTube URL and see video info
- ✅ Language selector shows 8 languages
- ✅ Feature toggles work (Fact Cleanup, Humanize)

**🎉 You're ready to use YT2Blog Pro!**