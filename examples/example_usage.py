"""
Example usage of the Hand Landmarks Detector

This script demonstrates various ways to use the HandLandmarksDetector class:
1. Detecting landmarks in a single image
2. Processing a video file
3. Real-time detection from webcam
4. Basic gesture recognition
"""

import cv2
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from hand_landmarks.hand_landmarks_detector import HandLandmarksDetector, recognize_basic_gestures
import json


def example_image_detection():
    """Example: Detect hand landmarks in a single image."""
    print("=== Image Detection Example ===")
    
    # Initialize detector
    detector = HandLandmarksDetector(
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    
    # Create a sample image or load from file
    # For demo purposes, we'll create a blank image
    # In practice, you would load: image = cv2.imread('path/to/your/image.jpg')
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(image, "Place your hand in front of camera", (50, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Detect landmarks
    results = detector.detect_landmarks_image(image)
    
    # Print results
    print(f"Hands detected: {results['hands_detected']}")
    for i, hand in enumerate(results['hands']):
        print(f"\nHand {i}:")
        print(f"  Handedness: {hand['handedness']} (confidence: {hand['handedness_confidence']:.3f})")
        print(f"  Number of landmarks: {len(hand['landmarks'])}")
        
        # Print first few landmarks as example
        print("  First 5 landmarks:")
        for j in range(min(5, len(hand['landmarks']))):
            landmark = hand['landmarks'][j]
            print(f"    {landmark['name']}: x={landmark['x']:.3f}, y={landmark['y']:.3f}, z={landmark['z']:.3f}")
    
    # Draw landmarks and save result
    annotated_image = detector.draw_landmarks(image, results)
    cv2.imwrite('example_output.jpg', annotated_image)
    print("\nAnnotated image saved as 'example_output.jpg'")


def example_video_processing():
    """Example: Process a video file (requires an actual video file)."""
    print("\n=== Video Processing Example ===")
    
    # Note: This example requires an actual video file
    video_path = "sample_video.mp4"  # Replace with your video path
    
    try:
        detector = HandLandmarksDetector()
        
        # Process video
        results_list = detector.detect_landmarks_video(
            video_path=video_path,
            output_path="output_with_landmarks.mp4"
        )
        
        print(f"Processed {len(results_list)} frames")
        
        # Analyze results
        hands_detected_frames = sum(1 for r in results_list if r['hands_detected'] > 0)
        print(f"Hands detected in {hands_detected_frames} frames")
        
    except ValueError as e:
        print(f"Video processing skipped: {e}")
        print("To test video processing, provide a valid video file path")


def example_live_detection():
    """Example: Real-time hand detection from webcam."""
    print("\n=== Live Detection Example ===")
    print("This will open your webcam for real-time hand detection.")
    print("Press 'q' to quit, 's' to save current landmarks")
    
    try:
        detector = HandLandmarksDetector(
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Start live detection
        detector.detect_landmarks_live(camera_id=0, show_window=True)
        
    except ValueError as e:
        print(f"Live detection failed: {e}")
        print("Make sure your camera is connected and not being used by another application")


def example_gesture_recognition():
    """Example: Basic gesture recognition."""
    print("\n=== Gesture Recognition Example ===")
    
    detector = HandLandmarksDetector()
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Could not open camera for gesture recognition demo")
        return
    
    print("Gesture Recognition Demo")
    print("Show different hand gestures to the camera")
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Get gesture landmarks
        gesture_data = detector.get_gesture_landmarks(frame)
        
        # Recognize gestures
        gestures = recognize_basic_gestures(gesture_data)
        
        # Draw landmarks
        results = detector.detect_landmarks_image(frame)
        annotated_frame = detector.draw_landmarks(frame, results)
        
        # Display gesture information
        y_offset = 30
        cv2.putText(annotated_frame, f"Hands: {gesture_data['hands_count']}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        for i, gesture in enumerate(gestures):
            y_offset += 40
            cv2.putText(annotated_frame, f"Gesture {i+1}: {gesture}", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        
        cv2.imshow('Gesture Recognition', annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


def example_landmark_analysis():
    """Example: Detailed landmark analysis."""
    print("\n=== Landmark Analysis Example ===")
    
    detector = HandLandmarksDetector()
    
    # Create or load an image
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Could not open camera for landmark analysis")
        return
    
    print("Landmark Analysis Demo")
    print("Press SPACE to analyze current frame, 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        
        # Show live feed
        cv2.putText(frame, "Press SPACE to analyze landmarks", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow('Landmark Analysis', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):  # Space key
            # Analyze current frame
            results = detector.detect_landmarks_image(frame)
            
            if results['hands_detected'] > 0:
                print(f"\n--- Analysis Results ---")
                print(f"Hands detected: {results['hands_detected']}")
                
                for hand_idx, hand in enumerate(results['hands']):
                    print(f"\nHand {hand_idx} ({hand['handedness']}):")
                    print(f"Confidence: {hand['handedness_confidence']:.3f}")
                    
                    # Calculate some interesting metrics
                    landmarks = hand['landmarks']
                    
                    # Distance from wrist to middle finger tip
                    wrist = landmarks[0]
                    middle_tip = landmarks[12]
                    hand_length = np.sqrt(
                        (middle_tip['x'] - wrist['x'])**2 + 
                        (middle_tip['y'] - wrist['y'])**2
                    )
                    print(f"Hand length (normalized): {hand_length:.3f}")
                    
                    # Finger tip positions
                    finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
                    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
                    
                    print("Finger tip positions (normalized):")
                    for tip_idx, name in zip(finger_tips, finger_names):
                        tip = landmarks[tip_idx]
                        print(f"  {name}: ({tip['x']:.3f}, {tip['y']:.3f}, {tip['z']:.3f})")
                
                # Save detailed results to JSON
                with open('landmark_analysis.json', 'w') as f:
                    json.dump(results, f, indent=2)
                print("\nDetailed results saved to 'landmark_analysis.json'")
                
            else:
                print("No hands detected in current frame")
    
    cap.release()
    cv2.destroyAllWindows()


def main():
    """Main function to run all examples."""
    print("Hand Landmarks Detection Examples")
    print("=" * 40)
    
    while True:
        print("\nChoose an example to run:")
        print("1. Image Detection")
        print("2. Video Processing")
        print("3. Live Detection")
        print("4. Gesture Recognition")
        print("5. Landmark Analysis")
        print("6. Run All Examples")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == '0':
            print("Goodbye!")
            break
        elif choice == '1':
            example_image_detection()
        elif choice == '2':
            example_video_processing()
        elif choice == '3':
            example_live_detection()
        elif choice == '4':
            example_gesture_recognition()
        elif choice == '5':
            example_landmark_analysis()
        elif choice == '6':
            example_image_detection()
            example_video_processing()
            example_live_detection()
            example_gesture_recognition()
            example_landmark_analysis()
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
