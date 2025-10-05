#!/usr/bin/env python3
"""
InSync Web Application Startup Script
Simple script to start the InSync web interface.
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import flask
        import flask_socketio
        import cv2
        import mediapipe
        import numpy
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Please install dependencies with: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if required environment variables are set."""
    required_vars = ['OPENAI_API_KEY']
    optional_vars = ['XI_API_KEY', 'XI_VOICE_ID']
    
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    if missing_required:
        print(f"❌ Missing required environment variables: {', '.join(missing_required)}")
        print("🔧 Please set these environment variables:")
        for var in missing_required:
            print(f"   export {var}=your_api_key_here")
        return False
    
    missing_optional = []
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_optional:
        print(f"⚠️  Optional environment variables not set: {', '.join(missing_optional)}")
        print("   TTS functionality will be limited without XI_API_KEY and XI_VOICE_ID")
    
    print("✅ Environment variables are properly configured")
    return True

def main():
    """Main startup function."""
    print("🚀 InSync Web Application Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Check environment
    if not check_environment():
        return 1
    
    print("\n🌐 Starting InSync Web Application...")
    print("📱 Open your browser to: http://localhost:5000")
    print("🎥 Camera interface: http://localhost:5000")
    print("⚙️  Gesture mappings: http://localhost:5000/mappings")
    print("\n💡 Press Ctrl+C to stop the application")
    print("=" * 50)
    
    try:
        # Import and run the web app
        from web_app import app, socketio
        socketio.run(app, debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 InSync Web Application stopped")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
