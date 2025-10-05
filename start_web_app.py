#!/usr/bin/env python3
"""
Startup script for the Hand Gesture Detection Web Application
This script handles environment setup and starts the Flask web server.
"""

import sys
import os
import subprocess

def check_and_install_dependencies():
    """Check if required packages are installed, install if missing."""
    required_packages = ['flask', 'flask-cors']
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is already installed")
        except ImportError:
            print(f"❌ {package} not found, installing...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package}: {e}")
                return False
    
    return True

def main():
    """Main startup function."""
    print("🚀 Hand Gesture Detection Web Application")
    print("=" * 50)
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_and_install_dependencies():
        print("❌ Failed to install required dependencies")
        return 1
    
    # Import and start the web application
    try:
        from web_app import app
        print("\n🌐 Starting Flask web server...")
        print("📱 Open http://localhost:3000 in your browser")
        print("🛑 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        app.run(host='0.0.0.0', port=3000, debug=False, threaded=True)
        
    except ImportError as e:
        print(f"❌ Failed to import web application: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Web server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error starting web server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
