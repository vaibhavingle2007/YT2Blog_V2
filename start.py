#!/usr/bin/env python3
"""
Production startup script for YouTube to Blog Converter
"""

import os
import sys
import uvicorn
from pathlib import Path

def main():
    """Start the FastAPI server in production mode"""
    
    # Get port from environment (Railway sets this)
    port = int(os.environ.get("PORT", 8000))
    
    # Ensure we're in the project root directory
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    # Add both project root and backend to Python path
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "backend"))
    
    print(f"🚀 Starting YouTube to Blog Converter API Server on port {port}...")
    print(f"📂 Working directory: {os.getcwd()}")
    print(f"🐍 Python path: {sys.path[:3]}")
    
    try:
        # Start the server in production mode
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=port,
            workers=1,  # Single worker for hobby plans
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("🔍 Trying alternative import...")
        try:
            # Alternative approach - change to backend directory
            os.chdir(project_root / "backend")
            uvicorn.run(
                "main:app",
                host="0.0.0.0",
                port=port,
                workers=1,
                log_level="info"
            )
        except Exception as e2:
            print(f"❌ Alternative start also failed: {e2}")
            sys.exit(1)

if __name__ == "__main__":
    main() 