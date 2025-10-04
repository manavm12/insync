"""
Gesture Interpretation Classes

This module contains specialized classes for interpreting gestures based on the number of fingers up.
Each class handles the logic for a specific finger count (0-5) and determines the specific gesture.
"""

import math
from typing import List, Dict


class BaseGestureInterpreter:
    """Base class for gesture interpreters."""
    
    def __init__(self):
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
    
    def interpret(self, landmarks: List[Dict], fingers_up: List[bool], handedness: str) -> str:
        """Interpret the gesture based on landmarks and finger states."""
        raise NotImplementedError("Subclasses must implement interpret method")
    
    def _calculate_distance(self, point1: Dict, point2: Dict) -> float:
        """Calculate Euclidean distance between two landmark points."""
        return math.sqrt(
            (point1['x'] - point2['x'])**2 + 
            (point1['y'] - point2['y'])**2 + 
            (point1['z'] - point2['z'])**2
        )


class ZeroFingersInterpreter(BaseGestureInterpreter):
    """Interpreter for gestures with 0 fingers up."""
    
    def interpret(self, landmarks: List[Dict], fingers_up: List[bool], handedness: str) -> str:
        """Interpret zero-finger gestures."""
        return "Closed Fist"


class OneFingerInterpreter(BaseGestureInterpreter):
    """Interpreter for gestures with 1 finger up."""
    
    def interpret(self, landmarks: List[Dict], fingers_up: List[bool], handedness: str) -> str:
        """Interpret one-finger gestures."""
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
        
        return "Unknown One Finger Gesture"
    
    def _analyze_thumb_gesture(self, landmarks: List[Dict], handedness: str) -> str:
        """Analyze thumb-only gestures to distinguish thumbs up/down."""
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


class TwoFingerInterpreter(BaseGestureInterpreter):
    """Interpreter for gestures with 2 fingers up."""
    
    def interpret(self, landmarks: List[Dict], fingers_up: List[bool], handedness: str) -> str:
        """Interpret two-finger gestures."""
        if fingers_up[1] and fingers_up[2]:  # Index + Middle
            return self._analyze_two_finger_gesture(landmarks)
        elif fingers_up[0] and fingers_up[1]:  # Thumb + Index
            return "Gun / L-Shape"
        elif fingers_up[0] and fingers_up[4]:  # Thumb + Pinky
            return "Call Me / Shaka"
        elif fingers_up[3] and fingers_up[4]:  # Ring + Pinky
            return "Two Fingers (Ring + Pinky)"
        else:
            return "Two Fingers Up"
    
    def _analyze_two_finger_gesture(self, landmarks: List[Dict]) -> str:
        """Analyze two-finger gestures (index + middle) for peace sign vs victory."""
        # Calculate distance between index and middle fingertips
        index_tip = landmarks[self.INDEX_TIP]
        middle_tip = landmarks[self.MIDDLE_TIP]
        
        distance = self._calculate_distance(index_tip, middle_tip)
        
        # If fingers are spread apart, it's likely a peace sign
        if distance > 0.05:  # Threshold for spread fingers
            return "Peace Sign / Victory"
        else:
            return "Two Fingers Close"


class ThreeFingerInterpreter(BaseGestureInterpreter):
    """Interpreter for gestures with 3 fingers up."""
    
    def interpret(self, landmarks: List[Dict], fingers_up: List[bool], handedness: str) -> str:
        """Interpret three-finger gestures."""
        # I Love You sign: Thumb + Index + Pinky (palm facing away)
        if fingers_up[0] and fingers_up[1] and fingers_up[4] and not fingers_up[2] and not fingers_up[3]:
            return self._analyze_iloveyou_gesture(landmarks, handedness)
        # Rock On sign: Index + Pinky (with thumb sometimes)
        elif fingers_up[1] and fingers_up[4] and not fingers_up[2] and not fingers_up[3]:
            return "Rock On / Devil Horns"
        # Three middle fingers: Index + Middle + Ring
        elif fingers_up[1] and fingers_up[2] and fingers_up[3] and not fingers_up[0] and not fingers_up[4]:
            return "Three Fingers Up"
        # Thumb + Index + Middle
        elif fingers_up[0] and fingers_up[1] and fingers_up[2] and not fingers_up[3] and not fingers_up[4]:
            return "Three (Thumb + Index + Middle)"
        # Thumb + Middle + Ring
        elif fingers_up[0] and fingers_up[2] and fingers_up[3] and not fingers_up[1] and not fingers_up[4]:
            return "Three (Thumb + Middle + Ring)"
        # Thumb + Ring + Pinky
        elif fingers_up[0] and fingers_up[3] and fingers_up[4] and not fingers_up[1] and not fingers_up[2]:
            return "Three (Thumb + Ring + Pinky)"
        # Index + Ring + Pinky
        elif fingers_up[1] and fingers_up[3] and fingers_up[4] and not fingers_up[0] and not fingers_up[2]:
            return "Three (Index + Ring + Pinky)"
        else:
            return "Three Fingers Up"
    
    def _analyze_iloveyou_gesture(self, landmarks: List[Dict], handedness: str) -> str:
        """Analyze the 'I Love You' sign (thumb + index + pinky)."""
        # Check palm orientation by looking at the z-coordinate of key landmarks
        wrist = landmarks[self.WRIST]
        middle_mcp = landmarks[self.MIDDLE_MCP]
        
        # If middle MCP is further from camera than wrist, palm is facing away
        palm_facing_away = middle_mcp['z'] > wrist['z']
        
        if palm_facing_away:
            return "I Love You"
        else:
            return "I Love You (Palm Towards)"


class FourFingerInterpreter(BaseGestureInterpreter):
    """Interpreter for gestures with 4 fingers up."""
    
    def interpret(self, landmarks: List[Dict], fingers_up: List[bool], handedness: str) -> str:
        """Interpret four-finger gestures."""
        if not fingers_up[0]:  # All except thumb
            return "Four Fingers (No Thumb)"
        elif not fingers_up[4]:  # All except pinky
            return "Four Fingers (No Pinky)"
        elif not fingers_up[1]:  # All except index
            return "Four Fingers (No Index)"
        elif not fingers_up[2]:  # All except middle
            return "Four Fingers (No Middle)"
        elif not fingers_up[3]:  # All except ring
            return "Four Fingers (No Ring)"
        else:
            return "Four Fingers Up"


class FiveFingerInterpreter(BaseGestureInterpreter):
    """Interpreter for gestures with 5 fingers up."""
    
    def interpret(self, landmarks: List[Dict], fingers_up: List[bool], handedness: str) -> str:
        """Interpret five-finger gestures."""
        return "Open Hand"


class GestureInterpreterFactory:
    """Factory class to create appropriate gesture interpreters."""
    
    def __init__(self):
        self.interpreters = {
            0: ZeroFingersInterpreter(),
            1: OneFingerInterpreter(),
            2: TwoFingerInterpreter(),
            3: ThreeFingerInterpreter(),
            4: FourFingerInterpreter(),
            5: FiveFingerInterpreter()
        }
    
    def get_interpreter(self, finger_count: int) -> BaseGestureInterpreter:
        """Get the appropriate interpreter for the given finger count."""
        return self.interpreters.get(finger_count, ZeroFingersInterpreter())
    
    def interpret_gesture(self, landmarks: List[Dict], fingers_up: List[bool], 
                         finger_count: int, handedness: str) -> str:
        """Interpret gesture using the appropriate interpreter."""
        interpreter = self.get_interpreter(finger_count)
        return interpreter.interpret(landmarks, fingers_up, handedness)
