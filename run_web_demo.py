#!/usr/bin/env python3
"""
Launcher script for the Mortgage Web Demo
"""
import subprocess
import sys
import os

def main():
    """Launch the Streamlit web application."""
    try:
        # Check if streamlit is installed
        import streamlit
        print("✅ Streamlit is installed")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "pandas"])
    
    # Launch the web app
    print("🚀 Starting Mortgage Web Demo...")
    print("📱 The app will open in your browser at http://localhost:8501")
    print("🔄 Press Ctrl+C to stop the server")
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "mortgage_web_demo.py",
        "--server.port=8501",
        "--server.address=localhost"
    ])

if __name__ == "__main__":
    main() 
    