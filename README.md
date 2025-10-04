# Hand Landmarks Detection with MediaPipe

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.9-green.svg)](https://mediapipe.dev/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8.1-red.svg)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python implementation for detecting and analyzing hand landmarks using Google's MediaPipe framework. This project provides real-time hand tracking, gesture recognition, and detailed landmark analysis capabilities.

## 🎯 Quick Demo

```bash
# Clone and setup
git clone <your-repo-url>
cd hand-landmarks-detection
python3 -m venv hand_detection_env
source hand_detection_env/bin/activate
pip install -r requirements.txt

# Start detecting!
python camera_gesture_detection.py
```

## Features

- **Multi-mode Detection**: Support for image, video, and live stream processing
- **Real-time Performance**: Optimized for real-time hand tracking from webcam
- **Detailed Landmark Data**: Returns 21 hand landmarks with normalized and pixel coordinates
- **Handedness Detection**: Identifies left/right hand with confidence scores
- **Basic Gesture Recognition**: Built-in recognition for common gestures
- **Multiple Hand Support**: Can detect and track multiple hands simultaneously
- **Export Capabilities**: Save landmark data and annotated images/videos

## Installation

### Prerequisites

- Python 3.7 or higher
- Webcam (for live detection)

### Setup

1. Clone or download the project files
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install mediapipe>=0.10.0 opencv-python>=4.8.0 numpy>=1.21.0
```

## Quick Start

### Basic Usage

```python
from hand_landmarks_detector import HandLandmarksDetector
import cv2

# Initialize detector
detector = HandLandmarksDetector()

# Load an image
image = cv2.imread('your_image.jpg')

# Detect landmarks
results = detector.detect_landmarks_image(image)

# Print results
print(f"Hands detected: {results['hands_detected']}")
for hand in results['hands']:
    print(f"Hand: {hand['handedness']} (confidence: {hand['handedness_confidence']:.3f})")
    print(f"Landmarks: {len(hand['landmarks'])}")
```

### Live Detection

```python
# Start live detection from webcam
detector = HandLandmarksDetector()
detector.detect_landmarks_live()
```

### Gesture Recognition

```python
# Get gesture data
gesture_data = detector.get_gesture_landmarks(image)

# Recognize basic gestures
from hand_landmarks_detector import recognize_basic_gestures
gestures = recognize_basic_gestures(gesture_data)
print(f"Recognized gestures: {gestures}")
```

## Detailed Usage

### 1. Image Processing

```python
import cv2
from hand_landmarks_detector import HandLandmarksDetector

detector = HandLandmarksDetector(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# Load and process image
image = cv2.imread('hand_image.jpg')
results = detector.detect_landmarks_image(image)

# Draw landmarks
annotated_image = detector.draw_landmarks(image, results)
cv2.imwrite('output_with_landmarks.jpg', annotated_image)
```

### 2. Video Processing

```python
# Process entire video file
results_list = detector.detect_landmarks_video(
    video_path='input_video.mp4',
    output_path='output_with_landmarks.mp4'
)

# Analyze results
for frame_result in results_list:
    print(f"Frame {frame_result['frame_number']}: {frame_result['hands_detected']} hands")
```

### 3. Live Stream Processing

```python
# Real-time detection with custom settings
detector = HandLandmarksDetector(
    max_num_hands=1,
    min_detection_confidence=0.8
)

detector.detect_landmarks_live(
    camera_id=0,  # Use default camera
    show_window=True
)
```

## Configuration Options

The `HandLandmarksDetector` class accepts the following parameters:

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `max_num_hands` | Maximum number of hands to detect | 2 | > 0 |
| `min_detection_confidence` | Minimum confidence for hand detection | 0.5 | 0.0 - 1.0 |
| `min_tracking_confidence` | Minimum confidence for hand tracking | 0.5 | 0.0 - 1.0 |
| `min_presence_confidence` | Minimum confidence for hand presence | 0.5 | 0.0 - 1.0 |

## Landmark Structure

Each detected hand provides 21 landmarks with the following information:

### Landmark Points
- **0**: Wrist
- **1-4**: Thumb (CMC, MCP, IP, TIP)
- **5-8**: Index finger (MCP, PIP, DIP, TIP)
- **9-12**: Middle finger (MCP, PIP, DIP, TIP)
- **13-16**: Ring finger (MCP, PIP, DIP, TIP)
- **17-20**: Pinky (MCP, PIP, DIP, TIP)

### Coordinate Systems
- **Normalized coordinates**: Values between 0.0 and 1.0 relative to image dimensions
- **Pixel coordinates**: Actual pixel positions in the image
- **Z-coordinate**: Depth information (relative to wrist)

### Data Structure

```python
{
    'hands_detected': 1,
    'hands': [
        {
            'hand_id': 0,
            'handedness': 'Left',
            'handedness_confidence': 0.98,
            'landmarks': [
                {
                    'id': 0,
                    'name': 'WRIST',
                    'x': 0.5,
                    'y': 0.6,
                    'z': 0.0
                },
                # ... 20 more landmarks
            ],
            'landmarks_pixel': [
                # Same structure but with pixel coordinates
            ]
        }
    ]
}
```

## Built-in Gesture Recognition

The system includes basic gesture recognition for:

- **Open Hand**: All fingers extended
- **Closed Fist**: All fingers closed
- **Pointing**: Only index finger extended
- **Peace Sign**: Index and middle fingers extended
- **Thumbs Up**: Only thumb extended

### Custom Gesture Recognition

You can extend the gesture recognition by analyzing landmark positions:

```python
def custom_gesture_detector(landmarks):
    # Access specific landmarks
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    
    # Calculate distances, angles, etc.
    # Implement your gesture logic
    
    return "Custom Gesture"
```

## Examples

Run the example script to see all features in action:

```bash
python example_usage.py
```

The example script includes:
1. Image detection demo
2. Video processing demo
3. Live detection demo
4. Gesture recognition demo
5. Detailed landmark analysis

## Performance Tips

1. **Reduce image resolution** for faster processing
2. **Adjust confidence thresholds** based on your use case
3. **Limit max_num_hands** if you only need single-hand detection
4. **Use static_image_mode=True** for single images (better accuracy)
5. **Process every nth frame** for video files to improve speed

## Troubleshooting

### Common Issues

1. **Camera not opening**:
   - Check if camera is being used by another application
   - Try different camera_id values (0, 1, 2, etc.)

2. **Poor detection accuracy**:
   - Ensure good lighting conditions
   - Adjust confidence thresholds
   - Make sure hands are clearly visible

3. **Slow performance**:
   - Reduce image resolution
   - Lower the frame rate
   - Process fewer hands

### Error Messages

- `Could not open camera with ID: X`: Camera not available or in use
- `Could not open video file: path`: Video file not found or corrupted
- `No hands detected`: Adjust lighting or confidence thresholds

## API Reference

### HandLandmarksDetector Class

#### Methods

- `detect_landmarks_image(image)`: Process single image
- `detect_landmarks_video(video_path, output_path)`: Process video file
- `detect_landmarks_live(camera_id, show_window)`: Real-time detection
- `draw_landmarks(image, results)`: Draw landmarks on image
- `get_gesture_landmarks(image)`: Get simplified gesture data

#### Utility Functions

- `calculate_distance(point1, point2)`: Calculate distance between landmarks
- `is_finger_extended(landmarks, tips, pips)`: Check if fingers are extended
- `recognize_basic_gestures(gesture_data)`: Basic gesture recognition

## 🔧 Development & Contributing

### Git Workflow

```bash
# Setup for development
./git_setup.sh                    # Initialize git and add files
git commit -m "Initial commit"    # Commit your changes
git checkout -b feature-branch    # Create feature branch
# Make your changes...
git add .
git commit -m "Add new feature"
git push origin feature-branch
```

### Project Structure
See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed file organization.

### Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## 📝 Changelog
See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:
1. Check the troubleshooting section
2. Review the example usage  
3. Check existing [issues](../../issues)
4. Create a new issue with detailed information

## 🙏 Acknowledgments

- Google MediaPipe team for the excellent hand tracking framework
- OpenCV community for computer vision tools
- Contributors and users of this project

---

**Happy hand tracking! 👋**
