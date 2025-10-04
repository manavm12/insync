# Project Structure

```
hand-landmarks-detection/
├── README.md                           # Main project documentation
├── LICENSE                            # MIT License
├── CONTRIBUTING.md                    # Contribution guidelines
├── CHANGELOG.md                       # Version history
├── PROJECT_STRUCTURE.md               # This file
├── requirements.txt                   # Python dependencies
├── setup.py                          # Package setup configuration
├── .gitignore                        # Git ignore rules
├── activate_env.sh                   # Environment activation script
│
├── hand_landmarks_detector.py         # Core detection class
├── camera_gesture_detection.py       # Real-time camera detection
├── example_usage.py                  # Interactive examples
├── test_camera.py                    # Camera testing utility
│
└── docs/                             # Additional documentation (optional)
    ├── API.md                        # API reference
    ├── EXAMPLES.md                   # Usage examples
    └── TROUBLESHOOTING.md            # Common issues and solutions
```

## File Descriptions

### Core Files

- **`hand_landmarks_detector.py`** - Main detection engine with `HandLandmarksDetector` class
- **`camera_gesture_detection.py`** - Real-time camera processing with `RealTimeGestureDetector` class
- **`example_usage.py`** - Interactive menu system with various usage examples
- **`test_camera.py`** - Quick camera connection and functionality testing

### Configuration Files

- **`requirements.txt`** - Python package dependencies with specific versions
- **`setup.py`** - Package installation and distribution configuration
- **`.gitignore`** - Files and directories to exclude from version control
- **`activate_env.sh`** - Convenience script for environment activation

### Documentation

- **`README.md`** - Comprehensive project overview, installation, and usage guide
- **`LICENSE`** - MIT License for open source distribution
- **`CONTRIBUTING.md`** - Guidelines for contributors
- **`CHANGELOG.md`** - Version history and release notes
- **`PROJECT_STRUCTURE.md`** - This file describing project organization

## Key Components

### HandLandmarksDetector Class
- Image processing (`detect_landmarks_image`)
- Video processing (`detect_landmarks_video`) 
- Live stream processing (`detect_landmarks_live`)
- Landmark visualization (`draw_landmarks`)
- Gesture analysis (`get_gesture_landmarks`)

### RealTimeGestureDetector Class
- Real-time camera integration
- Live gesture recognition
- Interactive controls and feedback
- Data export capabilities
- Performance optimization

### Utility Functions
- Distance calculations between landmarks
- Finger extension detection
- Basic gesture recognition algorithms
- Data formatting and export tools

## Usage Patterns

1. **Quick Testing**: `python test_camera.py`
2. **Real-time Detection**: `python camera_gesture_detection.py`
3. **Interactive Examples**: `python example_usage.py`
4. **Custom Integration**: Import classes in your own scripts

## Development Workflow

1. Activate environment: `source hand_detection_env/bin/activate`
2. Make changes to source files
3. Test with provided scripts
4. Update documentation if needed
5. Commit changes with clear messages
