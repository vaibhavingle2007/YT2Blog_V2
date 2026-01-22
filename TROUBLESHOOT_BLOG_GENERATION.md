# 🔧 Troubleshooting Blog Generation

## The Issue
Blog generation is not working or not showing in the main HTML page.

## Step-by-Step Debugging

### Step 1: Test Blog Generation API Directly
```bash
python test_blog_generation.py
```

**Expected Output:**
```
✅ Blog generation successful!
📊 Response Details:
   Template: article
   Language: en
   Word Count: 1250
   Reading Time: 6 min
   📝 Generated Content Preview:
   # How to Never Give You Up: A Comprehensive Guide...
```

**If this fails:** The issue is with the backend/API
**If this works:** The issue is with the frontend JavaScript

### Step 2: Test with Debug Interface
Open in browser: http://localhost:8000/debug-blog

1. Click "Step 1: Video Info" - Should show video details
2. Click "Step 2: Generate Blog" - Should show generated blog
3. Click "Full Test" - Should do both steps automatically

### Step 3: Check Browser Console
1. Open main app: http://localhost:8000
2. Press F12 → Console tab
3. Try generating a blog
4. Look for JavaScript errors (red text)

## Common Issues & Solutions

### ❌ Issue 1: "LLM Service Unavailable"
**Cause:** NEBIUS_API_KEY not configured or invalid

**Solution:**
1. Check your `.env` file:
   ```
   NEBIUS_API_KEY=your_actual_key_here
   ```
2. Restart the server after updating .env
3. Test with: `python test_blog_generation.py`

### ❌ Issue 2: API Timeout
**Cause:** LLM service is slow or unresponsive

**Solution:**
1. Try with a shorter video
2. Check internet connection
3. Try different template (summary is fastest)

### ❌ Issue 3: JavaScript Errors
**Cause:** Frontend JavaScript issues

**Common Errors:**
- `Cannot read property of undefined`
- `Fetch failed`
- `Network error`

**Solution:**
1. Clear browser cache (Ctrl+F5)
2. Try incognito mode
3. Check browser console for specific errors
4. Use debug interface: http://localhost:8000/debug-blog

### ❌ Issue 4: CORS Errors
**Cause:** Cross-origin request blocked

**Solution:**
1. Make sure server is running on localhost:8000
2. Check CORS settings in backend/main.py
3. Try different browser

### ❌ Issue 5: UI Not Updating
**Cause:** Frontend state management issues

**Solution:**
1. Check if loading animation starts
2. Check if progress bar moves
3. Look for JavaScript errors in console
4. Try refreshing the page

## Debugging Checklist

### ✅ Backend Checks
- [ ] Server is running on localhost:8000
- [ ] NEBIUS_API_KEY is in .env file
- [ ] `python test_blog_generation.py` works
- [ ] http://localhost:8000/api/health returns "healthy"

### ✅ Frontend Checks
- [ ] http://localhost:8000 loads without errors
- [ ] Browser console shows no JavaScript errors
- [ ] URL validation works (green checkmark)
- [ ] Generate button is clickable
- [ ] Loading animation appears when clicked

### ✅ API Checks
- [ ] http://localhost:8000/api/templates returns 4 templates
- [ ] http://localhost:8000/api/languages returns 8 languages
- [ ] Video info endpoint works with test URL

## Quick Fixes

### Fix 1: Restart Everything
```bash
# Stop server (Ctrl+C)
# Then restart
python run_enhanced_server.py
```

### Fix 2: Clear Browser Cache
- Press Ctrl+F5 (hard refresh)
- Or try incognito/private mode

### Fix 3: Test with Simple URL
Use this test URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`

### Fix 4: Check Network Tab
1. Open browser DevTools (F12)
2. Go to Network tab
3. Try generating blog
4. Look for failed requests (red entries)

## Expected Behavior

### ✅ What Should Happen:
1. Enter YouTube URL → Green checkmark appears
2. Click "Generate Blog" → Loading animation starts
3. Progress bar moves through 3 steps
4. Video preview appears with thumbnail and details
5. Blog editor appears with generated content
6. Word count and reading time update

### ❌ What Indicates Problems:
- No loading animation
- Progress bar doesn't move
- Error messages in browser console
- "Generate Blog" button stays disabled
- No content appears after loading

## Advanced Debugging

### Check Server Logs
Look at the terminal where you started the server for error messages.

### Test Individual Components
```bash
# Test just the LLM service
python -c "from utils.blog_generator import BlogGenerator; bg = BlogGenerator(); print('LLM enabled:', bg.llm_enabled)"

# Test just YouTube service
python -c "from backend.youtube_service import YouTubeService; ys = YouTubeService(); print(ys.get_video_metadata('dQw4w9WgXcQ'))"
```

### Check API Response Format
Use the debug interface at http://localhost:8000/debug-blog to see exact API responses.

## Getting Help

If none of these solutions work:

1. **Run the debug test:**
   ```bash
   python test_blog_generation.py
   ```

2. **Check the debug interface:**
   http://localhost:8000/debug-blog

3. **Share the output** of both tests to identify the exact issue.

## Success Indicators

You know blog generation is working when:
- ✅ `python test_blog_generation.py` shows generated content
- ✅ Debug interface shows blog content
- ✅ Main app shows loading → progress → blog content
- ✅ No JavaScript errors in browser console
- ✅ Generated blog appears in the editor

**🎯 Most issues are either missing API keys or JavaScript errors in the browser console.**