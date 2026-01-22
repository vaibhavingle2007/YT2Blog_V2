#!/usr/bin/env python3
"""
Root level entry point for Railway deployment
"""

import os
import sys
from pathlib import Path

# Add project directories to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

# Import and run the start script
from start import main

if __name__ == "__main__":
    main() 