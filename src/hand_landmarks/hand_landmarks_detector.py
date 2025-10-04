"""
Hand Landmarks Detection using MediaPipe

This module provides a comprehensive hand landmarks detection system that can:
- Detect hand landmarks in images, videos, and live streams
- Return landmark coordinates in both image and world coordinates
- Identify handedness (left/right hand)
- Support multiple hands detection
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import List, Dict, Optional, Tuple, Union
import time


class HandLandmarksDetector:
    """
    A comprehensive hand landmarks detector using MediaPipe.
    
    Supports three modes:
    - IMAGE: Single image processing
    - VIDEO: Video file processing
    - LIVE_STREAM: Real-time webcam processing
    """
    
    def __init__(self, 
                 max_num_hands: int = 2,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5,
                 min_presence_confidence: float = 0.5):
        """
        Initialize the Hand Landmarks Detector.
        
        Args:
            max_num_hands: Maximum number of hands to detect
            min_detection_confidence: Minimum confidence for hand detection
            min_tracking_confidence: Minimum confidence for hand tracking
            min_presence_confidence: Minimum confidence for hand presence
        """
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Initialize MediaPipe Hand Landmarker
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Hand landmark names for reference
        self.landmark_names = [
            'WRIST', 'THUMB_CMC', 'THUMB_MCP', 'THUMB_IP', 'THUMB_TIP',
            'INDEX_FINGER_MCP', 'INDEX_FINGER_PIP', 'INDEX_FINGER_DIP', 'INDEX_FINGER_TIP',
            'MIDDLE_FINGER_MCP', 'MIDDLE_FINGER_PIP', 'MIDDLE_FINGER_DIP', 'MIDDLE_FINGER_TIP',
            'RING_FINGER_MCP', 'RING_FINGER_PIP', 'RING_FINGER_DIP', 'RING_FINGER_TIP',
            'PINKY_MCP', 'PINKY_PIP', 'PINKY_DIP', 'PINKY_TIP'
        ]
    
    def detect_landmarks_image(self, image: np.ndarray) -> Dict:
        """
        Detect hand landmarks in a single image.
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            Dictionary containing detection results
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image
        results = self.hands.process(rgb_image)
        
        return self._process_results(results, image.shape)
    
    def detect_landmarks_video(self, video_path: str, output_path: Optional[str] = None) -> List[Dict]:
        """
        Detect hand landmarks in a video file.
        
        Args:
            video_path: Path to input video file
            output_path: Optional path to save output video with landmarks
            
        Returns:
            List of detection results for each frame
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Setup video writer if output path is provided
        out = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        results_list = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect landmarks
            frame_results = self.detect_landmarks_image(frame)
            frame_results['frame_number'] = frame_count
            frame_results['timestamp'] = frame_count / fps
            results_list.append(frame_results)
            
            # Draw landmarks if output video is requested
            if out is not None:
                annotated_frame = self.draw_landmarks(frame, frame_results)
                out.write(annotated_frame)
            
            frame_count += 1
        
        cap.release()
        if out is not None:
            out.release()
        
        return results_list
    
    def detect_landmarks_live(self, camera_id: int = 0, show_window: bool = True) -> None:
        """
        Detect hand landmarks from live webcam feed.
        
        Args:
            camera_id: Camera device ID (usually 0 for default camera)
            show_window: Whether to display the live feed window
        """
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open camera with ID: {camera_id}")
        
        print("Starting live hand landmarks detection...")
        print("Press 'q' to quit, 's' to save current landmarks")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Detect landmarks
            results = self.detect_landmarks_image(frame)
            
            # Draw landmarks
            annotated_frame = self.draw_landmarks(frame, results)
            
            # Add info text
            self._add_info_text(annotated_frame, results)
            
            if show_window:
                cv2.imshow('Hand Landmarks Detection', annotated_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                self._save_landmarks(results)
        
        cap.release()
        cv2.destroyAllWindows()
    
    def _process_results(self, results, image_shape: Tuple[int, int, int]) -> Dict:
        """Process MediaPipe results and extract landmark information."""
        height, width, _ = image_shape
        
        processed_results = {
            'hands_detected': 0,
            'hands': []
        }
        
        if results.multi_hand_landmarks:
            processed_results['hands_detected'] = len(results.multi_hand_landmarks)
            
            for idx, (hand_landmarks, handedness) in enumerate(
                zip(results.multi_hand_landmarks, results.multi_handedness)
            ):
                hand_data = {
                    'hand_id': idx,
                    'handedness': handedness.classification[0].label,
                    'handedness_confidence': handedness.classification[0].score,
                    'landmarks': [],
                    'landmarks_normalized': [],
                    'landmarks_pixel': []
                }
                
                # Extract landmark coordinates
                for i, landmark in enumerate(hand_landmarks.landmark):
                    # Normalized coordinates (0-1)
                    normalized_coords = {
                        'id': i,
                        'name': self.landmark_names[i],
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z
                    }
                    
                    # Pixel coordinates
                    pixel_coords = {
                        'id': i,
                        'name': self.landmark_names[i],
                        'x': int(landmark.x * width),
                        'y': int(landmark.y * height),
                        'z': landmark.z
                    }
                    
                    hand_data['landmarks'].append(normalized_coords)
                    hand_data['landmarks_normalized'].append(normalized_coords)
                    hand_data['landmarks_pixel'].append(pixel_coords)
                
                processed_results['hands'].append(hand_data)
        
        return processed_results
    
    def draw_landmarks(self, image: np.ndarray, results: Dict) -> np.ndarray:
        """
        Draw hand landmarks on the image.
        
        Args:
            image: Input image
            results: Detection results from detect_landmarks_image
            
        Returns:
            Image with drawn landmarks
        """
        annotated_image = image.copy()
        
        if results['hands_detected'] > 0:
            # Convert back to MediaPipe format for drawing
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_results = self.hands.process(rgb_image)
            
            if mp_results.multi_hand_landmarks:
                for hand_landmarks in mp_results.multi_hand_landmarks:
                    # Draw landmarks
                    self.mp_drawing.draw_landmarks(
                        annotated_image,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
        
        return annotated_image
    
    def _add_info_text(self, image: np.ndarray, results: Dict) -> None:
        """Add information text to the image."""
        # Add detection info
        info_text = f"Hands detected: {results['hands_detected']}"
        cv2.putText(image, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Add handedness info for each detected hand
        y_offset = 70
        for hand in results['hands']:
            hand_info = f"Hand {hand['hand_id']}: {hand['handedness']} ({hand['handedness_confidence']:.2f})"
            cv2.putText(image, hand_info, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            y_offset += 30
    
    def _save_landmarks(self, results: Dict) -> None:
        """Save current landmarks to a file."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"hand_landmarks_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"Hand Landmarks Detection Results\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Hands detected: {results['hands_detected']}\n\n")
            
            for hand in results['hands']:
                f.write(f"Hand {hand['hand_id']} ({hand['handedness']}):\n")
                f.write(f"Confidence: {hand['handedness_confidence']:.4f}\n")
                f.write("Landmarks (normalized coordinates):\n")
                
                for landmark in hand['landmarks']:
                    f.write(f"  {landmark['name']}: x={landmark['x']:.4f}, y={landmark['y']:.4f}, z={landmark['z']:.4f}\n")
                f.write("\n")
        
        print(f"Landmarks saved to: {filename}")
    
    def get_gesture_landmarks(self, image: np.ndarray) -> Dict:
        """
        Get hand landmarks for gesture recognition.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Simplified landmark data suitable for gesture recognition
        """
        results = self.detect_landmarks_image(image)
        
        gesture_data = {
            'hands_count': results['hands_detected'],
            'gestures': []
        }
        
        for hand in results['hands']:
            gesture_info = {
                'handedness': hand['handedness'],
                'confidence': hand['handedness_confidence'],
                'key_points': {
                    'wrist': hand['landmarks'][0],
                    'thumb_tip': hand['landmarks'][4],
                    'index_tip': hand['landmarks'][8],
                    'middle_tip': hand['landmarks'][12],
                    'ring_tip': hand['landmarks'][16],
                    'pinky_tip': hand['landmarks'][20]
                },
                'all_landmarks': hand['landmarks']
            }
            gesture_data['gestures'].append(gesture_info)
        
        return gesture_data
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'hands'):
            self.hands.close()


# Utility functions for gesture analysis
def calculate_distance(point1: Dict, point2: Dict) -> float:
    """Calculate Euclidean distance between two landmarks."""
    return np.sqrt((point1['x'] - point2['x'])**2 + 
                   (point1['y'] - point2['y'])**2 + 
                   (point1['z'] - point2['z'])**2)

def is_finger_extended(landmarks: List[Dict], finger_tips: List[int], finger_pips: List[int]) -> List[bool]:
    """
    Determine if fingers are extended based on landmark positions.
    
    Args:
        landmarks: List of all hand landmarks
        finger_tips: List of tip landmark indices
        finger_pips: List of PIP landmark indices
        
    Returns:
        List of boolean values indicating if each finger is extended
    """
    extended = []
    for tip_idx, pip_idx in zip(finger_tips, finger_pips):
        tip_y = landmarks[tip_idx]['y']
        pip_y = landmarks[pip_idx]['y']
        extended.append(tip_y < pip_y)  # Tip is above PIP
    return extended

def recognize_basic_gestures(gesture_data: Dict) -> List[str]:
    """
    Recognize basic hand gestures from landmark data.
    
    Args:
        gesture_data: Gesture data from get_gesture_landmarks
        
    Returns:
        List of recognized gestures
    """
    recognized_gestures = []
    
    for gesture in gesture_data['gestures']:
        landmarks = gesture['all_landmarks']
        
        # Define finger tip and PIP indices
        finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips
        finger_pips = [3, 6, 10, 14, 18]  # Corresponding PIP joints
        
        # Check which fingers are extended
        extended_fingers = is_finger_extended(landmarks, finger_tips, finger_pips)
        
        # Basic gesture recognition
        if all(extended_fingers):
            recognized_gestures.append("Open Hand")
        elif not any(extended_fingers):
            recognized_gestures.append("Closed Fist")
        elif extended_fingers[1] and not any(extended_fingers[i] for i in [0, 2, 3, 4]):
            recognized_gestures.append("Pointing")
        elif extended_fingers[1] and extended_fingers[2] and not any(extended_fingers[i] for i in [0, 3, 4]):
            recognized_gestures.append("Peace Sign")
        elif extended_fingers[0] and not any(extended_fingers[i] for i in [1, 2, 3, 4]):
            recognized_gestures.append("Thumbs Up")
        else:
            recognized_gestures.append("Unknown Gesture")
    
    return recognized_gestures
