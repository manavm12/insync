# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-10-04

### Added

- Initial release of Hand Landmarks Detection system
- Real-time hand tracking using MediaPipe
- Support for image, video, and live stream processing
- 21-point hand landmark detection
- Handedness detection (left/right hand identification)
- Basic gesture recognition (Open Hand, Fist, Pointing, Peace Sign, Thumbs Up)
- Multiple hand detection support (up to 2 hands)
- Live video feed with landmark visualization
- Landmark data export to JSON files
- Comprehensive example scripts and usage demonstrations
- Cross-platform compatibility (macOS, Windows, Linux)
- Detailed documentation and setup instructions

### Features

- `HandLandmarksDetector` class for core functionality
- `RealTimeGestureDetector` for live camera processing
- Interactive example menu system
- Camera permission handling
- Performance optimizations for real-time processing
- Configurable detection parameters
- Detailed landmark analysis tools

### Documentation

- Complete README with installation and usage instructions
- API reference documentation
- Contributing guidelines
- Example code and tutorials
- Troubleshooting guide

### Dependencies

- MediaPipe 0.10.9
- OpenCV 4.8.1.78
- NumPy 2.0.2
- Additional supporting libraries (matplotlib, protobuf, etc.)

## [2.0.0] - 2025-10-04

### 🤟 Major Update: ASL (American Sign Language) Interpreter

This release transforms the project into a comprehensive **real-time ASL interpreter** designed specifically for the hearing-impaired community.

### Added - ASL Recognition System

#### Core ASL Features

- **40+ ASL Signs Recognition**: Comprehensive vocabulary including numbers, letters, and common phrases
- **ASL-Specific Gesture Interpreters**: Specialized classes for each finger configuration
- **Hand Position Detection**: Recognizes hand location (near face, chest, etc.)
- **Palm Orientation Analysis**: Detects palm facing towards or away from camera
- **Static Hand Shape Recognition**: Full support for static ASL signs

#### ASL Vocabulary Categories

- **Numbers (0-10)**: All basic counting signs
- **ASL Alphabet**: 14 static letters (A, B, C, D, F, I, K, L, N, S, U, V, W, Y)
- **Common Phrases**: HELLO, GOODBYE, THANK YOU, PLEASE, SORRY, I LOVE YOU
- **Essential Words**: HELP, STOP, WAIT, GOOD, OK, YES, NO
- **Everyday Needs**: EAT, DRINK, WATER, BATHROOM, MORE, WANT, NEED, GO, COME
- **Emotions**: HAPPY, SAD, ANGRY, EXCITED

#### New Gesture Interpretation Classes

- `ZeroFingersInterpreter`: Recognizes closed fist signs (Letters A, S)
- `OneFingerInterpreter`: Single finger signs (Numbers 1, Letters D, I, L)
- `TwoFingerInterpreter`: Two finger combinations (Numbers 2, Letters F, V, Y)
- `ThreeFingerInterpreter`: Three finger signs (Numbers 3, Letter W, I LOVE YOU)
- `FourFingerInterpreter`: Four finger signs (Numbers 4, Letter B)
- `FiveFingerInterpreter`: Open hand signs (Numbers 5, HELLO, STOP)

#### Enhanced Base Interpreter

- `_check_palm_orientation()`: Determines palm direction
- `_get_hand_openness()`: Calculates finger spread
- `_are_fingertips_together()`: Detects touching fingertips
- `_is_hand_near_location()`: Identifies hand position in frame
- `_is_fist_on_chest()`: Detects chest-level gestures

### Enhanced

- **Gesture Recognition System**: Upgraded from basic to comprehensive ASL recognition
- **Real-Time Detection**: Improved output formatting with ASL-specific labels
- **Confidence Scoring**: Better hand shape matching algorithms
- **Multi-Hand Support**: Enhanced for ASL signs requiring both hands

### Documentation

- **Complete ASL Guide** (`docs/ASL_GUIDE.md`):
  - Full vocabulary reference
  - Usage instructions and tips
  - Troubleshooting guide
  - Future roadmap
  - Learning resources
- **Quick Reference Card** (`docs/ASL_QUICK_REFERENCE.md`):
  - Fast lookup tables for all signs
  - Visual descriptions
  - Recognition tips
  - Output interpretation guide
- **Updated README**: ASL-focused main documentation
- **Code Documentation**: Comprehensive inline documentation with ASL context

### Technical Improvements

- Modular gesture interpreter architecture
- Factory pattern for interpreter selection
- Enhanced landmark analysis algorithms
- Position-aware gesture recognition
- Orientation-dependent sign detection

### User Experience

- Clear ASL sign labels with `ASL:` prefix
- Motion requirement indicators
- Multiple interpretation suggestions
- Confidence scores for each detection
- Interactive controls for detailed analysis

### Notes

- **Static Hand Shapes**: Current version focuses on static ASL signs
- **Motion Tracking**: Planned for next release (will add 30+ signs)
- **Facial Expressions**: Critical ASL component planned for future update
- **Body Language**: Full holistic tracking planned

### Recognition Status

- ✅ **40+ Static Signs**: Fully recognized
- 🔄 **30+ Motion Signs**: Hand shapes detected, motion tracking needed
- 📍 **Position-Dependent**: Hand location matters for accurate recognition

## [1.0.0] - 2024-10-04

### Added

- Initial release of Hand Landmarks Detection system
- Real-time hand tracking using MediaPipe
- Support for image, video, and live stream processing
- 21-point hand landmark detection
- Handedness detection (left/right hand identification)
- Basic gesture recognition (Open Hand, Fist, Pointing, Peace Sign, Thumbs Up)
- Multiple hand detection support (up to 2 hands)
- Live video feed with landmark visualization
- Landmark data export to JSON files
- Comprehensive example scripts and usage demonstrations
- Cross-platform compatibility (macOS, Windows, Linux)
- Detailed documentation and setup instructions

### Features

- `HandLandmarksDetector` class for core functionality
- `RealTimeGestureDetector` for live camera processing
- Interactive example menu system
- Camera permission handling
- Performance optimizations for real-time processing
- Configurable detection parameters
- Detailed landmark analysis tools

### Documentation

- Complete README with installation and usage instructions
- API reference documentation
- Contributing guidelines
- Example code and tutorials
- Troubleshooting guide

### Dependencies

- MediaPipe 0.10.9
- OpenCV 4.8.1.78
- NumPy 2.0.2
- Additional supporting libraries (matplotlib, protobuf, etc.)

## [Unreleased]

### Planned - Future ASL Enhancements

#### High Priority

- **Motion Tracking**:
  - Temporal landmark tracking across frames
  - Velocity and direction calculation
  - Circular and linear motion patterns
  - Impact: +30 additional ASL signs

#### Critical Features

- **Facial Expression Recognition**:
  - Upgrade to MediaPipe Holistic
  - 468 facial landmarks
  - Eyebrow position detection (questions)
  - Mouth shape recognition
  - Impact: Essential for ASL grammar

#### Additional Improvements

- **Body Pose Estimation**: Full body tracking for context
- **Two-Hand Coordination**: Complex multi-hand signs
- **Context-Aware Interpretation**: Sentence building
- **Custom Sign Training**: User-defined gestures
- **Regional Variations**: Different ASL dialects
- **Performance Benchmarking**: Speed and accuracy metrics
- **Unit Test Suite**: Comprehensive testing
- **Web Interface**: Browser-based detection
- **Mobile App**: iOS and Android support
