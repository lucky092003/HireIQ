#!/usr/bin/env python
"""
Simple server launcher for Mike Smart Match
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from app.main import app
    import uvicorn
    
    print("🚀 Starting Mike Smart Match Backend...")
    print("📡 API running at http://127.0.0.1:8000")
    print("📚 Docs at http://127.0.0.1:8000/docs")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )
