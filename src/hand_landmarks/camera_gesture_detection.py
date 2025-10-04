"""
Real-time Hand Gesture Detection with Camera
This script connects to your camera and detects hand gestures, returning landmark values in real-time.
"""

import cv2
import numpy as np
from typing import List, Optional
from .hand_landmarks_detector import HandLandmarksDetector, recognize_basic_gestures
from .gesture_recognition import GestureRecognizer, recognize_advanced_gestures
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
        self.gesture_recognizer = GestureRecognizer()
        self.cap = None
        self.running = False
        self.message_buffer: List[str] = []
        self.last_gesture: Optional[str] = None
        
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
        
        self._reset_message_buffer()
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
                
                # Use advanced gesture recognition
                advanced_gestures = recognize_advanced_gestures(gesture_data)
                basic_gestures = recognize_basic_gestures(gesture_data)
                self._update_message_buffer(advanced_gestures)
                
                # Process and display results
                if results['hands_detected'] > 0:
                    if print_landmarks:
                        self._print_landmarks_advanced(results, advanced_gestures, frame_count)
                    
                    if save_to_file:
                        self._save_landmarks_to_file(results, advanced_gestures, frame_count)
                
                # Draw landmarks and info on frame
                if show_video:
                    annotated_frame = self._annotate_frame_advanced(frame, results, advanced_gestures)
                    cv2.imshow('Real-time Hand Gesture Detection', annotated_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self._save_current_landmarks(results, advanced_gestures)
                elif key == ord('p'):
                    print_landmarks = not print_landmarks
                    print(f"Landmark printing: {'ON' if print_landmarks else 'OFF'}")
                elif key == ord(' '):
                    self._detailed_analysis_advanced(results, advanced_gestures)
                
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
    
    def get_all_landmarks_formatted(self):
        """
        Get all 21 landmarks in a clean, formatted structure.
        
        Returns:
            Dictionary with all landmark coordinates for each detected hand
        """
        landmarks_data = self.get_current_landmarks()
        if not landmarks_data or landmarks_data['landmarks']['hands_detected'] == 0:
            return None

        formatted_data = {
            'timestamp': landmarks_data['timestamp'],
            'hands_count': landmarks_data['landmarks']['hands_detected'],
            'hands': []
        }

        for hand in landmarks_data['landmarks']['hands']:
            hand_data = {
                'handedness': hand['handedness'],
                'confidence': hand['handedness_confidence'],
                'gesture': landmarks_data['gestures'][len(formatted_data['hands'])] if len(formatted_data['hands']) < len(landmarks_data['gestures']) else 'Unknown',
                'landmarks': {}
            }
            
            # Add all 21 landmarks with their names
            for landmark in hand['landmarks']:
                hand_data['landmarks'][landmark['name']] = {
                    'id': landmark['id'],
                    'x': landmark['x'],
                    'y': landmark['y'], 
                    'z': landmark['z']
                }
            
            formatted_data['hands'].append(hand_data)

        return formatted_data

    def _update_message_buffer(self, advanced_gestures):
        """Append a new gesture word when it changes from the previous frame."""
        if not advanced_gestures:
            return

        primary = advanced_gestures[0]
        new_word = primary.get('gesture') if isinstance(primary, dict) else None

        if not new_word or new_word == 'Unknown Gesture':
            return

        if new_word != self.last_gesture:
            self.message_buffer.append(new_word)
            self.last_gesture = new_word
            print(f"📝 Captured gesture word: {new_word}")
            print(f"🧾 Current message: {self.get_message()}")

    def _reset_message_buffer(self):
        """Clear stored gesture words and reset the last gesture tracker."""
        self.message_buffer.clear()
        self.last_gesture = None

    def get_message(self) -> str:
        """Return the accumulated gesture words as a space-separated string."""
        return " ".join(self.message_buffer)

    def reset_message(self) -> None:
        """Public helper to clear the accumulated gesture message."""
        self._reset_message_buffer()

    def _print_landmarks_advanced(self, results, advanced_gestures, frame_count):
        """Print landmark coordinates and advanced gesture info to console."""
        print(f"\n📊 Frame {frame_count} - Hands: {results['hands_detected']}")

        for i, hand in enumerate(results['hands']):
            print(f"\n🖐️  Hand {i+1} ({hand['handedness']}) - Confidence: {hand['handedness_confidence']:.3f}")
            
            # Advanced gesture information
            if i < len(advanced_gestures):
                gesture_info = advanced_gestures[i]
                print(f"   🎯 Gesture: {gesture_info['gesture']}")
                if gesture_info['number'] is not None:
                    print(f"   🔢 Number: {gesture_info['number']}")
                
                # Finger states
                finger_states = gesture_info['finger_states']
                fingers_up = finger_states['fingers_up']
                print(f"   ✋ Fingers: {' '.join([name if up else '❌' for name, up in zip(finger_states['finger_names'], fingers_up)])}")
            
            # Print ALL 21 landmarks
            print("   📍 All Hand Landmarks (x, y, z):")
            for idx, landmark in enumerate(hand['landmarks']):
                print(f"      {idx:2d} - {landmark['name']:18s}: ({landmark['x']:.4f}, {landmark['y']:.4f}, {landmark['z']:.4f})")
    
    def _print_landmarks(self, results, gestures, frame_count):
        """Print landmark coordinates to console (basic version)."""
        print(f"\n📊 Frame {frame_count} - Hands: {results['hands_detected']}")
        
        for i, hand in enumerate(results['hands']):
            print(f"\n🖐️  Hand {i+1} ({hand['handedness']}) - Confidence: {hand['handedness_confidence']:.3f}")
            
            if i < len(gestures):
                print(f"   🎯 Gesture: {gestures[i]}")
            
            # Print ALL 21 landmarks
            print("   📍 All Hand Landmarks (x, y, z):")
            for idx, landmark in enumerate(hand['landmarks']):
                print(f"      {idx:2d} - {landmark['name']:18s}: ({landmark['x']:.4f}, {landmark['y']:.4f}, {landmark['z']:.4f})")
    
    def _annotate_frame_advanced(self, image, results, advanced_gestures):
        """Add advanced annotations to the video frame."""
        annotated_frame = self.detector.draw_landmarks(image, results)
        
        # Add detection info
        cv2.putText(annotated_frame, f"Hands: {results['hands_detected']}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Add advanced gesture info
        y_offset = 70
        for i, gesture_info in enumerate(advanced_gestures):
            gesture = gesture_info['gesture']
            color = (0, 255, 255) if gesture != "Unknown Gesture" else (0, 0, 255)
            
            # Main gesture
            cv2.putText(annotated_frame, f"Hand {i+1}: {gesture}", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset += 25
            
            # Number if detected
            if gesture_info['number'] is not None:
                cv2.putText(annotated_frame, f"Number: {gesture_info['number']}", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                y_offset += 25
            
            # Finger states
            finger_states = gesture_info['finger_states']
            fingers_text = f"Fingers: {finger_states['fingers_count']}/5"
            cv2.putText(annotated_frame, fingers_text, 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            y_offset += 35
        
        # Add instructions
        instructions = [
            "Press 'q' to quit",
            "Press 's' to save landmarks", 
            "Press SPACE for detailed analysis"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(annotated_frame, instruction, 
                       (10, annotated_frame.shape[0] - 60 + i*20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return annotated_frame
    
    def _annotate_frame(self, image, results, gestures):
        """Add annotations to the video frame (basic version)."""
        annotated_frame = self.detector.draw_landmarks(image, results)
        
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
    
    def _detailed_analysis_advanced(self, results, advanced_gestures):
        """Perform detailed analysis of current frame with advanced gesture info."""
        print("\n" + "="*60)
        print("🔍 ADVANCED DETAILED LANDMARK ANALYSIS")
        print("="*60)
        
        if results['hands_detected'] == 0:
            print("❌ No hands detected")
            return
        
        for i, hand in enumerate(results['hands']):
            print(f"\n🖐️  HAND {i+1} DETAILED ANALYSIS")
            print(f"   Handedness: {hand['handedness']}")
            print(f"   Confidence: {hand['handedness_confidence']:.4f}")
            
            if i < len(advanced_gestures):
                gesture_info = advanced_gestures[i]
                print(f"   🎯 Gesture: {gesture_info['gesture']}")
                if gesture_info['number'] is not None:
                    print(f"   🔢 Number: {gesture_info['number']}")
                
                # Detailed finger analysis
                finger_states = gesture_info['finger_states']
                print(f"   ✋ Fingers Extended: {finger_states['fingers_count']}/5")
                for name, extended in zip(finger_states['finger_names'], finger_states['fingers_up']):
                    status = "✅ Extended" if extended else "❌ Folded"
                    print(f"      {name}: {status}")
                
                # Hand orientation info
                orientation = gesture_info['orientation']
                print(f"   📐 Hand Angle: {orientation['hand_angle']:.1f}°")
                print(f"   👋 Palm Facing Camera: {'Yes' if orientation['palm_facing_camera'] else 'No'}")
            
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
            
            print(f"   📏 Hand Span: {hand_span:.4f}")
            print(f"   📏 Hand Length: {hand_length:.4f}")
            
            # Key landmark positions
            print("   📍 Key Landmark Positions:")
            key_landmarks = [0, 4, 8, 12, 16, 20]
            key_names = ['Wrist', 'Thumb Tip', 'Index Tip', 'Middle Tip', 'Ring Tip', 'Pinky Tip']
            for idx, name in zip(key_landmarks, key_names):
                landmark = landmarks[idx]
                print(f"      {name}: ({landmark['x']:.4f}, {landmark['y']:.4f}, {landmark['z']:.4f})")
        
        print("="*60)
    
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
