#!/bin/bash

# Activation script for hand detection environment
echo "🚀 Activating Hand Detection Environment"
echo "========================================"

# Activate virtual environment
source hand_detection_env/bin/activate

echo "✅ Virtual environment activated!"
echo "📦 Installed packages:"
pip list | grep -E "(mediapipe|opencv|numpy)"

echo ""
echo "🎯 Ready to run hand detection!"
echo ""
echo "Available commands:"
echo "  python test_camera.py           - Test camera and basic detection"
echo "  python camera_gesture_detection.py  - Full real-time detection"
echo "  python example_usage.py        - Interactive examples menu"
echo ""
echo "💡 Note: You may need to grant camera permissions when prompted by macOS"
echo ""

# Keep shell active
exec "$SHELL"
