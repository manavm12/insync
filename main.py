#!/usr/bin/env python3
"""
Main entry point for Hand Landmarks Detection System

This script provides a simple interface to run the hand detection system.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hand_landmarks import RealTimeGestureDetector


def main():
    """Main function to run the hand detection system."""
    print("🚀 Hand Landmarks Detection System")
    print("=" * 40)
    print("Starting real-time gesture detection...")
    print("Press 'q' to quit, 's' to save landmarks, SPACE for analysis")
    print("=" * 40)
    
    try:
        detector = RealTimeGestureDetector()
        detector.start_detection(
            show_video=True,
            print_landmarks=True,
            save_to_file=False
        )
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
