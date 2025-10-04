"""
Real-time Hand Gesture Detection with Camera
This script connects to your camera and detects hand gestures, returning landmark values in real-time.
"""

import cv2
import numpy as np
from hand_landmarks_detector import HandLandmarksDetector, recognize_basic_gestures
import json
import time


class RealTimeGestureDetector:
    """Real-time gesture detection from camera with landmark output."""
    
    def __init__(self, camera_id=0):
        """
        Initialize the real-time gesture detector.
        
        Args:
            camera_id: Camera device ID (usually 0 for default camera)
        """
        self.camera_id = camera_id
        self.detector = HandLandmarksDetector(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.cap = None
        self.running = False
        
    def start_detection(self, show_video=True, print_landmarks=True, save_to_file=False):
        """
        Start real-time gesture detection.
        
        Args:
            show_video: Whether to display the video window
            print_landmarks: Whether to print landmark coordinates to console
            save_to_file: Whether to save landmarks to JSON file
        """
        # Initialize camera
        self.cap = cv2.VideoCapture(self.camera_id)
        
        if not self.cap.isOpened():
            raise ValueError(f"Could not open camera with ID: {self.camera_id}")
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("🎥 Camera connected successfully!")
        print("👋 Starting hand gesture detection...")
        print("\nControls:")
        print("  'q' - Quit")
        print("  's' - Save current landmarks to file")
        print("  'p' - Toggle landmark printing")
        print("  SPACE - Capture and analyze current frame")
        
        self.running = True
        frame_count = 0
        
        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read from camera")
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Detect hand landmarks
                results = self.detector.detect_landmarks_image(frame)
                
                # Get gesture data
                gesture_data = self.detector.get_gesture_landmarks(frame)
                gestures = recognize_basic_gestures(gesture_data)
                
                # Process and display results
                if results['hands_detected'] > 0:
                    if print_landmarks:
                        self._print_landmarks(results, gestures, frame_count)
                    
                    if save_to_file:
                        self._save_landmarks_to_file(results, gestures, frame_count)
                
                # Draw landmarks and info on frame
                if show_video:
                    annotated_frame = self._annotate_frame(frame, results, gestures)
                    cv2.imshow('Real-time Hand Gesture Detection', annotated_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self._save_current_landmarks(results, gestures)
                elif key == ord('p'):
                    print_landmarks = not print_landmarks
                    print(f"Landmark printing: {'ON' if print_landmarks else 'OFF'}")
                elif key == ord(' '):
                    self._detailed_analysis(results, gestures)
                
                frame_count += 1
                
        except KeyboardInterrupt:
            print("\n🛑 Detection stopped by user")
        
        finally:
            self._cleanup()
    
    def get_current_landmarks(self):
        """
        Get landmarks from current camera frame (single capture).
        
        Returns:
            Dictionary with landmark data and gestures
        """
        if not self.cap or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camera_id)
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        frame = cv2.flip(frame, 1)
        results = self.detector.detect_landmarks_image(frame)
        gesture_data = self.detector.get_gesture_landmarks(frame)
        gestures = recognize_basic_gestures(gesture_data)
        
        return {
            'timestamp': time.time(),
            'landmarks': results,
            'gestures': gestures,
            'frame_shape': frame.shape
        }
    
    def _print_landmarks(self, results, gestures, frame_count):
        """Print landmark coordinates to console."""
        print(f"\n📊 Frame {frame_count} - Hands: {results['hands_detected']}")
        
        for i, hand in enumerate(results['hands']):
            print(f"\n🖐️  Hand {i+1} ({hand['handedness']}) - Confidence: {hand['handedness_confidence']:.3f}")
            
            if i < len(gestures):
                print(f"   🎯 Gesture: {gestures[i]}")
            
            # Print key landmarks
            key_landmarks = [0, 4, 8, 12, 16, 20]  # Wrist, thumb tip, finger tips
            key_names = ['Wrist', 'Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
            
            print("   📍 Key Landmarks:")
            for idx, name in zip(key_landmarks, key_names):
                landmark = hand['landmarks'][idx]
                print(f"      {name}: ({landmark['x']:.3f}, {landmark['y']:.3f}, {landmark['z']:.3f})")
    
    def _annotate_frame(self, frame, results, gestures):
        """Add annotations to the video frame."""
        annotated_frame = self.detector.draw_landmarks(frame, results)
        
        # Add detection info
        cv2.putText(annotated_frame, f"Hands: {results['hands_detected']}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Add gesture info
        y_offset = 70
        for i, gesture in enumerate(gestures):
            color = (0, 255, 255) if gesture != "Unknown Gesture" else (0, 0, 255)
            cv2.putText(annotated_frame, f"Gesture {i+1}: {gesture}", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset += 30
        
        # Add instructions
        instructions = [
            "Press 'q' to quit",
            "Press 's' to save landmarks",
            "Press SPACE for analysis"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(annotated_frame, instruction, 
                       (10, annotated_frame.shape[0] - 60 + i*20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return annotated_frame
    
    def _save_landmarks_to_file(self, results, gestures, frame_count):
        """Save landmarks to a continuous log file."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"landmarks_log_{timestamp}.jsonl"
        
        data = {
            'timestamp': time.time(),
            'frame': frame_count,
            'results': results,
            'gestures': gestures
        }
        
        with open(filename, 'a') as f:
            f.write(json.dumps(data) + '\n')
    
    def _save_current_landmarks(self, results, gestures):
        """Save current landmarks to a timestamped file."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"hand_landmarks_{timestamp}.json"
        
        data = {
            'timestamp': timestamp,
            'results': results,
            'gestures': gestures
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Landmarks saved to: {filename}")
    
    def _detailed_analysis(self, results, gestures):
        """Perform detailed analysis of current frame."""
        print("\n" + "="*50)
        print("🔍 DETAILED LANDMARK ANALYSIS")
        print("="*50)
        
        if results['hands_detected'] == 0:
            print("❌ No hands detected")
            return
        
        for i, hand in enumerate(results['hands']):
            print(f"\n🖐️  HAND {i+1} ANALYSIS")
            print(f"   Handedness: {hand['handedness']}")
            print(f"   Confidence: {hand['handedness_confidence']:.4f}")
            
            if i < len(gestures):
                print(f"   Gesture: {gestures[i]}")
            
            # Calculate hand metrics
            landmarks = hand['landmarks']
            
            # Hand span (thumb to pinky)
            thumb_tip = landmarks[4]
            pinky_tip = landmarks[20]
            hand_span = np.sqrt(
                (thumb_tip['x'] - pinky_tip['x'])**2 + 
                (thumb_tip['y'] - pinky_tip['y'])**2
            )
            
            # Hand length (wrist to middle finger)
            wrist = landmarks[0]
            middle_tip = landmarks[12]
            hand_length = np.sqrt(
                (middle_tip['x'] - wrist['x'])**2 + 
                (middle_tip['y'] - wrist['y'])**2
            )
            
            print(f"   Hand Span: {hand_span:.4f}")
            print(f"   Hand Length: {hand_length:.4f}")
            
            # Finger extension analysis
            finger_tips = [4, 8, 12, 16, 20]
            finger_pips = [3, 6, 10, 14, 18]
            finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
            
            print("   Finger States:")
            for tip_idx, pip_idx, name in zip(finger_tips, finger_pips, finger_names):
                tip_y = landmarks[tip_idx]['y']
                pip_y = landmarks[pip_idx]['y']
                extended = tip_y < pip_y
                print(f"      {name}: {'Extended' if extended else 'Folded'}")
        
        print("="*50)
    
    def _cleanup(self):
        """Clean up resources."""
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("🧹 Cleanup completed")


def main():
    """Main function to start gesture detection."""
    print("🚀 Real-time Hand Gesture Detection")
    print("=" * 40)
    
    try:
        # Initialize detector
        detector = RealTimeGestureDetector(camera_id=0)
        
        # Start detection
        detector.start_detection(
            show_video=True,
            print_landmarks=True,
            save_to_file=False
        )
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure your camera is connected and not being used by another application")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def quick_capture():
    """Quick function to capture and return landmarks from current camera frame."""
    detector = RealTimeGestureDetector()
    landmarks = detector.get_current_landmarks()
    detector._cleanup()
    return landmarks


if __name__ == "__main__":
    main()
