#!/usr/bin/env python3
"""
Start script for Irado Chatbot Dashboard
"""

import os
import sys
import subprocess

def check_requirements():
    """Check if required packages are installed"""
    try:
        import flask
        import pandas
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def start_dashboard():
    """Start the dashboard"""
    print("🚀 Starting Irado Chatbot Dashboard...")
    print("=" * 50)
    print("Dashboard will be available at: http://localhost:3255")
    print("Press Ctrl+C to stop the dashboard")
    print("=" * 50)
    
    # Change to dashboard directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Start the dashboard
    from dashboard import app
    app.run(host='0.0.0.0', port=3255, debug=False)

if __name__ == "__main__":
    if check_requirements():
        start_dashboard()
    else:
        print("❌ Failed to install requirements")
        sys.exit(1)
