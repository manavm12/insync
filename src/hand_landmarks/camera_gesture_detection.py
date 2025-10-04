"""
Real-time Hand Gesture Detection with Camera
This script connects to your camera and detects hand gestures, returning landmark values in real-time.
"""

import cv2
import numpy as np
from typing import List, Optional, Dict
from .hand_landmarks_detector import HandLandmarksDetector, recognize_basic_gestures
from .holistic_detector import HolisticDetector
from .gesture_recognition import GestureRecognizer, recognize_advanced_gestures
from .gesture_translator import fix_sentence
import json
import time
import threading
from collections import deque

class RealTimeGestureDetector:
    """Real-time gesture detection from camera with landmark output."""
    
    def __init__(self, camera_id=0, use_holistic=True):
        """
        Initialize the real-time gesture detector.
        
        Args:
            camera_id: Camera device ID (usually 0 for default camera)
            use_holistic: If True, use Holistic detector (hand + face tracking)
                         for improved accuracy on signs like THANK YOU
        """
        self.camera_id = camera_id
        self.use_holistic = use_holistic
        
        if use_holistic:
            # Use Holistic detector for hand + face tracking
            self.detector = HolisticDetector(
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            print("✨ Using Holistic detector (Hand + Face tracking enabled)")
        else:
            # Use standard hand detector
            self.detector = HandLandmarksDetector(
                max_num_hands=2,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            print("✋ Using standard hand detector")
        
        self.gesture_recognizer = GestureRecognizer()
        self.cap = None
        self.running = False
        
        # Sentence building and translation
        self.current_sentence: List[str] = []
        self.last_gesture: Optional[str] = None
        self.last_gesture_time: float = 0
        self.sentence_timeout: float = 5.0  # 5 seconds to complete a sentence
        
        # Translation queue and results
        self.sentence_queue: deque = deque()
        self.translated_sentences: List[Dict] = []
        self.translation_thread: Optional[threading.Thread] = None
        self.translation_running: bool = False
        
        # Display settings
        self.show_raw_gestures: bool = True
        self.show_translations: bool = True
        
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
        print("  't' - Toggle translation display")
        print("  'r' - Toggle raw gesture display")
        print("  'c' - Clear all sentences and translations")
        print("  'n' - Force new sentence (don't wait for timeout)")
        print("  SPACE - Capture and analyze current frame")
        
        self._reset_sentence_system()
        self._start_translation_thread()
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
                self._update_sentence_buffer(advanced_gestures)
                self._check_sentence_timeout()
                
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
                elif key == ord('t'):
                    self.show_translations = not self.show_translations
                    print(f"Translation display: {'ON' if self.show_translations else 'OFF'}")
                elif key == ord('r'):
                    self.show_raw_gestures = not self.show_raw_gestures
                    print(f"Raw gesture display: {'ON' if self.show_raw_gestures else 'OFF'}")
                elif key == ord('c'):
                    self._clear_all_sentences()
                elif key == ord('n'):
                    self._force_new_sentence()
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

    def _update_sentence_buffer(self, advanced_gestures):
        """Add new gesture word to current sentence when it changes."""
        if not advanced_gestures:
            return

        primary = advanced_gestures[0]
        new_word = primary.get('gesture') if isinstance(primary, dict) else None

        if not new_word or new_word == 'Unknown Gesture':
            return

        if new_word != self.last_gesture:
            self.current_sentence.append(new_word)
            self.last_gesture = new_word
            self.last_gesture_time = time.time()
            
            if self.show_raw_gestures:
                print(f"📝 Gesture: {new_word}")
                print(f"🔤 Current sentence: {' '.join(self.current_sentence)}")

    def _check_sentence_timeout(self):
        """Check if sentence should be completed due to timeout."""
        if not self.current_sentence:
            return
            
        current_time = time.time()
        if current_time - self.last_gesture_time >= self.sentence_timeout:
            self._complete_sentence()

    def _complete_sentence(self):
        """Complete current sentence and queue it for translation."""
        if not self.current_sentence:
            return
            
        sentence_text = ' '.join(self.current_sentence)
        print(f"\n✅ Sentence completed: '{sentence_text}'")
        
        # Add to translation queue
        sentence_data = {
            'id': len(self.translated_sentences) + len(self.sentence_queue) + 1,
            'raw_text': sentence_text,
            'timestamp': time.time(),
            'status': 'queued'
        }
        
        self.sentence_queue.append(sentence_data)
        print(f"📤 Queued for translation (Queue size: {len(self.sentence_queue)})")
        
        # Reset for next sentence
        self.current_sentence.clear()
        self.last_gesture = None

    def _force_new_sentence(self):
        """Force completion of current sentence without waiting for timeout."""
        if self.current_sentence:
            print("🔄 Forcing sentence completion...")
            self._complete_sentence()
        else:
            print("ℹ️  No current sentence to complete")

    def _clear_all_sentences(self):
        """Clear all sentences and translations."""
        self.current_sentence.clear()
        self.sentence_queue.clear()
        self.translated_sentences.clear()
        self.last_gesture = None
        print("🗑️  Cleared all sentences and translations")

    def _reset_sentence_system(self):
        """Reset the entire sentence system."""
        self._clear_all_sentences()
        self.translation_running = False

    def _start_translation_thread(self):
        """Start the background translation thread."""
        self.translation_running = True
        self.translation_thread = threading.Thread(target=self._translation_worker, daemon=True)
        self.translation_thread.start()
        print("🤖 Translation service started")

    def _translation_worker(self):
        """Background worker to process translation queue."""
        while self.translation_running:
            try:
                if self.sentence_queue:
                    sentence_data = self.sentence_queue.popleft()
                    
                    print(f"🔄 Translating: '{sentence_data['raw_text']}'")
                    sentence_data['status'] = 'translating'
                    
                    # Translate using OpenAI
                    translated_text = fix_sentence(sentence_data['raw_text'])
                    
                    sentence_data['translated_text'] = translated_text
                    sentence_data['status'] = 'completed'
                    sentence_data['translation_time'] = time.time()
                    
                    self.translated_sentences.append(sentence_data)
                    
                    if self.show_translations:
                        print(f"✨ Translation #{sentence_data['id']}: '{translated_text}'")
                    
                    # Keep only last 10 translations to save memory
                    if len(self.translated_sentences) > 10:
                        self.translated_sentences.pop(0)
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                print(f"❌ Translation error: {e}")
                if self.sentence_queue:
                    failed_sentence = self.sentence_queue.popleft()
                    failed_sentence['status'] = 'failed'
                    failed_sentence['error'] = str(e)
                    self.translated_sentences.append(failed_sentence)

    def get_current_sentence(self) -> str:
        """Get the current sentence being built."""
        return ' '.join(self.current_sentence)

    def get_recent_translations(self, count: int = 5) -> List[Dict]:
        """Get the most recent translations."""
        return self.translated_sentences[-count:] if self.translated_sentences else []

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
        
        # Add sentence and translation info
        if self.show_raw_gestures and self.current_sentence:
            current_text = f"Current: {' '.join(self.current_sentence)}"
            cv2.putText(annotated_frame, current_text, 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            y_offset += 25
        
        if self.show_translations and self.translated_sentences:
            recent = self.translated_sentences[-3:]  # Show last 3 translations
            for i, trans in enumerate(recent):
                if trans['status'] == 'completed':
                    text = f"#{trans['id']}: {trans['translated_text']}"
                    cv2.putText(annotated_frame, text, 
                               (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    y_offset += 20
        
        # Add instructions
        instructions = [
            "q:quit s:save t:toggle-trans r:toggle-raw",
            "c:clear n:new-sentence SPACE:analysis"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(annotated_frame, instruction, 
                       (10, annotated_frame.shape[0] - 40 + i*20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
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
        self.translation_running = False
        
        # Wait for translation thread to finish
        if self.translation_thread and self.translation_thread.is_alive():
            self.translation_thread.join(timeout=2.0)
        
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
