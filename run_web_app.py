#!/usr/bin/env python3
"""
InSync Web Application Runner
Simple script to run the web app on a specified port.
"""

import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description='Run InSync Web Application')
    parser.add_argument('--port', type=int, default=5001, help='Port to run on (default: 5001)')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    args = parser.parse_args()
    
    print("🚀 InSync Web Application")
    print("=" * 40)
    print(f"📱 Open your browser to: http://{args.host}:{args.port}")
    print(f"🎥 Camera interface: http://{args.host}:{args.port}")
    print(f"⚙️  Gesture mappings: http://{args.host}:{args.port}/mappings")
    print("💡 Press Ctrl+C to stop the application")
    print("=" * 40)
    
    try:
        from web_app import app, socketio
        socketio.run(app, debug=False, host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\n👋 InSync Web Application stopped")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
