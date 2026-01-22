# 🚀 Vercel Deployment Guide

This guide will help you deploy your YT2Blog Pro application to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI** (optional): Install with `npm i -g vercel`
3. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, or Bitbucket)

## Project Structure

The project is configured for Vercel with:
- `vercel.json` - Vercel configuration
- `api/index.py` - Serverless function entry point
- `backend/main.py` - FastAPI application
- `index.html` - Frontend HTML
- `public/` - Static assets

## Deployment Steps

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Push your code to GitHub/GitLab/Bitbucket**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Import Project in Vercel**
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "Add New Project"
   - Import your Git repository
   - Vercel will auto-detect the Python project

3. **Configure Environment Variables**
   In the Vercel dashboard, go to Settings → Environment Variables and add:
   
   **Required:**
   ```
   NEBIUS_API_KEY=your_nebius_api_key_here
   ```
   
   **Optional but Recommended:**
   ```
   YOUTUBE_API_KEY=your_youtube_api_key_here
   FIREBASE_API_KEY=your_firebase_api_key
   FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   FIREBASE_PROJECT_ID=your_project_id
   FIREBASE_STORAGE_BUCKET=your_project.appspot.com
   FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   FIREBASE_APP_ID=your_app_id
   FIREBASE_SERVICE_ACCOUNT_JSON=your_service_account_json
   STRIPE_SECRET_KEY=your_stripe_secret_key
   STRIPE_WEBHOOK_SECRET=your_webhook_secret
   PUBLIC_APP_URL=https://your-project.vercel.app
   DEBUG=False
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for the build to complete
   - Your app will be live at `https://your-project.vercel.app`

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel
   ```
   
   Follow the prompts:
   - Link to existing project or create new
   - Confirm project settings
   - Add environment variables when prompted

4. **Deploy to Production**
   ```bash
   vercel --prod
   ```

## Configuration Files

### vercel.json
Routes all requests to the FastAPI serverless function and serves static files.

### api/index.py
Entry point for Vercel's serverless function. Imports and exports the FastAPI app.

### .vercelignore
Excludes unnecessary files from deployment (cache, tests, docs, etc.)

## Important Notes

### ⚠️ Limitations

1. **Function Timeout**: Vercel serverless functions have a 10-second timeout on Hobby plan, 60 seconds on Pro plan. Blog generation might take longer.

2. **Cold Starts**: First request after inactivity may be slow (5-10 seconds).

3. **File System**: Vercel functions are read-only. Don't write files to disk.

4. **Memory**: Limited to 1GB on Hobby plan, 3GB on Pro plan.

### ✅ Best Practices

1. **Environment Variables**: Never commit `.env` files. Use Vercel's environment variables.

2. **CORS**: Already configured to allow Vercel domains (`*.vercel.app`).

3. **Static Assets**: Files in `public/` are served directly by Vercel.

4. **API Routes**: All `/api/*` routes are handled by the FastAPI serverless function.

## Troubleshooting

### Build Fails

1. **Check Python Version**: Vercel uses Python 3.11 by default (configured in `vercel.json`).

2. **Check Dependencies**: Ensure `requirements.txt` has all needed packages.

3. **Check Logs**: View build logs in Vercel dashboard for specific errors.

### Function Timeout

If blog generation times out:
- Upgrade to Vercel Pro plan (60-second timeout)
- Optimize LLM API calls
- Consider using Vercel Edge Functions for faster responses

### CORS Errors

If you see CORS errors:
- Check that your domain is in `CORS_ORIGINS` in `backend/config.py`
- Verify environment variables are set correctly

### Static Files Not Loading

- Ensure files are in the `public/` directory
- Check that routes in `vercel.json` are correct
- Verify file paths in HTML are relative (e.g., `/public/favicon.ico`)

## Post-Deployment

1. **Update PUBLIC_APP_URL**: Set this environment variable to your Vercel URL.

2. **Test All Features**:
   - Frontend loads correctly
   - API endpoints work
   - Blog generation completes
   - Static assets load

3. **Monitor Performance**:
   - Check Vercel dashboard for function execution times
   - Monitor error rates
   - Review logs for issues

## Custom Domain

To use a custom domain:

1. Go to Project Settings → Domains
2. Add your domain
3. Follow DNS configuration instructions
4. Update `PUBLIC_APP_URL` environment variable

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Support](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [FastAPI on Vercel](https://vercel.com/guides/deploying-fastapi-with-vercel)

---

**Note**: For long-running operations (like blog generation), consider:
- Using background jobs (Vercel Cron + Queue)
- Upgrading to Vercel Pro for longer timeouts
- Using a separate service for heavy processing
