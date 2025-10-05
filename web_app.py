#!/usr/bin/env python3
"""
Web Application for Hand Gesture Detection System

A Flask web application that provides a modern web interface for the hand gesture detection system.
Features live camera streaming, real-time gesture detection, sentence building, and text-to-speech.
"""

import sys
import os
import json
import time
import base64
import cv2
import threading
from flask import Flask, render_template, jsonify, Response, request
from flask_cors import CORS
import numpy as np

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hand_landmarks import RealTimeGestureDetector

app = Flask(__name__)
CORS(app)

# Global detector instance
detector = None
detector_thread = None
detector_running = False

# Global state for web interface
web_state = {
    'current_gesture': 'None',
    'current_sentence': '',
    'recent_translations': [],
    'hand_landmarks': [],
    'hands_detected': 0,
    'audio_status': {'is_playing': False, 'current_audio': None},
    'system_status': 'stopped'
}

class WebGestureDetector:
    """Wrapper around RealTimeGestureDetector for web interface."""
    
    def __init__(self):
        self.detector = RealTimeGestureDetector(
            camera_id=0, 
            use_holistic=True, 
            auto_play_tts=True,
            tts_auto_enqueue_short_sentences=3
        )
        # Disable console landmark logging
        self.detector.console_landmark_logging = False
        self.running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
    def _play_audio_sync(self, audio_path):
        """Play audio synchronously using system audio player."""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["afplay", audio_path], check=True)
            elif system == "Linux":
                subprocess.run(["aplay", audio_path], check=True)
            elif system == "Windows":
                subprocess.run(["start", audio_path], shell=True, check=True)
            else:
                print(f"⚠️ Unsupported system for audio playback: {system}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Audio playback failed: {e}")
        except FileNotFoundError:
            print(f"❌ Audio file not found: {audio_path}")
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
    
    def cancel_current_audio(self):
        """Cancel current audio playback."""
        if hasattr(self.detector, 'cancel_current_audio'):
            self.detector.cancel_current_audio()
        
    def start(self):
        """Start the detection system."""
        global web_state
        
        try:
            # Initialize camera
            self.detector.cap = cv2.VideoCapture(self.detector.camera_id)
            
            if not self.detector.cap.isOpened():
                raise ValueError(f"Could not open camera with ID: {self.detector.camera_id}")
            
            # Set camera properties
            self.detector.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.detector.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.detector.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Start background threads
            self.detector._reset_sentence_system()
            self.detector._start_translation_thread()
            self.detector._start_tts_thread()
            self.detector._start_audio_thread()
            
            self.running = True
            web_state['system_status'] = 'running'
            
            print("🎥 Web camera system started successfully!")
            
        except Exception as e:
            print(f"❌ Error starting camera system: {e}")
            web_state['system_status'] = 'error'
            raise
    
    def stop(self):
        """Stop the detection system."""
        global web_state
        
        self.running = False
        web_state['system_status'] = 'stopped'
        
        if self.detector.cap:
            self.detector.cap.release()
        
        # Stop background threads
        self.detector.translation_running = False
        self.detector.tts_running = False
        self.detector.audio_running = False
        
        print("🛑 Web camera system stopped")
    
    def process_frame(self):
        """Process a single frame and update web state."""
        global web_state
        
        if not self.running or not self.detector.cap:
            return None
        
        ret, frame = self.detector.cap.read()
        if not ret:
            return None
        
        # Mirror the frame
        frame = cv2.flip(frame, 1)
        
        # Store current frame for streaming
        with self.frame_lock:
            self.current_frame = frame.copy()
        
        # Detection
        results = self.detector.detector.detect_landmarks_image(frame)
        gesture_data = self.detector.detector.get_gesture_landmarks(frame)
        
        # Import gesture recognition functions
        from hand_landmarks.hand_landmarks_detector import recognize_basic_gestures
        from hand_landmarks.gesture_recognition import recognize_advanced_gestures
        
        advanced_gestures = recognize_advanced_gestures(gesture_data)
        basic_gestures = recognize_basic_gestures(gesture_data)
        
        # Update sentence buffer
        self.detector._update_sentence_buffer(advanced_gestures)
        self.detector._check_sentence_timeout()
        
        # Update web state
        web_state['hands_detected'] = results['hands_detected']
        current_sentence = self.detector.get_current_sentence()
        web_state['current_sentence'] = current_sentence
        web_state['recent_translations'] = self.detector.get_recent_translations(5)
        web_state['audio_status'] = self.detector.get_audio_status()
        
        # Debug output for sentence building
        if current_sentence and current_sentence.strip():
            print(f"📝 Current sentence: '{current_sentence}'")
        
        # Update current gesture
        if advanced_gestures and len(advanced_gestures) > 0:
            primary_gesture = advanced_gestures[0]
            if isinstance(primary_gesture, dict):
                gesture_name = primary_gesture.get('gesture', 'Unknown')
                web_state['current_gesture'] = gesture_name
                print(f"🎯 Current gesture: {gesture_name}")  # Debug output
            else:
                web_state['current_gesture'] = str(primary_gesture)
        elif basic_gestures and len(basic_gestures) > 0:
            web_state['current_gesture'] = str(basic_gestures[0])
        else:
            web_state['current_gesture'] = 'None'
        
        # Update hand landmarks for visualization
        web_state['hand_landmarks'] = []
        for hand in results['hands']:
            hand_info = {
                'handedness': hand['handedness'],
                'confidence': hand['handedness_confidence'],
                'landmarks': []
            }
            
            for landmark in hand['landmarks']:
                hand_info['landmarks'].append({
                    'name': landmark['name'],
                    'x': landmark['x'],
                    'y': landmark['y'],
                    'z': landmark['z']
                })
            
            web_state['hand_landmarks'].append(hand_info)
        
        # Draw landmarks on frame
        annotated_frame = self.detector.detector.draw_landmarks(frame, results)
        
        # Add gesture information overlay
        if advanced_gestures:
            cv2.putText(annotated_frame, f"Gesture: {web_state['current_gesture']}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        if web_state['current_sentence']:
            cv2.putText(annotated_frame, f"Sentence: {web_state['current_sentence']}", 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        return annotated_frame
    
    def get_frame_for_streaming(self):
        """Get current frame for video streaming."""
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        return None

# Initialize detector
web_detector = WebGestureDetector()

def detection_loop():
    """Main detection loop running in background thread."""
    global detector_running
    
    detector_running = True
    
    try:
        web_detector.start()
        
        while detector_running and web_detector.running:
            try:
                web_detector.process_frame()
                time.sleep(0.033)  # ~30 FPS
            except Exception as e:
                print(f"❌ Frame processing error: {e}")
                time.sleep(0.1)
                
    except Exception as e:
        print(f"❌ Detection loop error: {e}")
        web_state['system_status'] = 'error'
    
    finally:
        web_detector.stop()
        detector_running = False

def generate_frames():
    """Generate frames for video streaming."""
    while True:
        frame = web_detector.get_frame_for_streaming()
        
        if frame is not None:
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.033)  # ~30 FPS

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def get_status():
    """Get current system status."""
    return jsonify(web_state)

@app.route('/api/start', methods=['POST'])
def start_detection():
    """Start the detection system."""
    global detector_thread, detector_running
    
    if not detector_running:
        detector_thread = threading.Thread(target=detection_loop, daemon=True)
        detector_thread.start()
        return jsonify({'status': 'started'})
    else:
        return jsonify({'status': 'already_running'})

@app.route('/api/stop', methods=['POST'])
def stop_detection():
    """Stop the detection system."""
    global detector_running
    
    detector_running = False
    web_detector.stop()
    return jsonify({'status': 'stopped'})

@app.route('/api/clear_sentences', methods=['POST'])
def clear_sentences():
    """Clear all sentences and translations."""
    if web_detector.running:
        web_detector.detector._clear_all_sentences()
    return jsonify({'status': 'cleared'})

@app.route('/api/force_sentence', methods=['POST'])
def force_sentence():
    """Force completion of current sentence."""
    if web_detector.running:
        web_detector.detector._force_new_sentence()
    return jsonify({'status': 'forced'})

@app.route('/api/cancel_audio', methods=['POST'])
def cancel_audio():
    """Cancel current audio playback."""
    if web_detector.running:
        web_detector.cancel_current_audio()
    return jsonify({'status': 'cancelled'})

@app.route('/api/speak_text', methods=['POST'])
def speak_text():
    """Speak custom text via TTS."""
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    if web_detector.running:
        try:
            # Add text directly to TTS queue
            tts_entry = {
                'id': int(time.time()),
                'text': text,
                'timestamp': time.time(),
                'status': 'queued',
                'voice_id': web_detector.detector.tts_voice_id
            }
            web_detector.detector.tts_queue.append(tts_entry)
            return jsonify({'status': 'queued', 'text': text})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'System not running'}), 400

if __name__ == '__main__':
    print("🚀 Hand Gesture Detection Web App")
    print("=" * 40)
    print("Starting Flask web server...")
    print("Open http://localhost:3000 in your browser")
    print("=" * 40)
    
    app.run(host='0.0.0.0', port=3000, debug=True, threaded=True)
