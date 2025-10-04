"""
Test script to demonstrate getting all 21 hand landmarks
"""

from camera_gesture_detection import RealTimeGestureDetector
import json
import time


def test_all_landmarks():
    """Test getting all 21 landmarks from camera."""
    print("🎯 Testing All 21 Hand Landmarks")
    print("=" * 40)
    print("Place your hand in front of the camera...")
    print("Press Ctrl+C to stop")
    
    detector = RealTimeGestureDetector()
    
    try:
        while True:
            # Get all landmarks in formatted structure
            landmarks = detector.get_all_landmarks_formatted()
            
            if landmarks:
                print(f"\n📊 Timestamp: {time.strftime('%H:%M:%S', time.localtime(landmarks['timestamp']))}")
                print(f"🖐️  Hands detected: {landmarks['hands_count']}")
                
                for i, hand in enumerate(landmarks['hands']):
                    print(f"\n   Hand {i+1}: {hand['handedness']} (confidence: {hand['confidence']:.3f})")
                    print(f"   Gesture: {hand['gesture']}")
                    print(f"   All 21 Landmarks:")
                    
                    # Print all landmarks with their names
                    for landmark_name, coords in hand['landmarks'].items():
                        print(f"      {coords['id']:2d} - {landmark_name:18s}: x={coords['x']:.4f}, y={coords['y']:.4f}, z={coords['z']:.4f}")
                
                print("-" * 80)
            else:
                print("❌ No hands detected")
            
            time.sleep(0.5)  # Update every 0.5 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
    finally:
        detector._cleanup()


def save_landmarks_sample():
    """Capture and save a sample of all landmarks to JSON file."""
    print("\n💾 Capturing landmarks sample...")
    
    detector = RealTimeGestureDetector()
    landmarks = detector.get_all_landmarks_formatted()
    
    if landmarks:
        filename = f"all_landmarks_sample_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(landmarks, f, indent=2)
        
        print(f"✅ Sample saved to: {filename}")
        
        # Also print to console
        print("\n📋 Sample Data:")
        print(json.dumps(landmarks, indent=2))
    else:
        print("❌ No hands detected for sample")
    
    detector._cleanup()


def print_landmark_reference():
    """Print reference of all 21 landmark names and IDs."""
    print("\n📚 Hand Landmark Reference (21 points):")
    print("=" * 50)
    
    landmark_names = [
        'WRIST', 'THUMB_CMC', 'THUMB_MCP', 'THUMB_IP', 'THUMB_TIP',
        'INDEX_FINGER_MCP', 'INDEX_FINGER_PIP', 'INDEX_FINGER_DIP', 'INDEX_FINGER_TIP',
        'MIDDLE_FINGER_MCP', 'MIDDLE_FINGER_PIP', 'MIDDLE_FINGER_DIP', 'MIDDLE_FINGER_TIP',
        'RING_FINGER_MCP', 'RING_FINGER_PIP', 'RING_FINGER_DIP', 'RING_FINGER_TIP',
        'PINKY_MCP', 'PINKY_PIP', 'PINKY_DIP', 'PINKY_TIP'
    ]
    
    for i, name in enumerate(landmark_names):
        print(f"   {i:2d} - {name}")
    
    print("\nLegend:")
    print("   CMC = Carpometacarpal joint")
    print("   MCP = Metacarpophalangeal joint") 
    print("   PIP = Proximal interphalangeal joint")
    print("   DIP = Distal interphalangeal joint")
    print("   IP  = Interphalangeal joint (thumb)")
    print("   TIP = Fingertip")


if __name__ == "__main__":
    print("🚀 Hand Landmarks - All 21 Points Test")
    print("=" * 45)
    
    while True:
        print("\nChoose an option:")
        print("1. Live test - Show all 21 landmarks in real-time")
        print("2. Capture sample - Save current landmarks to JSON")
        print("3. Show landmark reference - List all 21 landmark names")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-3): ").strip()
        
        if choice == '0':
            print("Goodbye! 👋")
            break
        elif choice == '1':
            test_all_landmarks()
        elif choice == '2':
            save_landmarks_sample()
        elif choice == '3':
            print_landmark_reference()
        else:
            print("Invalid choice. Please try again.")
