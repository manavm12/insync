#!/usr/bin/env python3
"""
ASL Interpreter Demo Script

This script demonstrates the ASL (American Sign Language) recognition capabilities
of the hand landmarks detection system.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hand_landmarks.gesture_interpreters import GestureInterpreterFactory


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def show_supported_gestures():
    """Display all supported ASL gestures."""
    factory = GestureInterpreterFactory()
    supported = factory.get_supported_gestures()
    
    print_header("🤟 SUPPORTED ASL SIGNS")
    
    for category, signs in supported.items():
        print(f"\n📋 {category}:")
        print("-" * 70)
        for sign in signs:
            print(f"  • {sign}")
    
    print("\n" + "=" * 70)


def show_quick_tips():
    """Show quick tips for using the ASL interpreter."""
    print_header("💡 QUICK TIPS FOR BEST RECOGNITION")
    
    tips = [
        ("Lighting", "Ensure bright, even lighting on your hands"),
        ("Background", "Use a plain, contrasting background"),
        ("Distance", "Keep hands 1-2 feet from camera"),
        ("Position", "Center your hands in camera view"),
        ("Clarity", "Make distinct, deliberate hand shapes"),
        ("Hold", "Maintain position briefly for recognition")
    ]
    
    for topic, tip in tips:
        print(f"\n  {topic:12s}: {tip}")
    
    print("\n" + "=" * 70)


def show_demo_signs():
    """Show recommended signs to try first."""
    print_header("🎯 TRY THESE SIGNS FIRST")
    
    demo_signs = [
        ("Number 5", "Open hand, all fingers spread", "Easiest to recognize"),
        ("Number 1", "Index finger pointing up", "Simple and clear"),
        ("GOOD", "Thumb extended upward", "Thumbs up / Number 10"),
        ("PEACE", "Index + middle fingers in V", "Number 2 / Peace sign"),
        ("I LOVE YOU", "Thumb + index + pinky extended", "Iconic ASL sign"),
        ("OK", "Thumb + index forming circle", "OK / FINE sign"),
        ("STOP", "Open palm facing forward", "STOP / WAIT")
    ]
    
    print("\n  Recommended practice order:\n")
    for i, (sign, shape, note) in enumerate(demo_signs, 1):
        print(f"  {i}. {sign:15s} - {shape:35s} ({note})")
    
    print("\n" + "=" * 70)


def show_usage_instructions():
    """Show how to use the ASL interpreter."""
    print_header("🚀 HOW TO USE THE ASL INTERPRETER")
    
    print("""
  1. START THE INTERPRETER:
     
     Method 1 (Simple):
     $ python main.py
     
     Method 2 (Custom):
     $ python -c "from src.hand_landmarks import RealTimeGestureDetector; \\
                  RealTimeGestureDetector().start_detection()"
  
  2. INTERACTIVE CONTROLS:
     
     • Press 'q'     : Quit the application
     • Press 's'     : Save current hand landmarks
     • Press SPACE   : Show detailed gesture analysis
     • Press 'p'     : Toggle landmark printing
  
  3. READING THE OUTPUT:
     
     Example output:
     Hand 1 (Right) - Confidence: 0.95
     🎯 Gesture: ASL: I LOVE YOU
     ✋ Fingers: Thumb Index ❌ ❌ Pinky
     
     This shows:
     - Which hand was detected (Right)
     - Detection confidence (95%)
     - The recognized ASL sign (I LOVE YOU)
     - Which fingers are extended (Thumb, Index, Pinky)
  
  4. UNDERSTANDING OUTPUT LABELS:
     
     • "ASL: Number X"           - Counting number
     • "ASL: WORD"              - Common word/phrase
     • "ASL: X / Y"             - Multiple interpretations
     • "(needs motion)"         - Motion tracking required
     • Focus on practical communication, not alphabet spelling
    """)
    
    print("=" * 70)


def show_documentation_links():
    """Show links to documentation."""
    print_header("📚 DOCUMENTATION & RESOURCES")
    
    print("""
  📖 Complete Guides:
     • ASL Guide            : docs/ASL_GUIDE.md
     • Quick Reference      : docs/ASL_QUICK_REFERENCE.md
     • Update Summary       : docs/ASL_UPDATE_SUMMARY.md
     • Main README          : README.md
     • Changelog            : docs/CHANGELOG.md
  
  🌐 Online Resources:
     • Start ASL            : https://www.startasl.com
     • Lifeprint ASL        : https://www.lifeprint.com
     • HandSpeak            : https://www.handspeak.com
  
  🔧 Technical Info:
     • MediaPipe Hands      : https://google.github.io/mediapipe/solutions/hands.html
     • Project Structure    : docs/PROJECT_STRUCTURE.md
     • Contributing         : docs/CONTRIBUTING.md
    """)
    
    print("=" * 70)


def main():
    """Main demo function."""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║     🤟 ASL (American Sign Language) Interpreter Demo 🤟          ║")
    print("║                                                                   ║")
    print("║              Real-Time Sign Language Recognition                 ║")
    print("║           Designed for the Hearing-Impaired Community            ║")
    print("║                                                                   ║")
    print("║                      Version 2.0.0                                ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    
    # Show supported gestures
    show_supported_gestures()
    
    # Show quick tips
    show_quick_tips()
    
    # Show demo signs
    show_demo_signs()
    
    # Show usage instructions
    show_usage_instructions()
    
    # Show documentation links
    show_documentation_links()
    
    # Final message
    print("\n" + "=" * 70)
    print("  🎉 READY TO START!")
    print("=" * 70)
    print("""
  To begin ASL interpretation, run:
  
      python main.py
  
  This will start the camera and begin recognizing ASL signs in real-time!
  
  For detailed instructions, see: docs/ASL_GUIDE.md
    """)
    print("=" * 70)
    print("\n  Happy Signing! 🤟 Empowering communication for everyone.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo ended. See you soon!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

