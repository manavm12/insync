#!/usr/bin/env python3
"""
Verification script to test the new project structure
"""

import sys
import os

def test_imports():
    """Test that all imports work with the new structure."""
    print("🧪 Testing imports with new structure...")
    
    try:
        # Add src to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # Test core imports
        from hand_landmarks import HandLandmarksDetector
        print("✅ HandLandmarksDetector imported successfully")
        
        from hand_landmarks import GestureRecognizer
        print("✅ GestureRecognizer imported successfully")
        
        from hand_landmarks import RealTimeGestureDetector
        print("✅ RealTimeGestureDetector imported successfully")
        
        from hand_landmarks import recognize_basic_gestures, recognize_advanced_gestures
        print("✅ Gesture recognition functions imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def check_file_structure():
    """Check that all files are in the correct locations."""
    print("\n📁 Checking file structure...")
    
    expected_structure = {
        'src/hand_landmarks/__init__.py': 'Package initialization',
        'src/hand_landmarks/hand_landmarks_detector.py': 'Core detection module',
        'src/hand_landmarks/gesture_recognition.py': 'Advanced gesture recognition',
        'src/hand_landmarks/camera_gesture_detection.py': 'Real-time camera processing',
        'tests/__init__.py': 'Test package init',
        'tests/test_camera.py': 'Camera testing',
        'tests/test_all_landmarks.py': 'Landmark testing',
        'tests/test_advanced_gestures.py': 'Gesture testing',
        'examples/__init__.py': 'Examples package init',
        'examples/example_usage.py': 'Usage examples',
        'docs/CONTRIBUTING.md': 'Contribution guidelines',
        'docs/CHANGELOG.md': 'Version history',
        'docs/PROJECT_STRUCTURE.md': 'Detailed structure',
        'scripts/activate_env.sh': 'Environment activation',
        'scripts/git_setup.sh': 'Git initialization',
        'scripts/git_ready_summary.sh': 'Git status summary',
        'main.py': 'Main entry point',
        'requirements.txt': 'Dependencies',
        'setup.py': 'Package setup',
        'README.md': 'Project documentation',
        'LICENSE': 'MIT License',
        '.gitignore': 'Git ignore rules'
    }
    
    missing_files = []
    for file_path, description in expected_structure.items():
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path} - {description}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing {len(missing_files)} files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print(f"\n🎉 All {len(expected_structure)} files found in correct locations!")
        return True


def main():
    """Run all verification tests."""
    print("🚀 Hand Landmarks Detection - Structure Verification")
    print("=" * 60)
    
    # Test imports
    imports_ok = test_imports()
    
    # Check file structure
    structure_ok = check_file_structure()
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    if imports_ok and structure_ok:
        print("🎉 SUCCESS: Project structure is properly organized!")
        print("\n✅ Ready to use:")
        print("   • Run main application: python main.py")
        print("   • Run tests: python tests/test_camera.py")
        print("   • Run examples: python examples/example_usage.py")
        print("   • Install package: pip install -e .")
        return 0
    else:
        print("❌ FAILED: Issues found with project structure")
        if not imports_ok:
            print("   • Import issues detected")
        if not structure_ok:
            print("   • Missing files detected")
        return 1


if __name__ == "__main__":
    sys.exit(main())
