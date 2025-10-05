#!/usr/bin/env python3
"""
InSync Web Application Demo
This script demonstrates the web application functionality.
"""

import os
import sys
import time
import threading
import webbrowser
from pathlib import Path

def check_environment():
    """Check if environment is properly set up."""
    print("🔍 Checking environment setup...")
    
    # Check if we're in the right directory
    if not Path("web_app.py").exists():
        print("❌ web_app.py not found. Please run this from the InSync project root.")
        return False
    
    # Check if templates exist
    if not Path("templates").exists():
        print("❌ templates directory not found.")
        return False
    
    # Check environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set. Translation will not work.")
        print("   Set it with: export OPENAI_API_KEY='your_key_here'")
    else:
        print("✅ OPENAI_API_KEY is set")
    
    if not os.getenv("XI_API_KEY"):
        print("⚠️  XI_API_KEY not set. TTS will not work.")
        print("   Set it with: export XI_API_KEY='your_key_here'")
    else:
        print("✅ XI_API_KEY is set")
    
    return True

def start_web_app():
    """Start the web application in a separate thread."""
    print("🚀 Starting InSync Web Application...")
    
    try:
        from web_app import app, socketio
        socketio.run(app, debug=False, host='127.0.0.1', port=5000, log_output=False)
    except Exception as e:
        print(f"❌ Error starting web app: {e}")
        return False
    
    return True

def open_browser():
    """Open the web application in the default browser."""
    time.sleep(2)  # Wait for server to start
    print("🌐 Opening browser...")
    webbrowser.open("http://localhost:5000")

def main():
    """Main demo function."""
    print("🤟 InSync Web Application Demo")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        return 1
    
    print("\n📋 Demo Instructions:")
    print("1. The web application will start on http://localhost:5000")
    print("2. Your browser will open automatically")
    print("3. Click '🎥 Start Camera' to begin gesture detection")
    print("4. Perform gestures in front of your camera")
    print("5. Watch the real-time translation and TTS")
    print("6. Visit http://localhost:5000/mappings to create custom mappings")
    print("\n💡 Press Ctrl+C to stop the demo")
    print("=" * 50)
    
    # Start browser in separate thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    try:
        # Start web app (this will block)
        start_web_app()
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
