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

## [Unreleased]

### Planned
- Advanced gesture recognition algorithms
- Hand pose estimation
- Sign language recognition
- Performance benchmarking tools
- Unit test suite
- Docker containerization
- Web interface for browser-based detection
