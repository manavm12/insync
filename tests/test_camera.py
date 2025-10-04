"""
Quick test script to verify camera connection and hand detection
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from hand_landmarks.camera_gesture_detection import RealTimeGestureDetector
from hand_landmarks.hand_landmarks_detector import HandLandmarksDetector

def test_camera_connection():
    """Test if camera can be accessed."""
    print("🧪 Testing camera connection...")
    
    try:
        detector = RealTimeGestureDetector(camera_id=0)
        print("✅ Camera connection successful!")
        
        # Quick capture test
        print("📸 Taking a quick capture...")
        landmarks = quick_capture()
        
        if landmarks:
            print("✅ Hand detection system working!")
            print(f"📊 Hands detected: {landmarks['landmarks']['hands_detected']}")
            
            if landmarks['landmarks']['hands_detected'] > 0:
                print("🎯 Sample landmark data:")
                hand = landmarks['landmarks']['hands'][0]
                print(f"   Handedness: {hand['handedness']}")
                print(f"   Confidence: {hand['handedness_confidence']:.3f}")
                print(f"   Wrist position: ({hand['landmarks'][0]['x']:.3f}, {hand['landmarks'][0]['y']:.3f})")
                
                if landmarks['gestures']:
                    print(f"   Detected gesture: {landmarks['gestures'][0]}")
            else:
                print("ℹ️  No hands detected in frame (try placing your hand in front of camera)")
        else:
            print("❌ Failed to capture from camera")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True


def simple_detection():
    """Run a simple detection session."""
    print("\n🎥 Starting simple detection session...")
    print("Show your hand to the camera and try different gestures!")
    
    try:
        detector = RealTimeGestureDetector()
        detector.start_detection(
            show_video=True,
            print_landmarks=True,
            save_to_file=False
        )
    except Exception as e:
        print(f"❌ Detection failed: {e}")


if __name__ == "__main__":
    print("🚀 Hand Gesture Detection - Camera Test")
    print("=" * 45)
    
    # Test camera first
    if test_camera_connection():
        print("\n" + "="*45)
        input("Press Enter to start live detection (or Ctrl+C to exit)...")
        simple_detection()
    else:
        print("\n❌ Camera test failed. Please check your camera connection.")
