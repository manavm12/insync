"""
Holistic Detector using MediaPipe Holistic

This module provides hand + face landmark detection for improved ASL recognition.
By tracking a reference point on the face, we can detect gestures that involve
hand-to-face proximity (like THANK YOU, PLEASE, etc.)
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import List, Dict, Optional, Tuple


class HolisticDetector:
    """
    Enhanced detector using MediaPipe Holistic for hand and face tracking.
    
    This enables detection of ASL signs that require face reference points,
    such as THANK YOU (hand moves from mouth downward).
    """
    
    def __init__(self,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        """
        Initialize the Holistic Detector.
        
        Args:
            min_detection_confidence: Minimum confidence for detection
            min_tracking_confidence: Minimum confidence for tracking
        """
        self.mp_holistic = mp.solutions.holistic
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Initialize MediaPipe Holistic
        self.holistic = self.mp_holistic.Holistic(
            static_image_mode=False,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Hand landmark names for reference
        self.hand_landmark_names = [
            'WRIST', 'THUMB_CMC', 'THUMB_MCP', 'THUMB_IP', 'THUMB_TIP',
            'INDEX_FINGER_MCP', 'INDEX_FINGER_PIP', 'INDEX_FINGER_DIP', 'INDEX_FINGER_TIP',
            'MIDDLE_FINGER_MCP', 'MIDDLE_FINGER_PIP', 'MIDDLE_FINGER_DIP', 'MIDDLE_FINGER_TIP',
            'RING_FINGER_MCP', 'RING_FINGER_PIP', 'RING_FINGER_DIP', 'RING_FINGER_TIP',
            'PINKY_MCP', 'PINKY_PIP', 'PINKY_DIP', 'PINKY_TIP'
        ]
        
        # Face landmark indices for reference
        # Using nose tip (1) as primary face reference point
        # Using chin (152) as chest/lower face reference
        # Using upper lip (13) as mouth reference for THANK YOU
        self.FACE_NOSE_TIP = 1
        self.FACE_CHIN = 152
        self.FACE_UPPER_LIP = 13
        self.FACE_FOREHEAD = 10
    
    def detect_landmarks_image(self, image: np.ndarray) -> Dict:
        """
        Detect hand and face landmarks in a single image.
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            Dictionary containing hand and face detection results
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image
        results = self.holistic.process(rgb_image)
        
        return self._process_results(results, image.shape)
    
    def _process_results(self, results, image_shape: Tuple[int, int, int]) -> Dict:
        """Process MediaPipe Holistic results and extract landmark information."""
        height, width, _ = image_shape
        
        processed_results = {
            'hands_detected': 0,
            'hands': [],
            'face_detected': False,
            'face_reference_point': None,
            'face_mouth_point': None,
            'face_chin_point': None,
            'face_forehead_point': None
        }
        
        # Process face landmarks
        if results.face_landmarks:
            processed_results['face_detected'] = True
            
            # Extract key face reference points
            # Nose tip (primary reference)
            nose_landmark = results.face_landmarks.landmark[self.FACE_NOSE_TIP]
            processed_results['face_reference_point'] = {
                'x': nose_landmark.x,
                'y': nose_landmark.y,
                'z': nose_landmark.z,
                'pixel_x': int(nose_landmark.x * width),
                'pixel_y': int(nose_landmark.y * height)
            }
            
            # Upper lip (for THANK YOU detection)
            mouth_landmark = results.face_landmarks.landmark[self.FACE_UPPER_LIP]
            processed_results['face_mouth_point'] = {
                'x': mouth_landmark.x,
                'y': mouth_landmark.y,
                'z': mouth_landmark.z,
                'pixel_x': int(mouth_landmark.x * width),
                'pixel_y': int(mouth_landmark.y * height)
            }
            
            # Chin (for chest-level reference)
            chin_landmark = results.face_landmarks.landmark[self.FACE_CHIN]
            processed_results['face_chin_point'] = {
                'x': chin_landmark.x,
                'y': chin_landmark.y,
                'z': chin_landmark.z,
                'pixel_x': int(chin_landmark.x * width),
                'pixel_y': int(chin_landmark.y * height)
            }
            
            # Forehead (for upper reference)
            forehead_landmark = results.face_landmarks.landmark[self.FACE_FOREHEAD]
            processed_results['face_forehead_point'] = {
                'x': forehead_landmark.x,
                'y': forehead_landmark.y,
                'z': forehead_landmark.z,
                'pixel_x': int(forehead_landmark.x * width),
                'pixel_y': int(forehead_landmark.y * height)
            }
        
        # Process left hand
        if results.left_hand_landmarks:
            hand_data = self._process_hand(
                results.left_hand_landmarks,
                'Left',
                processed_results['hands_detected'],
                width,
                height
            )
            processed_results['hands'].append(hand_data)
            processed_results['hands_detected'] += 1
        
        # Process right hand
        if results.right_hand_landmarks:
            hand_data = self._process_hand(
                results.right_hand_landmarks,
                'Right',
                processed_results['hands_detected'],
                width,
                height
            )
            processed_results['hands'].append(hand_data)
            processed_results['hands_detected'] += 1
        
        return processed_results
    
    def _process_hand(self, hand_landmarks, handedness: str, hand_id: int,
                     width: int, height: int) -> Dict:
        """Process a single hand's landmarks."""
        hand_data = {
            'hand_id': hand_id,
            'handedness': handedness,
            'handedness_confidence': 1.0,  # Holistic always knows left/right
            'landmarks': [],
            'landmarks_normalized': [],
            'landmarks_pixel': []
        }
        
        # Extract landmark coordinates
        for i, landmark in enumerate(hand_landmarks.landmark):
            # Normalized coordinates (0-1)
            normalized_coords = {
                'id': i,
                'name': self.hand_landmark_names[i],
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z
            }
            
            # Pixel coordinates
            pixel_coords = {
                'id': i,
                'name': self.hand_landmark_names[i],
                'x': int(landmark.x * width),
                'y': int(landmark.y * height),
                'z': landmark.z
            }
            
            hand_data['landmarks'].append(normalized_coords)
            hand_data['landmarks_normalized'].append(normalized_coords)
            hand_data['landmarks_pixel'].append(pixel_coords)
        
        return hand_data
    
    def draw_landmarks(self, image: np.ndarray, results: Dict) -> np.ndarray:
        """
        Draw hand and face landmarks on the image.
        
        Args:
            image: Input image
            results: Detection results from detect_landmarks_image
            
        Returns:
            Image with drawn landmarks
        """
        annotated_image = image.copy()
        
        # Re-process for drawing (MediaPipe requires this)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_results = self.holistic.process(rgb_image)
        
        # Draw face landmarks (just the reference points for clarity)
        if results['face_detected'] and mp_results.face_landmarks:
            # Draw a circle at the nose tip
            nose_point = results['face_reference_point']
            cv2.circle(annotated_image, 
                      (nose_point['pixel_x'], nose_point['pixel_y']),
                      5, (0, 255, 255), -1)
            cv2.putText(annotated_image, "NOSE", 
                       (nose_point['pixel_x'] + 10, nose_point['pixel_y']),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            # Draw a circle at the mouth
            mouth_point = results['face_mouth_point']
            cv2.circle(annotated_image,
                      (mouth_point['pixel_x'], mouth_point['pixel_y']),
                      5, (255, 0, 255), -1)
            cv2.putText(annotated_image, "MOUTH",
                       (mouth_point['pixel_x'] + 10, mouth_point['pixel_y']),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
        
        # Draw hand landmarks
        if mp_results.left_hand_landmarks:
            self.mp_drawing.draw_landmarks(
                annotated_image,
                mp_results.left_hand_landmarks,
                self.mp_holistic.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )
        
        if mp_results.right_hand_landmarks:
            self.mp_drawing.draw_landmarks(
                annotated_image,
                mp_results.right_hand_landmarks,
                self.mp_holistic.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )
        
        return annotated_image
    
    def get_gesture_landmarks(self, image: np.ndarray) -> Dict:
        """
        Get hand and face landmarks for gesture recognition.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Simplified landmark data suitable for gesture recognition
        """
        results = self.detect_landmarks_image(image)
        
        gesture_data = {
            'hands_count': results['hands_detected'],
            'face_detected': results['face_detected'],
            'face_reference_point': results['face_reference_point'],
            'face_mouth_point': results['face_mouth_point'],
            'face_chin_point': results['face_chin_point'],
            'face_forehead_point': results['face_forehead_point'],
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
        if hasattr(self, 'holistic'):
            self.holistic.close()

