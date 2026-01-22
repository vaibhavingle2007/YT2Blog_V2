#!/usr/bin/env python3
"""
YouTube to Blog Converter Server Startup Script
Provides multiple ways to start the server with proper configuration.
"""

import os
import sys
import uvicorn
from pathlib import Path

def main():
    """Main function to start the FastAPI server"""
    
    # Keep working directory at project root for proper imports
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    
    # Ensure we're in the project root
    os.chdir(project_root)
    
    # Add the project root to Python path for imports
    sys.path.insert(0, str(project_root))
    
    # Avoid unicode emoji in Windows terminals that may not support it
    print("Starting YouTube to Blog Converter API Server...")
    print("Project root:", project_root)
    print("Backend directory:", backend_dir)
    print("Server will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")
    print("Hot reload enabled for development")
    print("-" * 50)
    
    try:
        # Start the server with proper configuration
        # Use backend.main:app since we're running from project root
        uvicorn.run(
            "backend.main:app",  # Proper import path from project root
            host="0.0.0.0",
            port=8000,
            reload=True,  # Enable hot reload for development
            reload_dirs=[str(project_root)],  # Watch for changes in project directory
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 