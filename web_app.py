#!/usr/bin/env python3
"""
InSync Web Application
A Flask-based web interface for the InSync gesture detection system.
"""

import os
import sys
import json
import time
import threading
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit
import cv2
import base64
import io
from collections import deque

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hand_landmarks import RealTimeGestureDetector
from hand_landmarks.gesture_interpreters import GestureInterpreterFactory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'insync_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global detector instance
detector = None
gesture_mappings = {}
custom_mappings_file = 'custom_gesture_mappings.json'

# Load custom gesture mappings
def load_custom_mappings():
    global gesture_mappings
    if os.path.exists(custom_mappings_file):
        try:
            with open(custom_mappings_file, 'r') as f:
                gesture_mappings = json.load(f)
        except Exception as e:
            print(f"Error loading custom mappings: {e}")
            gesture_mappings = {}
    else:
        gesture_mappings = {}

def save_custom_mappings():
    try:
        with open(custom_mappings_file, 'w') as f:
            json.dump(gesture_mappings, f, indent=2)
    except Exception as e:
        print(f"Error saving custom mappings: {e}")

# Get all available gestures
def get_available_gestures():
    factory = GestureInterpreterFactory()
    return factory.get_supported_gestures()

@app.route('/')
def index():
    """Main page with camera interface."""
    return render_template('index.html')

@app.route('/mappings')
def mappings():
    """Custom gesture mapping page."""
    return render_template('mappings.html')

@app.route('/api/gestures')
def api_gestures():
    """Get all available gestures."""
    return jsonify(get_available_gestures())

@app.route('/api/mappings', methods=['GET'])
def api_get_mappings():
    """Get current custom gesture mappings."""
    return jsonify(gesture_mappings)

@app.route('/api/mappings', methods=['POST'])
def api_save_mappings():
    """Save custom gesture mappings."""
    global gesture_mappings
    data = request.json
    gesture_mappings.update(data)
    save_custom_mappings()
    return jsonify({"status": "success"})

@app.route('/api/mappings/<gesture>', methods=['DELETE'])
def api_delete_mapping(gesture):
    """Delete a custom gesture mapping."""
    global gesture_mappings
    if gesture in gesture_mappings:
        del gesture_mappings[gesture]
        save_custom_mappings()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Mapping not found"}), 404

@app.route('/api/start_detection', methods=['POST'])
def api_start_detection():
    """Start gesture detection."""
    global detector
    try:
        if detector is None:
            detector = RealTimeGestureDetector(
                camera_id=0,
                use_holistic=True,
                auto_play_tts=False  # We'll handle TTS in the web interface
            )
            detector._start_translation_thread()
            detector._start_tts_thread()
            detector._start_audio_thread()
        
        # Start camera
        if not detector.cap or not detector.cap.isOpened():
            detector.cap = cv2.VideoCapture(detector.camera_id)
            if not detector.cap.isOpened():
                return jsonify({"status": "error", "message": "Could not open camera"}), 500
            
            # Set camera properties
            detector.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            detector.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            detector.cap.set(cv2.CAP_PROP_FPS, 30)
        
        detector.running = True
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/stop_detection', methods=['POST'])
def api_stop_detection():
    """Stop gesture detection."""
    global detector
    try:
        if detector:
            detector.running = False
            if detector.cap:
                detector.cap.release()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/current_sentence')
def api_current_sentence():
    """Get current sentence being built."""
    if detector:
        return jsonify({"sentence": detector.get_current_sentence()})
    return jsonify({"sentence": ""})

@app.route('/api/translations')
def api_translations():
    """Get recent translations."""
    if detector:
        return jsonify({"translations": detector.get_recent_translations(10)})
    return jsonify({"translations": []})

@app.route('/api/force_sentence', methods=['POST'])
def api_force_sentence():
    """Force completion of current sentence."""
    if detector:
        detector._force_new_sentence()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Detector not initialized"}), 500

@app.route('/api/clear_sentences', methods=['POST'])
def api_clear_sentences():
    """Clear all sentences and translations."""
    if detector:
        detector._clear_all_sentences()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Detector not initialized"}), 500

@app.route('/api/play_tts/<int:translation_id>', methods=['POST'])
def api_play_tts(translation_id):
    """Play TTS for a specific translation."""
    if detector:
        # Find the translation and play its TTS
        for tts_result in detector.tts_results:
            if tts_result.get('id') == translation_id and tts_result.get('status') == 'completed':
                audio_path = tts_result.get('audio_path')
                if audio_path and os.path.exists(audio_path):
                    # Queue for audio playback
                    audio_entry = {
                        'id': translation_id,
                        'path': audio_path,
                        'timestamp': time.time(),
                        'text': tts_result.get('text', '')
                    }
                    detector.audio_queue.append(audio_entry)
                    return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "TTS not found or not ready"}), 404
    return jsonify({"status": "error", "message": "Detector not initialized"}), 500

def video_stream():
    """Generate video stream from camera."""
    global detector
    while True:
        if detector and detector.running and detector.cap and detector.cap.isOpened():
            ret, frame = detector.cap.read()
            if ret:
                # Mirror the frame
                frame = cv2.flip(frame, 1)
                
                # Detection
                results = detector.detector.detect_landmarks_image(frame)
                gesture_data = detector.detector.get_gesture_landmarks(frame)
                
                from hand_landmarks.gesture_recognition import recognize_advanced_gestures
                advanced_gestures = recognize_advanced_gestures(gesture_data)
                
                # Apply custom mappings
                for gesture_info in advanced_gestures:
                    gesture = gesture_info.get('gesture', '')
                    if gesture in gesture_mappings:
                        gesture_info['gesture'] = gesture_mappings[gesture]
                
                detector._update_sentence_buffer(advanced_gestures)
                detector._check_sentence_timeout()
                
                # Annotate frame
                annotated_frame = detector._annotate_frame_advanced(frame, results, advanced_gestures)
                
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', annotated_frame)
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            time.sleep(0.1)

@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('status', {'message': 'Connected to InSync'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')

@socketio.on('request_update')
def handle_update_request():
    """Handle request for current status update."""
    if detector:
        emit('sentence_update', {
            'sentence': detector.get_current_sentence(),
            'translations': detector.get_recent_translations(5),
            'audio_status': detector.get_audio_status()
        })

def background_updates():
    """Background thread to send updates to connected clients."""
    while True:
        if detector and detector.running:
            try:
                # Send sentence updates
                current_sentence = detector.get_current_sentence()
                recent_translations = detector.get_recent_translations(5)
                audio_status = detector.get_audio_status()
                
                socketio.emit('sentence_update', {
                    'sentence': current_sentence,
                    'translations': recent_translations,
                    'audio_status': audio_status
                })
            except Exception as e:
                print(f"Error in background updates: {e}")
        
        time.sleep(1)  # Update every second

if __name__ == '__main__':
    # Load custom mappings on startup
    load_custom_mappings()
    
    # Start background update thread
    update_thread = threading.Thread(target=background_updates, daemon=True)
    update_thread.start()
    
    # Run the app
    print("🚀 Starting InSync Web Application")
    print("📱 Open your browser to: http://localhost:5000")
    print("🎥 Camera interface: http://localhost:5000")
    print("⚙️  Gesture mappings: http://localhost:5000/mappings")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
