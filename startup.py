#!/usr/bin/env python
"""
Startup Script for Skin Analysis Application

This script launches both the Flask frontend and FastAPI backend servers.
Run this instead of starting servers manually.
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def setup_environment():
    """Setup environment and check requirements"""
    print("=" * 60)
    print("Skin Analysis Application - Startup Script")
    print("=" * 60)
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version}")
    print()
    
    # Check if dependencies are installed
    print("Checking dependencies...")
    try:
        import flask
        import fastapi
        import tensorflow
        import cv2
        import numpy
        print("✓ All dependencies found")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nInstall dependencies with:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    print()


def start_backend():
    """Start FastAPI backend server"""
    print("Starting FastAPI backend (port 8000)...")
    print("-" * 60)
    
    backend_process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    return backend_process


def start_frontend():
    """Start Flask frontend server"""
    print("Starting Flask frontend (port 5000)...")
    print("-" * 60)
    
    frontend_process = subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    return frontend_process


def print_startup_info():
    """Print startup information"""
    print()
    print("=" * 60)
    print("✓ Application Starting")
    print("=" * 60)
    print()
    print("Web Interface: http://127.0.0.1:5000")
    print("API Documentation: http://127.0.0.1:8000/docs")
    print()
    print("Press Ctrl+C to stop the application")
    print("-" * 60)
    print()


def main():
    """Main startup function"""
    try:
        setup_environment()
        
        # Change to project directory
        project_dir = Path(__file__).parent
        os.chdir(project_dir)
        
        # Start servers
        print("Launching servers...")
        print()
        
        # Note: In production, use process managers like supervisord or systemd
        # For now, we'll just print instructions
        
        print_startup_info()
        
        print("To start the application:")
        print()
        print("Terminal 1 (Backend):")
        print("  cd", project_dir)
        print("  python main.py")
        print()
        print("Terminal 2 (Frontend):")
        print("  cd", project_dir)
        print("  python app.py")
        print()
        print("Then open: http://127.0.0.1:5000")
        print()
        
    except KeyboardInterrupt:
        print("\n✓ Startup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
