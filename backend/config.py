"""
Configuration settings for the YouTube to Blog Converter API
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

# Find the project root directory (where .env should be)
current_dir = Path(__file__).parent  # backend directory
project_root = current_dir.parent    # project root directory

# Load environment variables from project root
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    """Application settings"""
    
    # Server configuration
    HOST: str = os.getenv("HOST", "localhost")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # API Keys
    YOUTUBE_API_KEY: Optional[str] = os.getenv("YOUTUBE_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    NEBIUS_API_KEY: Optional[str] = os.getenv("NEBIUS_API_KEY")

    # Firebase (frontend config - used to render pricing/login pages if needed)
    FIREBASE_API_KEY: Optional[str] = os.getenv("FIREBASE_API_KEY")
    FIREBASE_AUTH_DOMAIN: Optional[str] = os.getenv("FIREBASE_AUTH_DOMAIN")
    FIREBASE_PROJECT_ID: Optional[str] = os.getenv("FIREBASE_PROJECT_ID")
    FIREBASE_STORAGE_BUCKET: Optional[str] = os.getenv("FIREBASE_STORAGE_BUCKET")
    FIREBASE_MESSAGING_SENDER_ID: Optional[str] = os.getenv("FIREBASE_MESSAGING_SENDER_ID")
    FIREBASE_APP_ID: Optional[str] = os.getenv("FIREBASE_APP_ID")

    # Firebase Admin
    FIREBASE_SERVICE_ACCOUNT_JSON: Optional[str] = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    FIREBASE_SERVICE_ACCOUNT_PATH: Optional[str] = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")

    # Stripe Billing (optional)
    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
    PUBLIC_APP_URL: str = os.getenv("PUBLIC_APP_URL", f"http://{os.getenv('HOST','localhost')}:{os.getenv('PORT','8000')}")
    STRIPE_PRICE_STARTER: Optional[str] = os.getenv("STRIPE_PRICE_STARTER")
    STRIPE_PRICE_PRO: Optional[str] = os.getenv("STRIPE_PRICE_PRO")
    
    # CORS settings
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000",
        "https://ytblogs.netlify.app",
        "https://*.netlify.app",
        "https://*.vercel.app",
        "*"  # Allow all origins for development (remove in production)
    ]
    
    # Application metadata
    APP_NAME: str = "YouTube to Blog Converter API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Convert YouTube videos into well-structured blog posts"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.DEBUG
    
    @property
    def has_youtube_api(self) -> bool:
        """Check if YouTube API key is configured"""
        return self.YOUTUBE_API_KEY is not None and len(self.YOUTUBE_API_KEY.strip()) > 0
    
    @property
    def has_openai_api(self) -> bool:
        """Check if OpenAI API key is configured"""
        return self.OPENAI_API_KEY is not None and len(self.OPENAI_API_KEY.strip()) > 0

    @property
    def has_nebius_api(self) -> bool:
        """Check if Nebius API key is configured"""
        return self.NEBIUS_API_KEY is not None and len(self.NEBIUS_API_KEY.strip()) > 0

    @property
    def has_firebase_project(self) -> bool:
        """Check if Firebase project is configured"""
        return self.FIREBASE_PROJECT_ID is not None and len(self.FIREBASE_PROJECT_ID.strip()) > 0

    @property
    def has_firebase_admin(self) -> bool:
        """Check if Firebase Admin credentials are configured"""
        if self.FIREBASE_SERVICE_ACCOUNT_JSON and self.FIREBASE_SERVICE_ACCOUNT_JSON.strip():
            return True
        if self.FIREBASE_SERVICE_ACCOUNT_PATH and self.FIREBASE_SERVICE_ACCOUNT_PATH.strip():
            return True
        return False

    @property
    def has_stripe(self) -> bool:
        """Check if Stripe is configured"""
        return self.STRIPE_SECRET_KEY is not None and len(self.STRIPE_SECRET_KEY.strip()) > 0

# Global settings instance
settings = Settings() 