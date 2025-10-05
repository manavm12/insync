# Hand Gesture Detection Web Application

A beautiful, modern web interface for the Hand Gesture Detection System that provides real-time ASL gesture recognition, sentence building, translation, and text-to-speech functionality.

## Features

🎥 **Live Camera Stream** - Real-time video feed with hand landmark visualization
🤟 **Gesture Recognition** - Advanced ASL gesture detection and recognition
📝 **Sentence Building** - Automatic sentence construction from gesture sequences
🌐 **Translation** - OpenAI-powered translation to proper English
🔊 **Text-to-Speech** - ElevenLabs integration for audio synthesis and playback
📱 **Responsive Design** - Modern, mobile-friendly interface
⚡ **Real-time Updates** - Live status updates and system monitoring

## Quick Start

### Option 1: Using the Startup Script (Recommended)
```bash
python3 start_web_app.py
```

### Option 2: Manual Setup
1. Install dependencies:
```bash
pip install flask flask-cors
```

2. Start the web application:
```bash
python3 web_app.py
```

3. Open your browser and navigate to: http://localhost:5000

## System Requirements

- Python 3.7+
- Webcam/Camera
- Internet connection (for OpenAI and ElevenLabs APIs)

### Required Environment Variables

For full functionality, set these environment variables:

```bash
# OpenAI API for translation
export OPENAI_API_KEY="your_openai_api_key_here"

# ElevenLabs API for text-to-speech
export XI_API_KEY="your_elevenlabs_api_key_here"
export XI_VOICE_ID="your_preferred_voice_id"  # Optional
```

## Web Interface Guide

### Main Dashboard

1. **Camera Feed** - Shows live video with hand landmark overlays
2. **Current Sentence** - Displays the sentence being built from gestures
3. **Recent Translations** - Shows the latest translated sentences
4. **Hand Landmarks** - Real-time hand landmark coordinates
5. **System Controls** - Start/stop detection and various controls

### Controls

- **Start/Stop** - Control the detection system
- **Complete Sentence** - Force completion of current sentence
- **Clear All** - Clear all sentences and translations
- **Cancel Audio** - Stop current audio playback
- **Custom Speech** - Enter custom text to speak via TTS

### Status Indicators

- **Green Badge** - System running normally
- **Red Badge** - System stopped
- **Yellow Badge** - System error or warning

## How It Works

1. **Detection** - MediaPipe detects hand landmarks in real-time
2. **Recognition** - Advanced algorithms recognize ASL gestures
3. **Sentence Building** - Gestures are combined into sentences with timeout handling
4. **Translation** - OpenAI API converts gesture sequences to proper English
5. **Speech** - ElevenLabs synthesizes and plays audio of translated sentences

## API Endpoints

The web application provides these REST API endpoints:

- `GET /` - Main web interface
- `GET /video_feed` - Live camera stream
- `GET /api/status` - Current system status
- `POST /api/start` - Start detection system
- `POST /api/stop` - Stop detection system
- `POST /api/clear_sentences` - Clear all sentences
- `POST /api/force_sentence` - Complete current sentence
- `POST /api/cancel_audio` - Cancel audio playback
- `POST /api/speak_text` - Speak custom text

## Troubleshooting

### Camera Issues
- Ensure your camera is not being used by another application
- Check camera permissions in your browser/system settings
- Try different camera IDs if you have multiple cameras

### API Issues
- Verify your OpenAI and ElevenLabs API keys are set correctly
- Check your internet connection
- Ensure you have sufficient API credits

### Performance Issues
- Close other applications using the camera
- Reduce browser tab usage for better performance
- Check system resources (CPU/Memory)

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│   Flask Server   │◄──►│  Detection Core │
│                 │    │                  │    │                 │
│ - HTML/CSS/JS   │    │ - REST API       │    │ - MediaPipe     │
│ - Real-time UI  │    │ - Video Stream   │    │ - Gesture Rec.  │
│ - Controls      │    │ - WebSocket      │    │ - Translation   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   External APIs  │
                       │                  │
                       │ - OpenAI         │
                       │ - ElevenLabs     │
                       └──────────────────┘
```

## Development

### File Structure
```
├── web_app.py              # Main Flask application
├── start_web_app.py        # Startup script
├── templates/
│   └── index.html          # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css       # Custom styles
│   └── js/
│       └── app.js          # Frontend JavaScript
└── src/                    # Core detection modules
    └── hand_landmarks/     # Hand detection components
```

### Customization

- **Styling**: Modify `static/css/style.css`
- **Frontend Logic**: Edit `static/js/app.js`
- **Backend API**: Update `web_app.py`
- **UI Layout**: Change `templates/index.html`

## License

This project is part of the Hand Gesture Detection System. Please refer to the main project license.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Verify all dependencies are installed
3. Ensure API keys are configured correctly
4. Check browser console for JavaScript errors
