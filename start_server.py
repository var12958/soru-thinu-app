#!/usr/bin/env python3
"""
Simple startup script for FoodSnap application
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get the directory where this script is located
    app_dir = Path(__file__).parent
    backend_dir = app_dir / "backend"
    
    print("🍕 Starting FoodSnap Application...")
    print(f"📁 App directory: {app_dir}")
    
    # Check if we're in the right directory
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        print("Make sure you're running this from the soru-thinu-app directory")
        return 1
    
    # Check if requirements are installed
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI dependencies found")
    except ImportError:
        print("❌ Missing dependencies!")
        print("Please install requirements:")
        print(f"pip install -r {backend_dir}/requirements.txt")
        return 1
    
    # Change to backend directory
    os.chdir(backend_dir)
    print(f"📂 Changed to: {os.getcwd()}")
    
    # Start the server
    print("🚀 Starting FastAPI server...")
    print("📱 Frontend will be available at: http://localhost:8080")
    print("🔗 API docs at: http://localhost:8080/docs")
    print("💬 Chat test at: http://localhost:8080/api/chat/test")
    print("\n⏹️  Press Ctrl+C to stop the server\n")
    
    try:
        # Run uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8080", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
        return 0
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())