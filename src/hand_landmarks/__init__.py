"""
Hand Landmarks Detection Package

A comprehensive hand gesture recognition system using MediaPipe.
Provides real-time detection of hand landmarks and advanced gesture recognition.
"""

from .hand_landmarks_detector import HandLandmarksDetector, recognize_basic_gestures
from .gesture_recognition import GestureRecognizer, recognize_advanced_gestures
from .camera_gesture_detection import RealTimeGestureDetector
from .holistic_detector import HolisticDetector

__version__ = "2.0.0"
__author__ = "Hand Landmarks Detection Team"
__email__ = "contact@handlandmarks.com"

__all__ = [
    "HandLandmarksDetector",
    "HolisticDetector",
    "recognize_basic_gestures", 
    "GestureRecognizer",
    "recognize_advanced_gestures",
    "RealTimeGestureDetector"
]
