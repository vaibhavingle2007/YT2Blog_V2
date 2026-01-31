from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Request
from pydantic import BaseModel, HttpUrl
import asyncio
from typing import Optional, Dict, Any
import sys
import os

# Add the parent directory to path to import utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from backend.youtube_service import YouTubeService
from backend.config import settings
from utils.blog_generator import BlogGenerator
from backend.auth_dependencies import require_firebase_user
from backend.credits_service import ensure_user_exists, get_credits, consume_credits
from backend.projects_service import save_project as save_project_fs, list_projects as list_projects_fs
from backend.billing_service import create_checkout_session, handle_webhook
from pathlib import Path

# Get project root directory (works in both local and Vercel environments)
PROJECT_ROOT = Path(parent_dir).resolve()

app = FastAPI(
    title=settings.APP_NAME, 
    version=settings.VERSION,
    description=settings.DESCRIPTION
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize services with configuration
youtube_service = YouTubeService(api_key=settings.YOUTUBE_API_KEY)
blog_generator = BlogGenerator()

# Mount static files (for serving frontend assets)
# Use absolute path for Vercel compatibility
public_dir = PROJECT_ROOT / "public"
if public_dir.exists():
    app.mount("/public", StaticFiles(directory=str(public_dir)), name="public")

class VideoRequest(BaseModel):
    url: HttpUrl
    template: str = "article"
    language: str = "en"
    fact_cleanup: bool = True
    humanize: bool = True
    # Deprecated. User identity is derived from Firebase ID token.
    user_id: Optional[str] = None

class VideoResponse(BaseModel):
    title: str
    description: str
    thumbnail: str
    duration: str
    views: str
    published_at: str
    channel_name: str
    video_id: str
    is_code_tutorial: bool = False

class BlogResponse(BaseModel):
    content: str
    template: str
    language: str
    word_count: int
    reading_time: int
    credits_used: int = 1
    credits_remaining: int = 4
    is_code_tutorial: bool = False

@app.get("/")
async def serve_frontend():
    """Serve the main frontend HTML file"""
    index_path = PROJECT_ROOT / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    else:
        raise HTTPException(status_code=404, detail="Frontend file not found")

@app.get("/pricing")
@app.get("/pricing.html")
async def serve_pricing():
    """Serve the pricing/upgrade page"""
    pricing_path = PROJECT_ROOT / "pricing.html"
    if pricing_path.exists():
        return FileResponse(str(pricing_path))
    else:
        raise HTTPException(status_code=404, detail="Pricing page not found")

@app.get("/features")
@app.get("/features.html")
async def serve_features():
    """Serve the features page"""
    features_path = PROJECT_ROOT / "features.html"
    if features_path.exists():
        return FileResponse(str(features_path))
    else:
        raise HTTPException(status_code=404, detail="Features page not found")

@app.get("/docs.html")
async def serve_docs_page():
    """Serve the documentation page"""
    docs_path = PROJECT_ROOT / "docs.html"
    if docs_path.exists():
        return FileResponse(str(docs_path))
    else:
        raise HTTPException(status_code=404, detail="Documentation page not found")

@app.get("/api/public-config")
async def public_config():
    """
    Public configuration for the frontend (safe values only).
    This avoids hardcoding Firebase keys into static HTML.
    """
    return {
        "firebase": {
            "apiKey": settings.FIREBASE_API_KEY,
            "authDomain": settings.FIREBASE_AUTH_DOMAIN,
            "projectId": settings.FIREBASE_PROJECT_ID,
            "storageBucket": settings.FIREBASE_STORAGE_BUCKET,
            "messagingSenderId": settings.FIREBASE_MESSAGING_SENDER_ID,
            "appId": settings.FIREBASE_APP_ID,
        },
        "billing": {
            "stripe_configured": settings.has_stripe,
            "public_app_url": settings.PUBLIC_APP_URL,
            "plans": [
                {"id": "free", "name": "Free", "daily_credits": 5},
                {"id": "starter", "name": "Starter", "daily_credits": 50},
                {"id": "pro", "name": "Pro", "daily_credits": 200},
            ],
        },
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "message": settings.APP_NAME, 
        "status": "active", 
        "version": settings.VERSION,
        "environment": "development" if settings.is_development else "production",
        "youtube_api_configured": settings.has_youtube_api,
        "nebius_api_configured": settings.has_nebius_api,
        "firebase_project_configured": settings.has_firebase_project,
        "firebase_admin_configured": settings.has_firebase_admin,
        "cors_origins": settings.CORS_ORIGINS
    }

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle CORS preflight requests"""
    return {"message": "OK"}

@app.post("/api/video-info", response_model=VideoResponse)
async def get_video_info(request: VideoRequest):
    """Extract video information from YouTube URL"""
    try:
        video_id = youtube_service.extract_video_id(str(request.url))
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        # Simulate API processing delay for better UX
        await asyncio.sleep(1)
        
        video_data = youtube_service.get_video_metadata(video_id)
        
        # Get transcript to detect if it's a code tutorial
        transcript = youtube_service.get_transcript(video_id)
        is_code_tutorial = blog_generator.detect_code_content(transcript) if transcript else False
        
        return VideoResponse(**video_data, is_code_tutorial=is_code_tutorial)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

@app.post("/api/generate-blog", response_model=BlogResponse)
async def generate_blog(request: VideoRequest, user: Dict[str, Any] = Depends(require_firebase_user)):
    """Generate blog content from video data"""
    if not blog_generator.llm_enabled:
        raise HTTPException(
            status_code=503, 
            detail="LLM Service Unavailable: NEBIUS_API_KEY is not configured on the server."
        )

    try:
        uid = user["uid"]
        ensure_user_exists(uid=uid, email=user.get("email"))

        # Consume credits first (fail fast if insufficient)
        try:
            credit_snapshot = consume_credits(uid, amount=1)
        except ValueError as e:
            if str(e) == "INSUFFICIENT_CREDITS":
                raise HTTPException(status_code=402, detail="Insufficient credits. Please upgrade.")
            raise

        video_id = youtube_service.extract_video_id(str(request.url))
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        # Simulate processing delay for better UX
        await asyncio.sleep(2)
        
        # Get video metadata and transcript
        video_data = youtube_service.get_video_metadata(video_id)
        transcript = youtube_service.get_transcript(video_id)
        
        # Detect if it's a code tutorial
        is_code_tutorial = blog_generator.detect_code_content(transcript) if transcript else False
        
        # Generate blog content with new features
        blog_content = blog_generator.generate_blog(
            video_data=video_data,
            template=request.template,
            transcript=transcript,
            language=request.language,
            fact_cleanup=request.fact_cleanup,
            humanize=request.humanize,
            is_code_tutorial=is_code_tutorial
        )
        
        # Calculate word count and reading time
        word_count = len(blog_content.split())
        reading_time = max(1, word_count // 200)  # Average reading speed: 200 words/minute
        
        return BlogResponse(
            content=blog_content,
            template=request.template,
            language=request.language,
            word_count=word_count,
            reading_time=reading_time,
            credits_used=1,
            credits_remaining=credit_snapshot.credits_remaining,
            is_code_tutorial=is_code_tutorial
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating blog: {str(e)}")

@app.get("/api/templates")
async def get_templates():
    """Get available blog templates"""
    return {
        "templates": [
            {
                "id": "article",
                "name": "Article",
                "description": "Standard blog article format with introduction, analysis, and conclusion"
            },
            {
                "id": "tutorial", 
                "name": "Tutorial",
                "description": "Step-by-step guide format with structured learning approach"
            },
            {
                "id": "review",
                "name": "Review", 
                "description": "Comprehensive review format with ratings and detailed analysis"
            },
            {
                "id": "summary",
                "name": "Summary",
                "description": "Concise summary format with key highlights and takeaways"
            }
        ]
    }

@app.get("/api/languages")
async def get_languages():
    """Get available output languages"""
    return {
        "languages": [
            {"code": "en", "name": "English", "flag": "🇺🇸"},
            {"code": "hi", "name": "Hindi", "flag": "🇮🇳"},
            {"code": "es", "name": "Spanish", "flag": "🇪🇸"},
            {"code": "fr", "name": "French", "flag": "🇫🇷"},
            {"code": "de", "name": "German", "flag": "🇩🇪"},
            {"code": "pt", "name": "Portuguese", "flag": "🇵🇹"},
            {"code": "ja", "name": "Japanese", "flag": "🇯🇵"},
            {"code": "ko", "name": "Korean", "flag": "🇰🇷"}
        ]
    }

@app.get("/api/me")
async def me(user: Dict[str, Any] = Depends(require_firebase_user)):
    uid = user["uid"]
    ensure_user_exists(uid=uid, email=user.get("email"))
    return {
        "uid": uid,
        "email": user.get("email"),
        "name": user.get("name"),
        "picture": user.get("picture"),
    }

@app.get("/api/me/credits")
async def my_credits(user: Dict[str, Any] = Depends(require_firebase_user)):
    """Get logged-in user's remaining credits"""
    uid = user["uid"]
    ensure_user_exists(uid=uid, email=user.get("email"))
    snap = get_credits(uid)
    return {
        "user_id": uid,
        "credits_remaining": snap.credits_remaining,
        "credits_total": snap.credits_total,
        "is_premium": snap.is_premium,
        "plan_id": snap.plan_id,
        "updated_at": snap.updated_at,
    }

@app.post("/api/billing/checkout")
async def billing_checkout(body: dict, user: Dict[str, Any] = Depends(require_firebase_user)):
    """
    Create Stripe Checkout Session for a plan.
    Body: { "plan_id": "starter" | "pro" }
    """
    plan_id = (body or {}).get("plan_id")
    if not plan_id:
        raise HTTPException(status_code=400, detail="Missing plan_id")
    try:
        url = create_checkout_session(user["uid"], plan_id=plan_id)
        # If Stripe is not configured, the plan is applied instantly and no URL is returned.
        return {"checkout_url": url, "applied": url is None}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid plan")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/billing/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    if not sig:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
    try:
        return handle_webhook(payload=payload, sig_header=sig)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Backward-compatible route (deprecated): keep existing path but require auth and ignore user_id
@app.get("/api/credits/{user_id}")
async def get_user_credits_deprecated(user_id: str, user: Dict[str, Any] = Depends(require_firebase_user)):
    return await my_credits(user)

@app.get("/api/me/projects")
async def my_projects(user: Dict[str, Any] = Depends(require_firebase_user)):
    """Get logged-in user's saved projects"""
    uid = user["uid"]
    ensure_user_exists(uid=uid, email=user.get("email"))
    projects = list_projects_fs(uid)
    return {"projects": projects}

@app.post("/api/me/projects")
async def save_my_project(project_data: dict, user: Dict[str, Any] = Depends(require_firebase_user)):
    """Save a project for later access (scoped to logged-in user)"""
    uid = user["uid"]
    ensure_user_exists(uid=uid, email=user.get("email"))
    project_id = save_project_fs(uid, project_data)
    return {"project_id": project_id, "message": "Project saved successfully"}

# Backward-compatible routes (deprecated): keep existing paths but require auth and ignore user_id
@app.post("/api/projects")
async def save_project_deprecated(project_data: dict, user: Dict[str, Any] = Depends(require_firebase_user)):
    return await save_my_project(project_data, user)

@app.get("/api/projects/{user_id}")
async def get_user_projects_deprecated(user_id: str, user: Dict[str, Any] = Depends(require_firebase_user)):
    return await my_projects(user)

@app.get("/api/health")
async def health_check():
    """Detailed health check endpoint"""
    try:
        return {
            "status": "healthy",
            "services": {
                "youtube_service": "operational",
                "blog_generator": "operational" if blog_generator.llm_enabled else "degraded"
            },
            "api_version": "2.0.0",
            "features": [
                "multi_language_support",
                "fact_cleanup_mode", 
                "humanize_output",
                "code_detection",
                "project_workspace",
                "credit_system"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    print(f"🚀 Starting {settings.APP_NAME} v{settings.VERSION}")
    print(f"🌐 Server: http://{settings.HOST}:{settings.PORT}")
    print(f"📖 API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🔧 Environment: {'Development' if settings.is_development else 'Production'}")
    print(f"🔑 YouTube API: {'✅ Configured' if settings.has_youtube_api else '❌ Not configured (using PyTube fallback)'}")
    
    # Use proper configuration for uvicorn
    uvicorn.run(
        "main:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.is_development,
        log_level="debug" if settings.is_development else "info"
    )