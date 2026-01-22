"""
Vercel serverless function entry point for FastAPI application
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

# Import the FastAPI app
from backend.main import app

# Vercel's @vercel/python automatically detects FastAPI apps
# The app is exported as the default handler
