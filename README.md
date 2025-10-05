# Insync Hand Gesture Interpreter

A real-time system that turns webcam hand gestures into natural language and optional speech. MediaPipe detects hands, custom logic recognizes conversational gestures, OpenAI shapes sentences, and ElevenLabs (optional) speaks them aloud. DeepFace can annotate the dominant emotion in-frame.

## Features

- Live gesture recognition using MediaPipe Hands with configurable smoothing.
- Sentence emits after consensus and auto-closes when 5 seconds pass with no new gestures or when all hands leave the frame.
- OpenAI-powered translation with customizable prompt/context.
- Optional DeepFace emotion overlay and logging.
- Optional ElevenLabs TTS with background queue and playback controls.
- Hotkeys for toggling logs, forcing sentences, saving landmarks, and cancelling audio.

## Requirements

- Python 3.9+ recommended.
- Webcam.
- `OPENAI_API_KEY` (env/.env) for translation.
- Optional `XI_API_KEY` for ElevenLabs TTS.
- Optional DeepFace (installed by default) for emotion detection.

`requirements.txt` includes mediapipe, opencv-python, numpy, deepface, protobuf<4.0.0, openai, python-dotenv, plus dev tools (pytest, black, flake8, isort).

## Setup

```bash
git clone <repo>
cd insync

python3 -m venv venv
source venv/bin/activate          # Windows PowerShell: .\venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt

# optional if using ElevenLabs TTS
pip install elevenlabs
```

Populate `.env`:

```
OPENAI_API_KEY=sk-...
XI_API_KEY=...          # optional
XI_VOICE_ID=...         # optional voice preset
SPEAKER_ROLE=...        # optional prompt context
```

## Running

```bash
source venv/bin/activate
python main.py
```

Window controls:

- `q` quit
- `s` save snapshot of current landmarks
- `p` toggle console landmark logging (set `detector.console_landmark_logging = True` to enable output)
- `t` toggle translation log lines
- `r` toggle raw gesture log lines
- `c` clear sentences and queues
- `n` force sentence completion
- `x` cancel audio & clear playback queue
- `SPACE` print detailed frame analysis

## Runtime Pipeline

1. Webcam frames are mirrored and processed by MediaPipe Hands (and optional Holistic for face points).
2. Gesture smoothing (window=9, consensus=0.6, cooldown=0.5 s, hold=0.25 s) filters jitter before emitting words.
3. If no gestures change for 5 s, or if no hands are detected, the sentence finalizes and queues for translation and TTS.
4. The OpenAI prompt reshapes gesture tokens into a natural sentence; empty/unknown input results in silence.
5. ElevenLabs (if configured) synthesizes speech asynchronously and plays it via the audio worker.
6. DeepFace (if enabled) updates the overlay every `emotion_interval` frames and logs the dominant emotion.

## Customising the Translator

Edit `src/hand_landmarks/gesture_translator.py` to embed contextual prompts. Example:

```python
CUSTOM_CONTEXT = """
Context:
- Speaker: emergency triage nurse
- Preferred terms: patient, appointment, medication
- Custom sign overrides: thumb-to-cheek → "patient"
"""

system_prompt = build_system_prompt(CUSTOM_CONTEXT)
```

Pass new context strings into `fix_sentence` when needed.

## Sensitivity Tuning

You can adjust the following in `RealTimeGestureDetector.__init__`:

- `gesture_window_size`
- `gesture_min_consensus`
- `gesture_cooldown_seconds`
- `gesture_transition_min_frames`
- `gesture_confidence_threshold`
- `gesture_margin_threshold`
- `gesture_pending_hold_seconds`

Smaller values make recognition more responsive; larger ones reject noise.

## Emotion Overlay

- Controlled by `self.emotion_detection_enabled` (auto-true if DeepFace imports).
- Runs every `emotion_interval` frames (default 15).
- Shows a bounding box with the dominant emotion label and confidence.

## Troubleshooting

- **Webcam not detected**: ensure no other app uses the camera; try `camera_id=1`.
- **Sentence never ends**: stay still or remove hands for ≥5 s; unknown gestures no longer reset the timer.
- **OpenAI/permission errors**: check `.env`, verify network access.
- **DeepFace protobuf crash**: reinstall protobuf 3.20.x (`pip install protobuf==3.20.3`).
- **ElevenLabs missing**: install the SDK and set `XI_API_KEY`, or disable autoplay (`detector.enable_auto_play(False)`).

## Project Structure

- `src/hand_landmarks/camera_gesture_detection.py` – main application, smoothing, translation pipeline, emotion & TTS wrappers.
- `src/hand_landmarks/gesture_recognition.py` – detailed gesture analytics utilities.
- `src/hand_landmarks/gesture_interpreters.py` – rule-based gesture classifiers.
- `src/hand_landmarks/gesture_translator.py` – OpenAI translator/prompt helper.
- `src/hand_landmarks/hand_landmarks_detector.py` – MediaPipe Hands wrapper.
- `main.py` – entry point.

## License

MIT License – see `LICENSE`.
