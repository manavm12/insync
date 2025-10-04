#!/usr/bin/env python3
"""
Test Face Tracking for ASL Recognition

This script demonstrates the enhanced ASL recognition with face reference points.
It shows how signs like THANK YOU can be detected based on hand proximity to the mouth.
"""

import sys
import os
import cv2

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hand_landmarks import HolisticDetector, recognize_advanced_gestures


def main():
    """Test face tracking with holistic detector."""
    print("=" * 70)
    print("🤟 ASL Face Tracking Test")
    print("=" * 70)
    print()
    print("This demo shows face tracking for improved ASL recognition:")
    print("  • Face reference points are tracked (nose, mouth, chin, forehead)")
    print("  • Hand distance to face points is calculated")
    print("  • Signs like THANK YOU can be detected based on proximity to mouth")
    print()
    print("Try these gestures:")
    print("  1. Open hand near mouth → Should detect 'THANK YOU'")
    print("  2. Open hand near chest → Should detect 'PLEASE'")
    print("  3. Open hand raised → Should detect 'HELLO'")
    print()
    print("Controls:")
    print("  'q' - Quit")
    print("  's' - Take screenshot")
    print("=" * 70)
    print()
    
    # Initialize holistic detector
    detector = HolisticDetector(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # Open camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Could not open camera!")
        return
    
    print("✅ Camera opened successfully!")
    print("📹 Starting detection...\n")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Detect landmarks
            results = detector.detect_landmarks_image(frame)
            
            # Get gesture data
            gesture_data = detector.get_gesture_landmarks(frame)
            
            # Recognize gestures with face reference
            gestures = recognize_advanced_gestures(gesture_data)
            
            # Draw landmarks and reference points
            annotated_frame = detector.draw_landmarks(frame, results)
            
            # Add gesture information
            y_offset = 30
            if results['face_detected']:
                cv2.putText(annotated_frame, "Face Tracked: YES", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, (0, 255, 0), 2)
                y_offset += 30
            else:
                cv2.putText(annotated_frame, "Face Tracked: NO", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, (0, 0, 255), 2)
                y_offset += 30
            
            cv2.putText(annotated_frame, f"Hands: {results['hands_detected']}", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (255, 255, 0), 2)
            y_offset += 40
            
            # Display gestures
            for i, gesture in enumerate(gestures):
                gesture_text = f"Hand {i+1}: {gesture['gesture']}"
                color = (0, 255, 255) if 'THANK YOU' in gesture['gesture'] or 'PLEASE' in gesture['gesture'] else (255, 255, 255)
                cv2.putText(annotated_frame, gesture_text,
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                           0.6, color, 2)
                y_offset += 25
                
                # Show if face detection helped
                if gesture.get('face_detected'):
                    cv2.putText(annotated_frame, "  (with face tracking)",
                               (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                               0.5, (0, 255, 255), 1)
                    y_offset += 25
            
            # Add instructions
            cv2.putText(annotated_frame, "Press 'q' to quit, 's' to screenshot",
                       (10, annotated_frame.shape[0] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Show the frame
            cv2.imshow('ASL Face Tracking Test', annotated_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"asl_face_tracking_{int(cv2.getTickCount())}.jpg"
                cv2.imwrite(filename, annotated_frame)
                print(f"📸 Screenshot saved: {filename}")
    
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\n✨ Face tracking test completed!")


if __name__ == "__main__":
    main()

