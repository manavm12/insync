# Real-Time ASL (American Sign Language) Interpreter 🤟

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.9-green.svg)](https://mediapipe.dev/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8.1-red.svg)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python implementation for **real-time American Sign Language (ASL) interpretation** using Google's MediaPipe framework. Designed to help the hearing-impaired communicate by recognizing common hand gestures and stringing them into coherent messages via OpenAI API calls. This project provides real-time hand tracking, ASL gesture recognition, and detailed landmark analysis capabilities.

**🎯 Primary Use Case**: Enable hearing-impaired individuals to sign into a camera and receive real-time text output of ASL keywords and phrases for effective communication.

## 🎯 Quick Demo

```bash
# Clone and setup
git clone <your-repo-url>
cd hand-landmarks-detection
python3 -m venv hand_detection_env
source hand_detection_env/bin/activate
pip install -r requirements.txt
pip install elevenlabs

# Start detecting!
python camera_gesture_detection.py
```

## ✨ ASL Features

### 🤟 Supported ASL Signs (30+)

- **Numbers 0-10**: All basic counting numbers in ASL
- **Common Phrases**: HELLO, GOODBYE, THANK YOU, PLEASE, SORRY, I LOVE YOU, PEACE
- **Essential Words**: HELP, STOP, WAIT, GOOD, BAD, OK, FINE, YES, NO, POINTING
- **Everyday Needs**: EAT, DRINK, WATER, BATHROOM, MORE, WANT, NEED, GO, COME, CALL ME

### 📊 Recognition Capabilities

- **Static Hand Shapes**: Fully recognizes 30+ practical ASL signs
- **Face Tracking** ✨ **NEW**: Tracks facial reference points (mouth, chin, forehead) for accurate detection of signs like THANK YOU
- **Distance-Based Detection**: Calculates hand proximity to face for improved accuracy
- **Hand Position Detection**: Identifies hand location relative to face and body
- **Palm Orientation**: Detects if palm faces towards or away from camera
- **Both Hands Support**: Can track and interpret both hands simultaneously
- **Real-time Output**: Instant ASL sign recognition with confidence scores
- **Practical Focus**: Emphasizes everyday communication words over alphabet spelling

See the **[ASL Guide](docs/ASL_GUIDE.md)** for complete vocabulary and **[Face Tracking Guide](docs/FACE_TRACKING.md)** for the new face tracking feature!

## 🔧 General Features

- **Multi-mode Detection**: Support for image, video, and live stream processing
- **Real-time Performance**: Optimized for real-time hand tracking from webcam
- **Detailed Landmark Data**: Returns 21 hand landmarks with normalized and pixel coordinates
- **Handedness Detection**: Identifies left/right hand with confidence scores
- **Practical ASL Recognition**: Built-in recognition for 30+ everyday ASL signs
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

### 🤟 ASL Interpreter Usage (Primary Use Case)

```python
from src.hand_landmarks import RealTimeGestureDetector

# Initialize ASL interpreter
detector = RealTimeGestureDetector(camera_id=0)

# Start real-time ASL sign recognition
detector.start_detection(
    show_video=True,
    print_landmarks=False,
    save_to_file=False
)
```

**Interactive Controls:**

- Press **'q'** to quit
- Press **'s'** to save current landmarks
- Press **SPACE** for detailed gesture analysis
- Press **'p'** to toggle landmark printing

**Example Output:**

```
Hand 1 (Right) - Confidence: 0.95
🎯 Gesture: ASL: I LOVE YOU
✋ Fingers: Thumb Index ❌ ❌ Pinky
```

### Basic Hand Landmark Detection

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

### Advanced ASL Gesture Recognition

```python
from src.hand_landmarks.gesture_recognition import recognize_advanced_gestures

# Get gesture data
gesture_data = detector.get_gesture_landmarks(image)

# Recognize ASL gestures
asl_gestures = recognize_advanced_gestures(gesture_data)

for gesture in asl_gestures:
    print(f"ASL Sign: {gesture['gesture']}")
    print(f"Confidence: {gesture['confidence']:.2f}")
    if gesture['number'] is not None:
        print(f"Number: {gesture['number']}")
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

| Parameter                  | Description                           | Default | Range     |
| -------------------------- | ------------------------------------- | ------- | --------- |
| `max_num_hands`            | Maximum number of hands to detect     | 2       | > 0       |
| `min_detection_confidence` | Minimum confidence for hand detection | 0.5     | 0.0 - 1.0 |
| `min_tracking_confidence`  | Minimum confidence for hand tracking  | 0.5     | 0.0 - 1.0 |
| `min_presence_confidence`  | Minimum confidence for hand presence  | 0.5     | 0.0 - 1.0 |

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

## 🤟 ASL Gesture Recognition System

The system includes comprehensive ASL sign recognition organized by hand shape:

### Recognized ASL Signs

#### **Numbers (0-10)**

- 0-5: Standard ASL counting numbers
- 10: Thumbs up / "GOOD"

#### **Common Words & Phrases**

- **Greetings**: HELLO, GOODBYE
- **Politeness**: THANK YOU, PLEASE, SORRY
- **Expressions**: I LOVE YOU, GOOD, BAD, OK, FINE, PEACE
- **Commands**: STOP, WAIT, HELP, POINTING
- **Questions**: YES, NO
- **Social**: CALL ME

#### **Everyday Communication**

- **Food & Drink**: EAT, DRINK, WATER
- **Actions**: MORE, WANT, NEED
- **Movement**: GO, COME
- **Facilities**: BATHROOM

#### **Emotions**

- HAPPY, SAD, ANGRY, EXCITED

### ASL Recognition Features

```python
from src.hand_landmarks.gesture_interpreters import GestureInterpreterFactory

# Get supported ASL vocabulary
factory = GestureInterpreterFactory()
supported_signs = factory.get_supported_gestures()

# Display all categories
for category, signs in supported_signs.items():
    print(f"\n{category}:")
    for sign in signs:
        print(f"  - {sign}")
```

### Custom Gesture Recognition

You can extend the ASL vocabulary by adding custom gestures:

```python
def custom_asl_sign_detector(landmarks):
    # Access specific landmarks
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]

    # Calculate distances, angles, palm orientation
    # Implement your ASL sign logic

    return "ASL: CUSTOM SIGN"
```

**Note**: Many ASL signs require motion tracking (e.g., THANK YOU, PLEASE). The current version detects hand shapes; motion detection will be added in future updates. See [ASL Guide](docs/ASL_GUIDE.md) for details on which signs need motion.

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

## ElevenLabs TTS integration (optional)

This project can synthesize translated sentences using ElevenLabs TTS. The TTS helper is implemented in `src/eleven_tts.py` and the detector will enqueue translated sentences for synthesis automatically.

Quick notes:

- Set your ElevenLabs API key in the environment: `XI_API_KEY` is required.
- Optionally set a default voice id in `XI_VOICE_ID` so you don't need to pass a voice id each time.
- The detector exposes two runtime options when constructing `RealTimeGestureDetector`:
  - `auto_play_tts` (bool): if True, plays the synthesized audio automatically after synthesis completes.
  - `tts_auto_enqueue_short_sentences` (int): sentences with word count <= this value are sent directly to TTS.

Example usage:

```python
from src.hand_landmarks.camera_gesture_detection import RealTimeGestureDetector

# autoplay and auto-enqueue sentences of 2 words or fewer
detector = RealTimeGestureDetector(auto_play_tts=True, tts_auto_enqueue_short_sentences=2)
detector.tts_voice_id = "XW70ikSsadUbinwLMZ5w"  # or set XI_VOICE_ID in env
detector.start_detection()
```

Environment variables (recommended)

Create a `.env` file (ignored by git) or export in your shell:

```
export XI_API_KEY="your_real_api_key"
export XI_VOICE_ID="your_preferred_voice_id"
```

If you don't set `XI_VOICE_ID`, you can still pass a `voice_id` to `synthesize_to_file` or set `detector.tts_voice_id` at runtime.

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

## 🚀 Future ASL Enhancements

### Planned Features

1. **Motion Tracking** (High Priority)

   - Track hand movements over time
   - Recognize signs like THANK YOU, PLEASE, SORRY
   - Detect circular, linear, and complex motions
   - **Impact**: +30 additional signs

2. **Facial Expression Recognition** (Critical for ASL)

   - Upgrade to MediaPipe Holistic
   - Detect eyebrow raises (questions)
   - Recognize mouth shapes
   - **Impact**: Essential for ASL grammar

3. **Body Pose Estimation**

   - Full body tracking
   - Context and emphasis detection
   - **Impact**: Better sign interpretation

4. **Two-Hand Coordination**

   - Simultaneous two-hand tracking
   - Complex two-hand signs
   - **Impact**: Double vocabulary potential

5. **Context-Aware Interpretation**
   - Sentence building from sign sequences
   - Grammar rules application
   - Natural conversation flow

See the [ASL Guide](docs/ASL_GUIDE.md) for detailed roadmap and technical specifications.

## 📚 Documentation

- **[ASL Guide](docs/ASL_GUIDE.md)** - Complete ASL vocabulary, usage tips, and troubleshooting
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - File organization and architecture
- **[Contributing](docs/CONTRIBUTING.md)** - Contribution guidelines
- **[Changelog](docs/CHANGELOG.md)** - Version history

## Support

If you encounter any issues or have questions:

1. Check the **[ASL Guide](docs/ASL_GUIDE.md)** for ASL-specific help
2. Review the troubleshooting section
3. Check the example usage
4. Check existing [issues](../../issues)
5. Create a new issue with detailed information

## 🙏 Acknowledgments

- **ASL Community**: Thank you to the deaf and hard-of-hearing community for their invaluable feedback and guidance

## CLI Usage

You can run the detector from the command line with these options:

```bash
python -m src.hand_landmarks.camera_gesture_detection --auto-play-tts --tts-short-threshold 2 --voice-id XW70ikSsadUbinwLMZ5w
```

- `--auto-play-tts`: automatically play synthesized audio
- `--tts-short-threshold N`: sentences with <= N words are auto-enqueued to TTS
- `--voice-id`: default ElevenLabs voice id to use

- **Sign Language Experts**: For helping ensure accurate ASL representation
- **Google MediaPipe team**: For the excellent hand tracking framework
- **OpenCV community**: For computer vision tools
- **Contributors and users**: For making this project better

---

**Happy signing! 🤟 Empowering communication for the hearing-impaired community.**
