# InSync Web Application

A modern web-based interface for the InSync gesture detection system, providing real-time camera feed, gesture recognition, and custom word mapping capabilities.

## Features

### 🎥 Real-time Camera Interface

- Live camera feed with hand landmark detection
- Real-time gesture recognition and display
- Current sentence building display
- Translation results with TTS playback

### ⚙️ Custom Gesture Mappings

- Map your own words/phrases to any available gesture
- Visual interface for selecting gestures
- Save and manage custom mappings
- Persistent storage of mappings

### 🔊 Text-to-Speech Integration

- Automatic TTS for translated sentences
- Manual TTS playback for any translation
- Audio queue management
- ElevenLabs integration

### 📱 Modern Web Interface

- Responsive design for desktop and mobile
- Real-time updates via WebSocket
- Intuitive controls and status indicators
- Beautiful, modern UI with smooth animations

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Required for OpenAI translation
export OPENAI_API_KEY="your_openai_api_key"

# Optional for TTS (ElevenLabs)
export XI_API_KEY="your_elevenlabs_api_key"
export XI_VOICE_ID="your_voice_id"
```

### 3. Start the Web Application

```bash
python start_web_app.py
```

### 4. Open Your Browser

Navigate to: http://localhost:5000

## Usage

### Camera Interface (`/`)

1. **Start Camera**: Click "🎥 Start Camera" to begin gesture detection
2. **Gesture Recognition**: Perform gestures in front of the camera
3. **Sentence Building**: Watch as gestures are added to the current sentence
4. **Translation**: Sentences are automatically sent to OpenAI for translation
5. **TTS Playback**: Click "🔊 Play" on any translation to hear the audio

### Custom Mappings (`/mappings`)

1. **Select Gesture**: Click on any available gesture from the left panel
2. **Enter Custom Word**: Type your custom word or phrase
3. **Save Mapping**: Click "💾 Save Mapping" to store the mapping
4. **Manage Mappings**: View, edit, or delete existing custom mappings

## Available Gestures

The system recognizes a wide variety of ASL gestures including:

### Numbers

- Number 1-5 (finger counting)
- Thumbs up/down (GOOD/BAD)

### Common Words & Phrases

- HELLO/HI, GOODBYE, THANK YOU, PLEASE
- YES, NO, STOP, WAIT
- I LOVE YOU, OK/FINE, PEACE

### Everyday Needs

- HELP, EAT, DRINK, WATER
- BATHROOM, MORE, WANT, NEED
- GO, COME, CALL ME, POINTING

## API Endpoints

### Camera Control

- `POST /api/start_detection` - Start gesture detection
- `POST /api/stop_detection` - Stop gesture detection
- `GET /video_feed` - Live camera stream

### Sentence Management

- `GET /api/current_sentence` - Get current sentence being built
- `POST /api/force_sentence` - Force completion of current sentence
- `POST /api/clear_sentences` - Clear all sentences and translations

### Translations

- `GET /api/translations` - Get recent translations
- `POST /api/play_tts/<id>` - Play TTS for specific translation

### Custom Mappings

- `GET /api/gestures` - Get all available gestures
- `GET /api/mappings` - Get current custom mappings
- `POST /api/mappings` - Save custom mappings
- `DELETE /api/mappings/<gesture>` - Delete custom mapping

## WebSocket Events

### Client → Server

- `connect` - Client connection
- `disconnect` - Client disconnection
- `request_update` - Request current status update

### Server → Client

- `status` - General status messages
- `sentence_update` - Current sentence and translation updates

## Configuration

### Environment Variables

- `OPENAI_API_KEY` - Required for text translation
- `XI_API_KEY` - ElevenLabs API key for TTS
- `XI_VOICE_ID` - ElevenLabs voice ID for TTS

### Custom Mappings Storage

Custom mappings are stored in `custom_gesture_mappings.json` in the project root.

## Troubleshooting

### Camera Issues

- Ensure camera is not being used by another application
- Check camera permissions in your browser
- Try different camera IDs if multiple cameras are available

### Translation Issues

- Verify `OPENAI_API_KEY` is set correctly
- Check internet connection
- Monitor console for API error messages

### TTS Issues

- Verify `XI_API_KEY` and `XI_VOICE_ID` are set
- Check ElevenLabs account status and credits
- Ensure audio output is working on your system

### Performance Issues

- Close other applications using the camera
- Reduce browser tab count
- Check system resources (CPU, memory)

## Development

### Project Structure

```
insync/
├── web_app.py              # Main Flask application
├── start_web_app.py        # Startup script
├── templates/
│   ├── index.html          # Camera interface
│   └── mappings.html       # Custom mappings interface
├── custom_gesture_mappings.json  # Custom mappings storage
└── src/                    # Core gesture detection system
```

### Adding New Features

1. Modify `web_app.py` for backend functionality
2. Update HTML templates for UI changes
3. Add new API endpoints as needed
4. Update WebSocket events for real-time features

## Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

Note: WebRTC camera access requires HTTPS in production environments.

## Security Notes

- The application runs on all interfaces (`0.0.0.0`) by default
- For production use, consider:
  - Running behind a reverse proxy (nginx, Apache)
  - Using HTTPS with SSL certificates
  - Implementing authentication if needed
  - Restricting network access as appropriate

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the main InSync documentation
3. Check browser console for error messages
4. Verify all dependencies are properly installed
