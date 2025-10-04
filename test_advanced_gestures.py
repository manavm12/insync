"""
Test script for advanced gesture recognition
Demonstrates the new gesture detection capabilities including thumbs up/down, numbers, etc.
"""

from camera_gesture_detection import RealTimeGestureDetector
from gesture_recognition import GestureRecognizer, recognize_advanced_gestures
import time


def test_advanced_gestures():
    """Test the advanced gesture recognition system."""
    print("🎯 Advanced Gesture Recognition Test")
    print("=" * 45)
    print("Show different gestures to test the recognition:")
    print("• Thumbs Up / Thumbs Down")
    print("• Numbers 0-5 (finger counting)")
    print("• Peace Sign / Victory")
    print("• Pointing / One Finger Up")
    print("• Open Hand / Closed Fist")
    print("• Gun gesture (thumb + index)")
    print("• Call Me gesture (thumb + pinky)")
    print("")
    print("Press Ctrl+C to stop")
    print("=" * 45)
    
    detector = RealTimeGestureDetector()
    
    try:
        while True:
            # Get current landmarks
            landmarks_data = detector.get_current_landmarks()
            
            if landmarks_data and landmarks_data['landmarks']['hands_detected'] > 0:
                # Get gesture data
                gesture_data = detector.detector.get_gesture_landmarks(
                    detector.cap.read()[1] if detector.cap else None
                )
                
                if gesture_data['hands_count'] > 0:
                    # Use advanced recognition
                    advanced_results = recognize_advanced_gestures(gesture_data)
                    
                    print(f"\n🕐 {time.strftime('%H:%M:%S')}")
                    print(f"👋 Hands detected: {len(advanced_results)}")
                    
                    for i, result in enumerate(advanced_results):
                        print(f"\n   🖐️  Hand {i+1} ({result['handedness']}):")
                        print(f"      🎯 Gesture: {result['gesture']}")
                        
                        if result['number'] is not None:
                            print(f"      🔢 Number: {result['number']}")
                        
                        # Show finger states
                        finger_states = result['finger_states']
                        fingers_up = finger_states['fingers_up']
                        finger_names = finger_states['finger_names']
                        
                        fingers_display = []
                        for name, up in zip(finger_names, fingers_up):
                            fingers_display.append(f"{name}{'✅' if up else '❌'}")
                        
                        print(f"      ✋ Fingers: {' | '.join(fingers_display)}")
                        print(f"      📊 Count: {finger_states['fingers_count']}/5")
                        
                        # Show orientation
                        orientation = result['orientation']
                        print(f"      📐 Angle: {orientation['hand_angle']:.1f}°")
                
                print("-" * 60)
            else:
                print("❌ No hands detected - show your hand to the camera")
            
            time.sleep(0.8)  # Update every 0.8 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
    finally:
        detector._cleanup()


def test_specific_gestures():
    """Test recognition of specific gestures with prompts."""
    gestures_to_test = [
        "Thumbs Up",
        "Thumbs Down", 
        "Peace Sign (Index + Middle fingers)",
        "Number 1 (Index finger only)",
        "Number 2 (Index + Middle)",
        "Number 3 (Index + Middle + Ring)",
        "Number 4 (All except thumb)",
        "Number 5 (All fingers)",
        "Closed Fist",
        "Open Hand",
        "Pointing (Index finger)",
        "Gun gesture (Thumb + Index)",
        "Call Me (Thumb + Pinky)"
    ]
    
    print("🎯 Specific Gesture Recognition Test")
    print("=" * 50)
    print("Follow the prompts to test specific gestures")
    print("")
    
    detector = RealTimeGestureDetector()
    
    for gesture_name in gestures_to_test:
        print(f"\n👉 Please show: {gesture_name}")
        print("   Press Enter when ready, or 's' to skip...")
        
        user_input = input().strip().lower()
        if user_input == 's':
            continue
        
        print("   Analyzing gesture...")
        
        # Capture and analyze
        landmarks_data = detector.get_current_landmarks()
        
        if landmarks_data and landmarks_data['landmarks']['hands_detected'] > 0:
            gesture_data = detector.detector.get_gesture_landmarks(
                detector.cap.read()[1] if detector.cap else None
            )
            
            if gesture_data['hands_count'] > 0:
                advanced_results = recognize_advanced_gestures(gesture_data)
                
                for result in advanced_results:
                    detected_gesture = result['gesture']
                    confidence = result['confidence']
                    
                    print(f"   ✅ Detected: {detected_gesture}")
                    print(f"   📊 Confidence: {confidence:.3f}")
                    
                    if result['number'] is not None:
                        print(f"   🔢 Number: {result['number']}")
                    
                    # Check if it matches what we asked for
                    if gesture_name.lower() in detected_gesture.lower():
                        print("   🎉 CORRECT MATCH!")
                    else:
                        print("   ⚠️  Different gesture detected")
            else:
                print("   ❌ No hands detected")
        else:
            print("   ❌ Failed to capture")
        
        print("-" * 30)
    
    detector._cleanup()
    print("\n✅ Specific gesture test completed!")


if __name__ == "__main__":
    print("🚀 Advanced Gesture Recognition Testing")
    print("=" * 50)
    
    while True:
        print("\nChoose a test:")
        print("1. Continuous gesture recognition")
        print("2. Specific gesture testing")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-2): ").strip()
        
        if choice == '0':
            print("Goodbye! 👋")
            break
        elif choice == '1':
            test_advanced_gestures()
        elif choice == '2':
            test_specific_gestures()
        else:
            print("Invalid choice. Please try again.")
