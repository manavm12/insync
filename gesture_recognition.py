"""
Advanced Hand Gesture Recognition System

This module contains comprehensive gesture detection algorithms for various hand signs
including thumbs up/down, finger counting, peace signs, and more.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
import math


class GestureRecognizer:
    """Advanced gesture recognition using hand landmark analysis."""
    
    def __init__(self):
        """Initialize the gesture recognizer with landmark definitions."""
        # Landmark indices for easy reference
        self.WRIST = 0
        self.THUMB_TIP = 4
        self.THUMB_IP = 3
        self.THUMB_MCP = 2
        self.INDEX_TIP = 8
        self.INDEX_DIP = 7
        self.INDEX_PIP = 6
        self.INDEX_MCP = 5
        self.MIDDLE_TIP = 12
        self.MIDDLE_DIP = 11
        self.MIDDLE_PIP = 10
        self.MIDDLE_MCP = 9
        self.RING_TIP = 16
        self.RING_DIP = 15
        self.RING_PIP = 14
        self.RING_MCP = 13
        self.PINKY_TIP = 20
        self.PINKY_DIP = 19
        self.PINKY_PIP = 18
        self.PINKY_MCP = 17
        
        # Finger tip and joint indices for easy iteration
        self.finger_tips = [self.THUMB_TIP, self.INDEX_TIP, self.MIDDLE_TIP, self.RING_TIP, self.PINKY_TIP]
        self.finger_pips = [self.THUMB_IP, self.INDEX_PIP, self.MIDDLE_PIP, self.RING_PIP, self.PINKY_PIP]
        self.finger_mcps = [self.THUMB_MCP, self.INDEX_MCP, self.MIDDLE_MCP, self.RING_MCP, self.PINKY_MCP]
        self.finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    
    def recognize_gesture(self, landmarks: List[Dict], handedness: str = "Right") -> str:
        """
        Recognize gesture from hand landmarks.
        
        Args:
            landmarks: List of 21 hand landmarks with x, y, z coordinates
            handedness: "Left" or "Right" hand
            
        Returns:
            String describing the recognized gesture
        """
        if len(landmarks) != 21:
            return "Invalid landmark data"
        
        # Get finger extension states
        fingers_up = self._get_fingers_up(landmarks, handedness)
        
        # Count extended fingers
        fingers_count = sum(fingers_up)
        
        # Recognize specific gestures
        gesture = self._classify_gesture(landmarks, fingers_up, fingers_count, handedness)
        
        return gesture
    
    def _get_fingers_up(self, landmarks: List[Dict], handedness: str) -> List[bool]:
        """
        Determine which fingers are extended.
        
        Args:
            landmarks: Hand landmarks
            handedness: "Left" or "Right" hand
            
        Returns:
            List of 5 booleans indicating if each finger is up
        """
        fingers_up = []
        
        # Thumb (special case - check x-axis for left/right movement)
        if handedness == "Right":
            # Right hand: thumb up if tip is to the right of IP joint
            thumb_up = landmarks[self.THUMB_TIP]['x'] > landmarks[self.THUMB_IP]['x']
        else:
            # Left hand: thumb up if tip is to the left of IP joint
            thumb_up = landmarks[self.THUMB_TIP]['x'] < landmarks[self.THUMB_IP]['x']
        fingers_up.append(thumb_up)
        
        # Other fingers (check y-axis - tip above PIP joint)
        for tip_idx, pip_idx in zip(self.finger_tips[1:], self.finger_pips[1:]):
            finger_up = landmarks[tip_idx]['y'] < landmarks[pip_idx]['y']
            fingers_up.append(finger_up)
        
        return fingers_up
    
    def _classify_gesture(self, landmarks: List[Dict], fingers_up: List[bool], 
                         fingers_count: int, handedness: str) -> str:
        """
        Classify the gesture based on finger states and additional analysis.
        
        Args:
            landmarks: Hand landmarks
            fingers_up: Which fingers are extended
            fingers_count: Total number of extended fingers
            handedness: Hand orientation
            
        Returns:
            Gesture name
        """
        # No fingers up
        if fingers_count == 0:
            return "Closed Fist"
        
        # All fingers up
        elif fingers_count == 5:
            return "Open Hand"
        
        # One finger gestures
        elif fingers_count == 1:
            if fingers_up[0]:  # Only thumb
                return self._analyze_thumb_gesture(landmarks, handedness)
            elif fingers_up[1]:  # Only index
                return "Pointing / One Finger Up"
            elif fingers_up[2]:  # Only middle
                return "Middle Finger"
            elif fingers_up[3]:  # Only ring
                return "Ring Finger Up"
            elif fingers_up[4]:  # Only pinky
                return "Pinky Up"
        
        # Two finger gestures
        elif fingers_count == 2:
            if fingers_up[1] and fingers_up[2]:  # Index + Middle
                return self._analyze_two_finger_gesture(landmarks)
            elif fingers_up[0] and fingers_up[1]:  # Thumb + Index
                return "Gun / L-Shape"
            elif fingers_up[0] and fingers_up[4]:  # Thumb + Pinky
                return "Call Me / Shaka"
            elif fingers_up[3] and fingers_up[4]:  # Ring + Pinky
                return "Two Fingers (Ring + Pinky)"
            else:
                return f"Two Fingers Up"
        
        # Three finger gestures
        elif fingers_count == 3:
            if fingers_up[1] and fingers_up[2] and fingers_up[3]:  # Index + Middle + Ring
                return "Three Fingers Up"
            elif fingers_up[0] and fingers_up[1] and fingers_up[2]:  # Thumb + Index + Middle
                return "Three (Thumb + Index + Middle)"
            else:
                return "Three Fingers Up"
        
        # Four finger gestures
        elif fingers_count == 4:
            if not fingers_up[0]:  # All except thumb
                return "Four Fingers (No Thumb)"
            elif not fingers_up[4]:  # All except pinky
                return "Four Fingers (No Pinky)"
            else:
                return "Four Fingers Up"
        
        return "Unknown Gesture"
    
    def _analyze_thumb_gesture(self, landmarks: List[Dict], handedness: str) -> str:
        """
        Analyze thumb-only gestures to distinguish thumbs up/down.
        
        Args:
            landmarks: Hand landmarks
            handedness: Hand orientation
            
        Returns:
            Specific thumb gesture
        """
        wrist_y = landmarks[self.WRIST]['y']
        thumb_tip_y = landmarks[self.THUMB_TIP]['y']
        thumb_mcp_y = landmarks[self.THUMB_MCP]['y']
        
        # Check if thumb is pointing up or down relative to wrist and MCP
        if thumb_tip_y < wrist_y and thumb_tip_y < thumb_mcp_y:
            return "Thumbs Up"
        elif thumb_tip_y > wrist_y and thumb_tip_y > thumb_mcp_y:
            return "Thumbs Down"
        else:
            return "Thumb Extended"
    
    def _analyze_two_finger_gesture(self, landmarks: List[Dict]) -> str:
        """
        Analyze two-finger gestures (index + middle) for peace sign vs victory.
        
        Args:
            landmarks: Hand landmarks
            
        Returns:
            Specific two-finger gesture
        """
        # Calculate distance between index and middle fingertips
        index_tip = landmarks[self.INDEX_TIP]
        middle_tip = landmarks[self.MIDDLE_TIP]
        
        distance = self._calculate_distance(index_tip, middle_tip)
        
        # If fingers are spread apart, it's likely a peace sign
        if distance > 0.05:  # Threshold for spread fingers
            return "Peace Sign / Victory"
        else:
            return "Two Fingers Close"
    
    def _calculate_distance(self, point1: Dict, point2: Dict) -> float:
        """Calculate Euclidean distance between two landmark points."""
        return math.sqrt(
            (point1['x'] - point2['x'])**2 + 
            (point1['y'] - point2['y'])**2 + 
            (point1['z'] - point2['z'])**2
        )
    
    def get_finger_states(self, landmarks: List[Dict], handedness: str = "Right") -> Dict:
        """
        Get detailed finger state information.
        
        Args:
            landmarks: Hand landmarks
            handedness: Hand orientation
            
        Returns:
            Dictionary with finger states and additional info
        """
        fingers_up = self._get_fingers_up(landmarks, handedness)
        
        return {
            'fingers_up': fingers_up,
            'finger_names': self.finger_names,
            'fingers_count': sum(fingers_up),
            'finger_details': {
                name: {'extended': up, 'tip_position': landmarks[tip_idx]}
                for name, up, tip_idx in zip(self.finger_names, fingers_up, self.finger_tips)
            }
        }
    
    def recognize_number_gesture(self, landmarks: List[Dict], handedness: str = "Right") -> Optional[int]:
        """
        Recognize number gestures (0-5).
        
        Args:
            landmarks: Hand landmarks
            handedness: Hand orientation
            
        Returns:
            Number (0-5) or None if not a clear number gesture
        """
        fingers_up = self._get_fingers_up(landmarks, handedness)
        fingers_count = sum(fingers_up)
        
        # Simple number recognition based on finger count
        if fingers_count == 0:
            return 0
        elif fingers_count == 1 and fingers_up[1]:  # Only index finger
            return 1
        elif fingers_count == 2 and fingers_up[1] and fingers_up[2]:  # Index + Middle
            return 2
        elif fingers_count == 3 and fingers_up[1] and fingers_up[2] and fingers_up[3]:  # Index + Middle + Ring
            return 3
        elif fingers_count == 4 and not fingers_up[0]:  # All except thumb
            return 4
        elif fingers_count == 5:  # All fingers
            return 5
        
        return None  # Not a clear number gesture
    
    def analyze_hand_orientation(self, landmarks: List[Dict]) -> Dict:
        """
        Analyze hand orientation and position.
        
        Args:
            landmarks: Hand landmarks
            
        Returns:
            Dictionary with orientation information
        """
        wrist = landmarks[self.WRIST]
        middle_mcp = landmarks[self.MIDDLE_MCP]
        middle_tip = landmarks[self.MIDDLE_TIP]
        
        # Calculate hand direction vector
        hand_vector = {
            'x': middle_tip['x'] - wrist['x'],
            'y': middle_tip['y'] - wrist['y'],
            'z': middle_tip['z'] - wrist['z']
        }
        
        # Calculate hand angle (rough estimation)
        angle = math.atan2(hand_vector['y'], hand_vector['x']) * 180 / math.pi
        
        return {
            'wrist_position': wrist,
            'hand_vector': hand_vector,
            'hand_angle': angle,
            'palm_facing_camera': middle_mcp['z'] > wrist['z']  # Rough estimation
        }


def recognize_advanced_gestures(gesture_data: Dict) -> List[Dict]:
    """
    Advanced gesture recognition function that can be used with existing code.
    
    Args:
        gesture_data: Gesture data from HandLandmarksDetector.get_gesture_landmarks()
        
    Returns:
        List of dictionaries with detailed gesture information
    """
    recognizer = GestureRecognizer()
    results = []
    
    for hand_data in gesture_data.get('gestures', []):
        landmarks = hand_data.get('all_landmarks', [])
        handedness = hand_data.get('handedness', 'Right')
        
        if len(landmarks) == 21:
            # Main gesture recognition
            gesture = recognizer.recognize_gesture(landmarks, handedness)
            
            # Additional analysis
            finger_states = recognizer.get_finger_states(landmarks, handedness)
            number = recognizer.recognize_number_gesture(landmarks, handedness)
            orientation = recognizer.analyze_hand_orientation(landmarks)
            
            result = {
                'handedness': handedness,
                'confidence': hand_data.get('confidence', 0.0),
                'gesture': gesture,
                'number': number,
                'finger_states': finger_states,
                'orientation': orientation
            }
            
            results.append(result)
    
    return results
