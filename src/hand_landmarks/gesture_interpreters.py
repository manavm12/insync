"""
ASL Gesture Interpretation Classes

This module contains specialized classes for interpreting American Sign Language (ASL) gestures
based on hand shape, finger positions, and hand orientation. Designed for real-time ASL interpretation
to help the hearing-impaired communicate effectively.

Each class handles the logic for a specific finger count (0-5) and determines the specific ASL gesture.
"""

import math
from typing import List, Dict, Tuple, Optional


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
    
    def interpret(self, landmarks: List[Dict], fingers_up: List[bool], handedness: str, 
                  face_ref: Optional[Dict] = None) -> str:
        """
        Interpret the gesture based on landmarks and finger states.
        
        Args:
            landmarks: Hand landmark positions
            fingers_up: Which fingers are extended
            handedness: Left or Right hand
            face_ref: Optional face reference points dict with keys:
                     'nose', 'mouth', 'chin', 'forehead'
        """
        raise NotImplementedError("Subclasses must implement interpret method")
    
    def _calculate_distance(self, point1: Dict, point2: Dict) -> float:
        """Calculate Euclidean distance between two landmark points."""
        return math.sqrt(
            (point1['x'] - point2['x'])**2 + 
            (point1['y'] - point2['y'])**2 + 
            (point1['z'] - point2['z'])**2
        )
    
    def _is_hand_near_location(self, landmarks: List[Dict], target_y: float, tolerance: float = 0.15) -> bool:
        """Check if hand is near a specific vertical location (for signs like 'thank you', 'please')."""
        # Use multiple finger tips to determine hand position
        avg_y = sum([landmarks[i]['y'] for i in [8, 12, 16]]) / 3
        return abs(avg_y - target_y) < tolerance
    
    def _get_hand_openness(self, landmarks: List[Dict], fingers_up: List[bool]) -> float:
        """Calculate how open/spread the hand is (0-1 scale)."""
        # Calculate average distance between adjacent fingertips
        distances = []
        tip_indices = [4, 8, 12, 16, 20]
        for i in range(len(tip_indices) - 1):
            dist = self._calculate_distance(landmarks[tip_indices[i]], landmarks[tip_indices[i+1]])
            distances.append(dist)
        return sum(distances) / len(distances) if distances else 0
    
    def _are_fingertips_together(self, landmarks: List[Dict], finger_indices: List[int], threshold: float = 0.08) -> bool:
        """Check if specified fingertips are close together."""
        if len(finger_indices) < 2:
            return False
        total_dist = 0
        count = 0
        for i in range(len(finger_indices)):
            for j in range(i + 1, len(finger_indices)):
                dist = self._calculate_distance(landmarks[finger_indices[i]], landmarks[finger_indices[j]])
                total_dist += dist
                count += 1
        avg_dist = total_dist / count if count > 0 else 0
        return avg_dist < threshold
    
    def _is_fist_on_chest(self, landmarks: List[Dict]) -> bool:
        """Check if hand is in fist position near chest area (for 'sorry', 'please')."""
        # Approximate chest location in camera view
        wrist_y = landmarks[self.WRIST]['y']
        # Chest is typically in middle of frame vertically (0.3-0.6)
        return 0.3 < wrist_y < 0.7
    
    def _check_palm_orientation(self, landmarks: List[Dict]) -> str:
        """Determine if palm is facing towards or away from camera."""
        wrist = landmarks[self.WRIST]
        middle_mcp = landmarks[self.MIDDLE_MCP]
        # If middle MCP is further from camera than wrist, palm faces away
        if middle_mcp['z'] > wrist['z']:
            return "away"
        else:
            return "towards"
    
    def _is_hand_near_face_point(self, landmarks: List[Dict], face_point: Dict, 
                                  threshold: float = 0.15) -> bool:
        """
        Check if hand is near a specific face point.
        
        Args:
            landmarks: Hand landmarks
            face_point: Face reference point with 'x', 'y', 'z' coordinates
            threshold: Distance threshold for "near" detection
            
        Returns:
            True if hand is near the face point
        """
        if face_point is None:
            return False
        
        # Use palm center (average of key points) for distance calculation
        palm_center_x = sum([landmarks[i]['x'] for i in [0, 5, 9, 13, 17]]) / 5
        palm_center_y = sum([landmarks[i]['y'] for i in [0, 5, 9, 13, 17]]) / 5
        
        palm_center = {'x': palm_center_x, 'y': palm_center_y, 'z': 0}
        
        distance = self._calculate_distance(palm_center, face_point)
        return distance < threshold
    
    def _calculate_distance_to_face(self, hand_point: Dict, face_point: Optional[Dict]) -> float:
        """
        Calculate distance from a hand point to a face point.
        
        Args:
            hand_point: Hand landmark point
            face_point: Face reference point
            
        Returns:
            Distance value, or infinity if face_point is None
        """
        if face_point is None:
            return float('inf')
        return self._calculate_distance(hand_point, face_point)


class ZeroFingersInterpreter(BaseGestureInterpreter):
    """Interpreter for ASL gestures with 0 fingers up (closed fist)."""
    
    def interpret(self, landmarks: List[Dict], fingers_up: List[bool], handedness: str,
                  face_ref: Optional[Dict] = None) -> str:
        """Interpret zero-finger ASL gestures."""
        # Check if fist is near chest (could be "sorry" or "please")
        if face_ref and face_ref.get('chin'):
            # Use chin as reference for chest area
            # If fist is near/below chin area, it's likely SORRY/PLEASE
            if self._is_hand_near_face_point(landmarks, face_ref['chin'], threshold=0.20):
                return "SORRY/PLEASE (fist at chest, motion needed)"
        elif self._is_fist_on_chest(landmarks):
            # Fallback to positional detection if no face reference
            return "SORRY/PLEASE (fist at chest, motion needed)"
        
        return "Closed Fist"


class OneFingerInterpreter(BaseGestureInterpreter):
    """Interpreter for ASL gestures with 1 finger up."""
    
    def interpret(self, landmarks: List[Dict], fingers_up: List[bool], handedness: str,
                  face_ref: Optional[Dict] = None) -> str:
        """Interpret one-finger ASL gestures."""
        if fingers_up[0]:  # Only thumb
            return self._analyze_thumb_gesture(landmarks, handedness)
        elif fingers_up[1]:  # Only index
            return self._analyze_index_gesture(landmarks)
        elif fingers_up[2]:  # Only middle
            return "Need"
        elif fingers_up[3]:  # Only ring
            return "Help"
        elif fingers_up[4]:  # Only pinky
            return "Homework"
        
        return "Single Finger Up"
    
    def _analyze_thumb_gesture(self, landmarks: List[Dict], handedness: str) -> str:
        """Analyze thumb-only ASL gestures."""
        wrist_y = landmarks[self.WRIST]['y']
        thumb_tip_y = landmarks[self.THUMB_TIP]['y']
        thumb_mcp_y = landmarks[self.THUMB_MCP]['y']
        
        # Check if thumb is pointing up or down
        if thumb_tip_y < wrist_y and thumb_tip_y < thumb_mcp_y:
            return "GOOD"
        elif thumb_tip_y > wrist_y and thumb_tip_y > thumb_mcp_y:
            return "BAD / Thumbs Down"
        else:
            return "Thumb Extended"
    
    def _analyze_index_gesture(self, landmarks: List[Dict]) -> str:
        """Analyze index finger gestures for ASL."""
        index_tip = landmarks[self.INDEX_TIP]
        wrist = landmarks[self.WRIST]
        
        # Check if pointing up (Number 1)
        if index_tip['y'] < wrist['y']:
            return "Number 1"
        else:
            return "GO"


class TwoFingerInterpreter(BaseGestureInterpreter):
    """Interpreter for ASL gestures with 2 fingers up."""
    
    def interpret(self, landmarks: List[Dict], fingers_up: List[bool], handedness: str,
                  face_ref: Optional[Dict] = None) -> str:
        """Interpret two-finger ASL gestures."""
        if fingers_up[1] and fingers_up[2]:  # Index + Middle
            return self._analyze_index_middle_gesture(landmarks)
        elif fingers_up[0] and fingers_up[1]:  # Thumb + Index
            return self._analyze_thumb_index_gesture(landmarks)
        elif fingers_up[0] and fingers_up[4]:  # Thumb + Pinky
            return self._analyze_thumb_pinky_gesture(landmarks)
        elif fingers_up[3] and fingers_up[4]:  # Ring + Pinky
            return "Two Fingers (Ring + Pinky)"
        elif fingers_up[0] and fingers_up[2]:  # Thumb + Middle
            return "Thumb + Middle"
        else:
            return "Two Fingers Up"
    
    def _analyze_index_middle_gesture(self, landmarks: List[Dict]) -> str:
        """Analyze index + middle finger ASL gestures."""
        index_tip = landmarks[self.INDEX_TIP]
        middle_tip = landmarks[self.MIDDLE_TIP]
        wrist = landmarks[self.WRIST]
        
        distance = self._calculate_distance(index_tip, middle_tip)
        
        # Check if fingers are pointing up (Number 2)
        avg_y = (index_tip['y'] + middle_tip['y']) / 2
        if avg_y < wrist['y'] and distance > 0.05:
            return "Number 2 / PEACE"
        elif distance > 0.05:
            return "PEACE Sign"
        else:
            # Fingers close together
            return "Two Fingers Close"
    
    def _analyze_thumb_index_gesture(self, landmarks: List[Dict]) -> str:
        """Analyze thumb + index finger ASL gestures."""
        thumb_tip = landmarks[self.THUMB_TIP]
        index_tip = landmarks[self.INDEX_TIP]
        
        # Check if forming a circle (OK sign)
        distance = self._calculate_distance(thumb_tip, index_tip)
        if distance < 0.06:
            return "OK / FINE"
        else:
            # L-shape
            return "L-Shape"
    
    def _analyze_thumb_pinky_gesture(self, landmarks: List[Dict]) -> str:
        """Analyze thumb + pinky ASL gestures."""
        return "CALL ME / Hang Loose"


class ThreeFingerInterpreter(BaseGestureInterpreter):
    """Interpreter for ASL gestures with 3 fingers up."""
    
    def interpret(self, landmarks: List[Dict], fingers_up: List[bool], handedness: str,
                  face_ref: Optional[Dict] = None) -> str:
        """Interpret three-finger ASL gestures."""
        # I Love You sign: Thumb + Index + Pinky
        if fingers_up[0] and fingers_up[1] and fingers_up[4] and not fingers_up[2] and not fingers_up[3]:
            return self._analyze_iloveyou_gesture(landmarks)
        # Three middle fingers: Index + Middle + Ring (Number 3)
        elif fingers_up[1] and fingers_up[2] and fingers_up[3] and not fingers_up[0] and not fingers_up[4]:
            return self._analyze_three_middle_fingers(landmarks)
        # Thumb + Index + Middle
        elif fingers_up[0] and fingers_up[1] and fingers_up[2] and not fingers_up[3] and not fingers_up[4]:
            return "Number 3 (variant)"
        # Thumb + Middle + Ring
        elif fingers_up[0] and fingers_up[2] and fingers_up[3] and not fingers_up[1] and not fingers_up[4]:
            return "Three Fingers (Thumb + Middle + Ring)"
        # Thumb + Ring + Pinky
        elif fingers_up[0] and fingers_up[3] and fingers_up[4] and not fingers_up[1] and not fingers_up[2]:
            return "Three Fingers (Thumb + Ring + Pinky)"
        # Index + Ring + Pinky
        elif fingers_up[1] and fingers_up[3] and fingers_up[4] and not fingers_up[0] and not fingers_up[2]:
            return "Three Fingers (Index + Ring + Pinky)"
        # Middle + Ring + Pinky
        elif fingers_up[2] and fingers_up[3] and fingers_up[4] and not fingers_up[0] and not fingers_up[1]:
            return "Three Fingers (Middle + Ring + Pinky)"
        else:
            return "Three Fingers Up"
    
    def _analyze_iloveyou_gesture(self, landmarks: List[Dict]) -> str:
        """Analyze the ASL 'I Love You' sign (thumb + index + pinky)."""
        palm_orientation = self._check_palm_orientation(landmarks)
        
        if palm_orientation == "away":
            return "I LOVE YOU"
        else:
            return "I LOVE YOU (palm towards)"
    
    def _analyze_three_middle_fingers(self, landmarks: List[Dict]) -> str:
        """Analyze three middle fingers extended (index, middle, ring)."""
        index_tip = landmarks[self.INDEX_TIP]
        middle_tip = landmarks[self.MIDDLE_TIP]
        ring_tip = landmarks[self.RING_TIP]
        wrist = landmarks[self.WRIST]
        
        # Check if pointing upward (Number 3)
        avg_y = (index_tip['y'] + middle_tip['y'] + ring_tip['y']) / 3
        if avg_y < wrist['y']:
            return "Number 3"
        else:
            return "Three Fingers Extended"


class FourFingerInterpreter(BaseGestureInterpreter):
    """Interpreter for ASL gestures with 4 fingers up."""
    
    def interpret(self, landmarks: List[Dict], fingers_up: List[bool], handedness: str,
                  face_ref: Optional[Dict] = None) -> str:
        """Interpret four-finger ASL gestures."""
        if not fingers_up[0]:  # All except thumb (Number 4 or Letter B)
            return self._analyze_four_no_thumb(landmarks)
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
    
    def _analyze_four_no_thumb(self, landmarks: List[Dict]) -> str:
        """Analyze four fingers without thumb (common ASL gesture)."""
        wrist = landmarks[self.WRIST]
        index_tip = landmarks[self.INDEX_TIP]
        
        # Check if fingers pointing upward
        if index_tip['y'] < wrist['y']:
            # Check if fingers are spread (Number 4)
            finger_tips = [landmarks[i] for i in [8, 12, 16, 20]]
            total_spread = sum([
                self._calculate_distance(finger_tips[i], finger_tips[i+1]) 
                for i in range(len(finger_tips)-1)
            ])
            
            if total_spread > 0.15:
                return "Number 4"
        else:
            return "Four Fingers Extended"


class FiveFingerInterpreter(BaseGestureInterpreter):
    """Interpreter for ASL gestures with 5 fingers up (open hand)."""
    
    def interpret(self, landmarks: List[Dict], fingers_up: List[bool], handedness: str,
                  face_ref: Optional[Dict] = None) -> str:
        """Interpret five-finger ASL gestures."""
        return self._analyze_open_hand(landmarks, face_ref)
    
    def _analyze_open_hand(self, landmarks: List[Dict], face_ref: Optional[Dict] = None) -> str:
        """Analyze open hand gestures for ASL meanings with face reference."""
        palm_orientation = self._check_palm_orientation(landmarks)
        hand_openness = self._get_hand_openness(landmarks, [True]*5)
        wrist = landmarks[self.WRIST]
        middle_tip = landmarks[self.MIDDLE_TIP]
        
        # If we have face reference, use it for better detection
        if face_ref:
            # Check if hand is near mouth (THANK YOU)
            if face_ref.get('mouth'):
                dist_to_mouth = self._calculate_distance_to_face(middle_tip, face_ref['mouth'])
                if dist_to_mouth < 0.12:  # Very close to mouth
                    return "THANK YOU (near mouth, motion needed)"
            
            # Check if hand is near chin/chest area (PLEASE)
            if face_ref.get('chin'):
                dist_to_chin = self._calculate_distance_to_face(middle_tip, face_ref['chin'])
                if 0.12 < dist_to_chin < 0.25:  # Between mouth and chest
                    return "PLEASE (chest area, motion needed)"
            
            # Check if hand is near forehead (HELLO)
            if face_ref.get('forehead'):
                dist_to_forehead = self._calculate_distance_to_face(middle_tip, face_ref['forehead'])
                if dist_to_forehead < 0.15 and palm_orientation == "away":
                    return "HELLO / HI (near forehead)"
        
        # Fallback to position-based detection if no face reference
        # Upper region suggests "Hello" or "Stop"
        if middle_tip['y'] < 0.3:
            if palm_orientation == "away":
                return "HELLO / HI"
            else:
                return "STOP / WAIT"
        
        # Middle region near chest could be "Please" or "Thank You" (motion needed)
        elif 0.3 < middle_tip['y'] < 0.6:
            return "Open Hand (PLEASE/THANK YOU need motion)"
        
        # Check if hand is very spread (Number 5)
        elif hand_openness > 0.15:
            return "Number 5"
        
        # General open hand
        return "Open Hand"


class GestureInterpreterFactory:
    """Factory class to create appropriate ASL gesture interpreters."""
    
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
                         finger_count: int, handedness: str, 
                         face_ref: Optional[Dict] = None) -> str:
        """
        Interpret ASL gesture using the appropriate interpreter.
        
        Args:
            landmarks: Hand landmark positions
            fingers_up: Which fingers are extended
            finger_count: Total number of fingers up
            handedness: Left or Right hand
            face_ref: Optional face reference points dict with keys:
                     'nose', 'mouth', 'chin', 'forehead'
        """
        interpreter = self.get_interpreter(finger_count)
        return interpreter.interpret(landmarks, fingers_up, handedness, face_ref)
    
    def get_supported_gestures(self) -> Dict[str, List[str]]:
        """
        Get a dictionary of all supported ASL gestures organized by category.
        
        Returns:
            Dictionary with categories and their supported gestures
        """
        return {
            "Numbers": [
                "Number 1 (index finger up)",
                "Number 2 (index + middle fingers, V-shape)",
                "Number 3 (index + middle + ring fingers)",
                "Number 4 (four fingers spread, thumb tucked)",
                "Number 5 (all fingers spread)",
                "Number 10 (thumbs up / GOOD)"
            ],
            "Common Words & Phrases": [
                "HELLO / HI (open hand raised, palm out)",
                "GOODBYE (wave hand - needs motion)",
                "THANK YOU (hand from lips moving forward - needs motion)",
                "PLEASE (hand circular motion on chest - needs motion)",
                "SORRY (fist circular on chest - needs motion)",
                "I LOVE YOU (thumb + index + pinky extended)",
                "YES (fist nodding - needs motion)",
                "NO (fingers closing - needs motion)",
                "STOP (palm facing out)",
                "WAIT (palm facing out)",
                "GOOD (thumbs up / Number 10)",
                "BAD (thumbs down)",
                "OK / FINE (thumb + index circle)",
                "PEACE (index + middle V-shape)"
            ],
            "Everyday Needs": [
                "HELP (fist on palm, lift together - needs motion)",
                "EAT (fingertips to mouth - needs motion)",
                "DRINK (C-shape to mouth - needs motion)",
                "WATER (fingers at chin - needs motion)",
                "BATHROOM (shaking hand - needs motion)",
                "MORE (fingertips together - needs motion)",
                "WANT (hands pulling toward body - needs motion)",
                "NEED (downward motion - needs motion)",
                "GO (pointing forward - needs motion)",
                "COME (pointing inward - needs motion)",
                "CALL ME (thumb + pinky extended)",
                "POINTING (index finger extended)"
            ],
            "Note": [
                "Signs marked with 'needs motion' require movement tracking.",
                "This version recognizes static hand shapes and positions.",
                "For full ASL communication, consider upgrading to MediaPipe Holistic",
                "to track facial expressions and body language, which are crucial in ASL.",
                "Alphabet letters have been removed to focus on practical communication words."
            ]
        }