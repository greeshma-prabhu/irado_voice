#!/usr/bin/env python3
"""
Startup script for the Irado Chatbot
"""
import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import flask
        import openai
        import psycopg2
        import dotenv
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    env_file = Path('.env')
    if not env_file.exists():
        print("✗ .env file not found")
        print("Please copy .env.example to .env and configure your settings")
        return False
    print("✓ .env file found")
    return True

def check_database_connection():
    """Check database connection"""
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        conn = db.get_connection()
        conn.close()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("Please check your PostgreSQL configuration")
        return False

def main():
    """Main startup function"""
    print("Starting Irado Chatbot...")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment file
    if not check_env_file():
        sys.exit(1)
    
    # Check database connection
    if not check_database_connection():
        sys.exit(1)
    
    print("=" * 50)
    print("All checks passed! Starting chatbot server...")
    print("=" * 50)
    
    # Start the Flask application
    try:
        from app import app, init_app
        init_app()
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()



