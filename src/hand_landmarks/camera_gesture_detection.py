"""
Real-time Hand Gesture Detection with Camera
This script connects to your camera and detects hand gestures, returning landmark values in real-time.
"""

import cv2
import numpy as np
from typing import List, Optional, Dict
from .hand_landmarks_detector import HandLandmarksDetector, recognize_basic_gestures
from .holistic_detector import HolisticDetector
from .gesture_recognition import GestureRecognizer, recognize_advanced_gestures
from .gesture_translator import fix_sentence
import json
import time
import threading
import subprocess
import shutil
import sys
import argparse
from collections import deque, Counter
import os

class RealTimeGestureDetector:
    """Real-time gesture detection from camera with landmark output."""
    
    def __init__(self, camera_id=0, use_holistic=True, auto_play_tts: bool = False, tts_auto_enqueue_short_sentences: int = 3):
        """
        Initialize the real-time gesture detector.
        
        Args:
            camera_id: Camera device ID (usually 0 for default camera)
            use_holistic: If True, use Holistic detector (hand + face tracking)
                         for improved accuracy on signs like THANK YOU
        """
        self.camera_id = camera_id
        self.use_holistic = use_holistic

        if use_holistic:
            self.detector = HolisticDetector(min_detection_confidence=0.7, min_tracking_confidence=0.5)
            print("✨ Using Holistic detector (Hand + Face tracking enabled)")
        else:
            self.detector = HandLandmarksDetector(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.5)
            print("✋ Using standard hand detector")

        self.gesture_recognizer = GestureRecognizer()
        self.cap = None
        self.running = False

        # Sentence building and translation (plain assignments to avoid in-method annotations)
        self.current_sentence = []
        self.last_gesture = None
        self.last_gesture_time = 0
        self.sentence_timeout = 5.0  # seconds to complete a sentence

        # Translation queue and results
        self.sentence_queue = deque()
        self.translated_sentences = []
        self.translation_thread = None
        self.translation_running = False

        # TTS queue and results (sentences to send to ElevenLabs)
        self.tts_queue = deque()
        self.tts_results = []
        self.tts_thread = None
        self.tts_running = False

        # Audio playback queue and control for synchronous playback
        self.audio_queue = deque()
        self.audio_thread = None
        self.audio_running = False
        self.current_audio_playing = None
        self.audio_cancelled = False

        # Default voice id for ElevenLabs TTS; can be overridden via env or parameter
        self.tts_voice_id = os.getenv("XI_VOICE_ID")

        # Persistent ElevenLabs client (optional). If XI_API_KEY is set and the
        # official SDK is installed, instantiate a reusable client to avoid
        # creating a new connection for every synthesis request.
        self._eleven_client = None
        try:
            if os.getenv('XI_API_KEY'):
                from elevenlabs import ElevenLabs
                self._eleven_client = ElevenLabs(base_url="https://api.elevenlabs.io")
                print("🔁 ElevenLabs client initialized for TTS")
        except Exception:
            # Non-fatal: we'll fall back to the helper which itself will
            # attempt a lazy SDK import per-call if needed.
            self._eleven_client = None

        # Whether to auto-play synthesized TTS audio after synthesis completes
        # Can be toggled via constructor or the `enable_auto_play` method.
        self.auto_play_tts = bool(auto_play_tts)

        # (optional) If a completed sentence has <= this many words, it will
        # be auto-enqueued directly to TTS (bypassing translation)
        self.tts_auto_enqueue_short_sentences = int(tts_auto_enqueue_short_sentences or 0)

        # Display settings
        self.show_raw_gestures = True
        self.show_translations = True
        self.console_landmark_logging = False  # disable verbose landmark dumps by default

        # Gesture smoothing parameters
        self.gesture_window_size = 14
        self.gesture_min_consensus = 0.75
        self.gesture_cooldown_seconds = 0.8
        self.gesture_transition_min_frames = 5
        self.gesture_confidence_threshold = 0.75
        self.gesture_margin_threshold = 0.15
        self.gesture_pending_hold_seconds = 0.4
        self.gesture_pending_label = None
        self.gesture_pending_start = 0.0
        self.gesture_history = deque(maxlen=self.gesture_window_size)
        self.last_emitted_gesture_time = 0.0

    def enable_auto_play(self, enable: bool = True):
        """Toggle automatic playback of synthesized TTS audio."""
        self.auto_play_tts = bool(enable)
        
    def start_detection(self, show_video: bool = True, print_landmarks: bool = True, save_to_file: bool = False):
        """Start the real-time detection loop."""
        # Initialize camera
        self.cap = cv2.VideoCapture(self.camera_id)

        if not self.cap.isOpened():
            raise ValueError(f"Could not open camera with ID: {self.camera_id}")

        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        print("🎥 Camera connected successfully!")
        print("👋 Starting hand gesture detection...")
        print("\nControls:")
        print("  'q' - Quit")
        print("  's' - Save current landmarks to file")
        print("  'p' - Toggle landmark printing")
        print("  't' - Toggle translation display")
        print("  'r' - Toggle raw gesture display")
        print("  'c' - Clear all sentences and translations")
        print("  'n' - Force new sentence (don't wait for timeout)")
        print("  'x' - Cancel current audio and clear audio queue")
        print("  SPACE - Capture and analyze current frame")

        self._reset_sentence_system()
        self._start_translation_thread()
        self._start_tts_thread()
        self._start_audio_thread()
        self.running = True
        frame_count = 0

        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read from camera")
                    break

                # Mirror
                frame = cv2.flip(frame, 1)

                # Detection
                results = self.detector.detect_landmarks_image(frame)
                gesture_data = self.detector.get_gesture_landmarks(frame)

                advanced_gestures = recognize_advanced_gestures(gesture_data)
                basic_gestures = recognize_basic_gestures(gesture_data)
                self._update_sentence_buffer(advanced_gestures)
                self._check_sentence_timeout()

                # Process
                if results['hands_detected'] > 0:
                    if print_landmarks:
                        self._print_landmarks_advanced(results, advanced_gestures, frame_count)
                    if save_to_file:
                        self._save_landmarks_to_file(results, advanced_gestures, frame_count)

                if show_video:
                    annotated_frame = self._annotate_frame_advanced(frame, results, advanced_gestures)
                    cv2.imshow('Real-time Hand Gesture Detection', annotated_frame)

                # Keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self._save_current_landmarks(results, advanced_gestures)
                elif key == ord('p'):
                    print_landmarks = not print_landmarks
                    status = 'ON' if print_landmarks else 'OFF'
                    if print_landmarks and not self.console_landmark_logging:
                        status += " (enable detector.console_landmark_logging to see output)"
                    print(f"Landmark printing: {status}")
                elif key == ord('t'):
                    self.show_translations = not self.show_translations
                    print(f"Translation display: {'ON' if self.show_translations else 'OFF'}")
                elif key == ord('r'):
                    self.show_raw_gestures = not self.show_raw_gestures
                    print(f"Raw gesture display: {'ON' if self.show_raw_gestures else 'OFF'}")
                elif key == ord('c'):
                    self._clear_all_sentences()
                elif key == ord('n'):
                    self._force_new_sentence()
                elif key == ord('x'):
                    self.cancel_current_audio()
                elif key == ord(' '):
                    self._detailed_analysis_advanced(results, advanced_gestures)

                frame_count += 1

        except KeyboardInterrupt:
            print("\n🛑 Detection stopped by user")

        finally:
            self._cleanup()
    
    def get_current_landmarks(self):
        """
        Get landmarks from current camera frame (single capture).
        
        Returns:
            Dictionary with landmark data and gestures
        """
        if not self.cap or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camera_id)
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        frame = cv2.flip(frame, 1)
        results = self.detector.detect_landmarks_image(frame)
        gesture_data = self.detector.get_gesture_landmarks(frame)
        gestures = recognize_basic_gestures(gesture_data)
        
        return {
            'timestamp': time.time(),
            'landmarks': results,
            'gestures': gestures,
            'frame_shape': frame.shape
        }
    
    def get_all_landmarks_formatted(self):
        """
        Get all 21 landmarks in a clean, formatted structure.
        
        Returns:
            Dictionary with all landmark coordinates for each detected hand
        """
        landmarks_data = self.get_current_landmarks()
        if not landmarks_data or landmarks_data['landmarks']['hands_detected'] == 0:
            return None

        formatted_data = {
            'timestamp': landmarks_data['timestamp'],
            'hands_count': landmarks_data['landmarks']['hands_detected'],
            'hands': []
        }

        for hand in landmarks_data['landmarks']['hands']:
            hand_data = {
                'handedness': hand['handedness'],
                'confidence': hand['handedness_confidence'],
                'gesture': landmarks_data['gestures'][len(formatted_data['hands'])] if len(formatted_data['hands']) < len(landmarks_data['gestures']) else 'Unknown',
                'landmarks': {}
            }
            
            # Add all 21 landmarks with their names
            for landmark in hand['landmarks']:
                hand_data['landmarks'][landmark['name']] = {
                    'id': landmark['id'],
                    'x': landmark['x'],
                    'y': landmark['y'], 
                    'z': landmark['z']
                }
            
            formatted_data['hands'].append(hand_data)

        return formatted_data

    def _update_sentence_buffer(self, advanced_gestures):
        """Add new gesture word to current sentence when it changes."""
        if not advanced_gestures:
            self._register_gesture_observation('Unknown Gesture', confidence=0.0)
            return

        primary = advanced_gestures[0]
        new_word = primary.get('gesture') if isinstance(primary, dict) else None
        if not new_word:
            new_word = 'Unknown Gesture'

        confidence = None
        if isinstance(primary, dict):
            confidence = primary.get('confidence')

        self._register_gesture_observation(new_word, confidence)

    def _append_unknown_sign(self, timestamp: Optional[float] = None):
        """Record an unknown sign placeholder when recognition fails."""
        if self.last_gesture == 'Unknown Sign':
            return

        if timestamp is None:
            timestamp = time.time()

        self.last_gesture = None
        self.last_gesture_time = timestamp
        self.last_emitted_gesture_time = timestamp
        self.gesture_history.clear()
        self.gesture_pending_label = None
        self.gesture_pending_start = 0.0

        if self.show_raw_gestures:
            print("📝 Gesture: Unknown Sign")
            print(f"🔤 Current sentence: {' '.join(self.current_sentence)}")

    def _emit_gesture_word(self, word: str, timestamp: Optional[float] = None):
        if not word:
            return
        if timestamp is None:
            timestamp = time.time()

        if word:
            self.current_sentence.append(word)

        self.last_gesture = word
        self.last_gesture_time = timestamp
        self.last_emitted_gesture_time = timestamp
        self.gesture_history.clear()
        self.gesture_pending_label = None
        self.gesture_pending_start = 0.0

        if self.show_raw_gestures:
            print(f"📝 Gesture: {word}")
            print(f"🔤 Current sentence: {' '.join(self.current_sentence)}")

    def _register_gesture_observation(self, gesture_label: str, confidence: Optional[float] = None):
        timestamp = time.time()
        label = gesture_label or 'Unknown Gesture'

        if label != 'Unknown Gesture' and confidence is not None:
            try:
                if confidence < self.gesture_confidence_threshold:
                    label = 'Unknown Gesture'
            except Exception:
                label = 'Unknown Gesture'

        self.gesture_history.append(label)

        if len(self.gesture_history) < self.gesture_window_size:
            return

        candidate, ratio = self._get_gesture_consensus()
        if not candidate or ratio < self.gesture_min_consensus:
            return

        if not self._has_sufficient_margin(candidate):
            return

        if candidate == 'Unknown Gesture':
            if self._pending_confirmed(candidate, timestamp):
                self._append_unknown_sign(timestamp)
            return

        if timestamp - self.last_emitted_gesture_time < self.gesture_cooldown_seconds:
            return

        if candidate == self.last_gesture:
            return

        if not self._has_substantial_transition(candidate):
            return

        if not self._pending_confirmed(candidate, timestamp):
            return

        self._emit_gesture_word(candidate, timestamp)

    def _get_gesture_consensus(self):
        if not self.gesture_history:
            return None, 0.0

        counts = Counter(self.gesture_history)
        candidate, count = counts.most_common(1)[0]

        if candidate == 'Unknown Gesture' and len(counts) > 1:
            for label, cnt in counts.most_common():
                if label != 'Unknown Gesture' and cnt == count:
                    candidate, count = label, cnt
                    break

        ratio = count / len(self.gesture_history)
        return candidate, ratio

    def _has_sufficient_margin(self, candidate: str) -> bool:
        counts = Counter(self.gesture_history)
        top = counts.get(candidate, 0)
        if len(counts) == 1:
            return True
        second = 0
        for label, cnt in counts.most_common(2):
            if label != candidate:
                second = cnt
                break
        margin = (top - second) / len(self.gesture_history)
        return margin >= self.gesture_margin_threshold

    def _has_substantial_transition(self, candidate: str) -> bool:
        if self.last_gesture is None:
            return True
        if candidate == self.last_gesture:
            return False

        distinct_frames = sum(1 for label in self.gesture_history if label != self.last_gesture)
        return distinct_frames >= self.gesture_transition_min_frames

    def _pending_confirmed(self, candidate: str, timestamp: float) -> bool:
        if self.gesture_pending_label == candidate:
            if (timestamp - self.gesture_pending_start) >= self.gesture_pending_hold_seconds:
                return True
            return False

        self.gesture_pending_label = candidate
        self.gesture_pending_start = timestamp
        return False

    def _check_sentence_timeout(self):
        """Check if sentence should be completed due to timeout."""
        if not self.current_sentence:
            return
            
        current_time = time.time()
        if current_time - self.last_gesture_time >= self.sentence_timeout:
            self._complete_sentence()

    def _complete_sentence(self):
        """Complete current sentence and queue it for translation."""
        if not self.current_sentence:
            return
            
        sentence_text = ' '.join(self.current_sentence)
        print(f"\n✅ Sentence completed: '{sentence_text}'")
        # Centralized enqueue for translation (keeps id logic in one place)
        self._enqueue_sentence_for_translation(sentence_text)

        # Reset for next sentence
        self.current_sentence.clear()
        self.last_gesture = None

    def _enqueue_sentence_for_translation(self, sentence_text: str):
        """Create a sentence_data object and append to the translation queue.

        This central helper makes it easier to change id/timestamping or to add
        persistence/retry logic later.
        """
        sentence_data = {
            'id': len(self.translated_sentences) + len(self.sentence_queue) + 1,
            'raw_text': sentence_text,
            'timestamp': time.time(),
            'status': 'queued'
        }

        self.sentence_queue.append(sentence_data)
        print(f"📤 Queued for translation (Queue size: {len(self.sentence_queue)})")

    def _force_new_sentence(self):
        """Force completion of current sentence without waiting for timeout."""
        if self.current_sentence:
            print("🔄 Forcing sentence completion...")
            self._complete_sentence()
        else:
            print("ℹ️  No current sentence to complete")

    def _clear_all_sentences(self):
        """Clear all sentences and translations."""
        self.current_sentence.clear()
        self.sentence_queue.clear()
        self.translated_sentences.clear()
        self.last_gesture = None
        print("🗑️  Cleared all sentences and translations")

    def _reset_sentence_system(self):
        """Reset the entire sentence system."""
        self._clear_all_sentences()
        self.translation_running = False
        self.tts_running = False
        self.audio_running = False
        self.gesture_history.clear()
        self.last_emitted_gesture_time = 0.0
        self.gesture_pending_label = None
        self.gesture_pending_start = 0.0

    def _start_translation_thread(self):
        """Start the background translation thread."""
        self.translation_running = True
        self.translation_thread = threading.Thread(target=self._translation_worker, daemon=True)
        self.translation_thread.start()
        print("🤖 Translation service started")

    def _start_tts_thread(self):
        """Start the background TTS worker thread."""
        self.tts_running = True
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.tts_thread.start()
        print("🔊 TTS service started")

    def _start_audio_thread(self):
        """Start the background audio playback thread."""
        self.audio_running = True
        self.audio_thread = threading.Thread(target=self._audio_worker, daemon=True)
        self.audio_thread.start()
        print("🎵 Audio playback service started")

    def _translation_worker(self):
        """Background worker to process translation queue."""
        while self.translation_running:
            try:
                if self.sentence_queue:
                    sentence_data = self.sentence_queue.popleft()
                    
                    print(f"🔄 Translating: '{sentence_data['raw_text']}'")
                    sentence_data['status'] = 'translating'
                    
                    # Translate using OpenAI
                    translated_text = fix_sentence(sentence_data['raw_text'])
                    cleaned_text = (translated_text or "").strip()

                    sentence_data['translated_text'] = cleaned_text
                    sentence_data['translation_time'] = time.time()

                    silent_tokens = {"", "silent", "remain silent", "silence", "[silence]", "[silent]"}
                    is_silent = cleaned_text.lower() in silent_tokens
                    sentence_data['status'] = 'silent' if is_silent else 'completed'

                    self.translated_sentences.append(sentence_data)

                    if self.show_translations:
                        if is_silent:
                            print(f"✨ Translation #{sentence_data['id']}: (silent)")
                        else:
                            print(f"✨ Translation #{sentence_data['id']}: '{cleaned_text}'")
                    
                    # Keep only last 10 translations to save memory
                    if len(self.translated_sentences) > 10:
                        self.translated_sentences.pop(0)

                    if is_silent:
                        continue

                    # Enqueue for TTS synthesis
                    if cleaned_text:
                        try:
                            tts_entry = {
                                'id': sentence_data['id'],
                                'text': cleaned_text,
                                'timestamp': time.time(),
                                'status': 'queued',
                                'voice_id': self.tts_voice_id
                            }
                            self.tts_queue.append(tts_entry)
                            print(f"📣 Queued for TTS (TTS Queue size: {len(self.tts_queue)})")
                        except Exception:
                            # non-fatal - continue
                            pass
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                print(f"❌ Translation error: {e}")
                if self.sentence_queue:
                    failed_sentence = self.sentence_queue.popleft()
                    failed_sentence['status'] = 'failed'
                    failed_sentence['error'] = str(e)
                    self.translated_sentences.append(failed_sentence)

    def _tts_worker(self):
        """Background worker that consumes translated sentences and synthesizes audio via ElevenLabs."""
        while self.tts_running:
            try:
                if self.tts_queue:
                    tts_data = self.tts_queue.popleft()
                    tts_data['status'] = 'synthesizing'
                    tts_data['synthesis_start'] = time.time()

                    # Lazy import to avoid import-time dependencies
                    try:
                        from src.eleven_tts import synthesize_to_file
                    except Exception:
                        # can't synthesize without the module
                        tts_data['status'] = 'failed'
                        tts_data['error'] = 'eleven_tts module not available'
                        self.tts_results.append(tts_data)
                        print(f"❌ TTS failed (module missing) for id {tts_data.get('id')}")
                        continue

                    voice_id = tts_data.get('voice_id') or self.tts_voice_id or os.getenv('XI_VOICE_ID')
                    api_key = os.getenv('XI_API_KEY')
                    out_name = f"tts_{tts_data.get('id')}.mp3"

                    try:
                        print(f"🔊 TTS synthesis started for id {tts_data.get('id')}: '{tts_data.get('text')[:60]}'")

                        # Prefer a persistent client when available (faster, reused TCP/TLS)
                        audio_path = None
                        if getattr(self, '_eleven_client', None) is not None:
                            try:
                                # SDK convert invocation
                                res = self._eleven_client.text_to_speech.convert(
                                    voice_id=voice_id,
                                    text=tts_data['text'],
                                    output_format='mp3_44100_128',
                                )
                                # Handle common response shapes from SDK
                                if isinstance(res, (bytes, bytearray)):
                                    with open(out_name, 'wb') as fh:
                                        fh.write(res)
                                    audio_path = out_name
                                elif hasattr(res, 'read'):
                                    data = res.read()
                                    with open(out_name, 'wb') as fh:
                                        fh.write(data)
                                    audio_path = out_name
                                elif isinstance(res, str) and os.path.exists(res):
                                    # SDK returned a path
                                    if res != out_name:
                                        with open(res, 'rb') as src, open(out_name, 'wb') as dst:
                                            dst.write(src.read())
                                    audio_path = out_name
                                elif isinstance(res, dict):
                                    for k in ('audio', 'audio_content', 'content'):
                                        if k in res and isinstance(res[k], (bytes, bytearray)):
                                            with open(out_name, 'wb') as fh:
                                                fh.write(res[k])
                                            audio_path = out_name
                                            break
                                else:
                                    # Last resort: try bytes()
                                    try:
                                        blob = bytes(res)
                                        with open(out_name, 'wb') as fh:
                                            fh.write(blob)
                                        audio_path = out_name
                                    except Exception:
                                        audio_path = None
                            except Exception as e:
                                print(f"❌ Persistent ElevenLabs client synthesis failed: {e}")

                        # Fallback to helper which will lazy-import SDK or raise
                        if not audio_path:
                            from src.eleven_tts import synthesize_to_file
                            audio_path = synthesize_to_file(text=tts_data['text'], voice_id=voice_id, output_path=out_name, api_key=api_key)
                        tts_data['status'] = 'completed'
                        tts_data['audio_path'] = audio_path
                        tts_data['synthesis_time'] = time.time()
                        self.tts_results.append(tts_data)
                        print(f"✅ TTS completed for id {tts_data.get('id')}: {audio_path}")

                        # Keep tts_results bounded
                        if len(self.tts_results) > 20:
                            self.tts_results.pop(0)
                        # Optionally auto-play the synthesized audio (synchronous)
                        if getattr(self, 'auto_play_tts', False):
                            try:
                                # Queue audio for synchronous playback
                                audio_entry = {
                                    'id': tts_data.get('id'),
                                    'path': audio_path,
                                    'timestamp': time.time(),
                                    'text': tts_data.get('text', '')
                                }
                                self.audio_queue.append(audio_entry)
                                print(f"🎵 Queued audio for playback (Audio Queue size: {len(self.audio_queue)})")
                            except Exception as e:
                                print(f"❌ TTS autoplay error for id {tts_data.get('id')}: {e}")
                    except Exception as e:
                        tts_data['status'] = 'failed'
                        tts_data['error'] = str(e)
                        self.tts_results.append(tts_data)
                        print(f"❌ TTS synthesis error for id {tts_data.get('id')}: {e}")

                time.sleep(0.1)
            except Exception as e:
                print(f"❌ TTS worker error: {e}")
                time.sleep(0.5)

    def _audio_worker(self):
        """Background worker that plays audio files synchronously from the queue."""
        while self.audio_running:
            try:
                if self.audio_queue:
                    audio_data = self.audio_queue.popleft()
                    self.current_audio_playing = audio_data
                    self.audio_cancelled = False
                    
                    print(f"🎵 Playing audio for id {audio_data.get('id')}: '{audio_data.get('text', '')[:60]}'")
                    
                    # Play audio synchronously (blocking)
                    self._play_audio_sync(audio_data['path'])
                    
                    # Mark as completed
                    self.current_audio_playing = None
                    print(f"✅ Audio playback completed for id {audio_data.get('id')}")
                
                time.sleep(0.1)
            except Exception as e:
                print(f"❌ Audio worker error: {e}")
                self.current_audio_playing = None
                time.sleep(0.5)

    def get_current_sentence(self) -> str:
        """Get the current sentence being built."""
        return ' '.join(self.current_sentence)

    def append_unknown_sign(self) -> str:
        """Expose manual recording of an unrecognized sign."""
        self._append_unknown_sign()
        return ''

    def get_recent_translations(self, count: int = 5) -> List[Dict]:
        """Get the most recent translations."""
        return self.translated_sentences[-count:] if self.translated_sentences else []

    def get_audio_status(self) -> Dict:
        """Get current audio playback status."""
        return {
            'is_playing': self.current_audio_playing is not None,
            'current_audio': self.current_audio_playing,
            'queue_size': len(self.audio_queue),
            'cancelled': self.audio_cancelled
        }

    def _print_landmarks_advanced(self, results, advanced_gestures, frame_count):
        """Print landmark coordinates and advanced gesture info to console."""
        if not self.console_landmark_logging:
            return

        print(f"\n📊 Frame {frame_count} - Hands: {results['hands_detected']}")

        for i, hand in enumerate(results['hands']):
            print(f"\n🖐️  Hand {i+1} ({hand['handedness']}) - Confidence: {hand['handedness_confidence']:.3f}")
            
            # Advanced gesture information
            if i < len(advanced_gestures):
                gesture_info = advanced_gestures[i]
                print(f"   🎯 Gesture: {gesture_info['gesture']}")
                if gesture_info['number'] is not None:
                    print(f"   🔢 Number: {gesture_info['number']}")
                
                # Finger states
                finger_states = gesture_info['finger_states']
                fingers_up = finger_states['fingers_up']
                print(f"   ✋ Fingers: {' '.join([name if up else '❌' for name, up in zip(finger_states['finger_names'], fingers_up)])}")
            
            # Print ALL 21 landmarks
            print("   📍 All Hand Landmarks (x, y, z):")
            for idx, landmark in enumerate(hand['landmarks']):
                print(f"      {idx:2d} - {landmark['name']:18s}: ({landmark['x']:.4f}, {landmark['y']:.4f}, {landmark['z']:.4f})")
    
    def _print_landmarks(self, results, gestures, frame_count):
        """Print landmark coordinates to console (basic version)."""
        if not self.console_landmark_logging:
            return

        print(f"\n📊 Frame {frame_count} - Hands: {results['hands_detected']}")
        
        for i, hand in enumerate(results['hands']):
            print(f"\n🖐️  Hand {i+1} ({hand['handedness']}) - Confidence: {hand['handedness_confidence']:.3f}")
            
            if i < len(gestures):
                print(f"   🎯 Gesture: {gestures[i]}")
            
            # Print ALL 21 landmarks
            print("   📍 All Hand Landmarks (x, y, z):")
            for idx, landmark in enumerate(hand['landmarks']):
                print(f"      {idx:2d} - {landmark['name']:18s}: ({landmark['x']:.4f}, {landmark['y']:.4f}, {landmark['z']:.4f})")
    
    def _annotate_frame_advanced(self, image, results, advanced_gestures):
        """Add advanced annotations to the video frame."""
        annotated_frame = self.detector.draw_landmarks(image, results)
        
        # Add detection info
        cv2.putText(annotated_frame, f"Hands: {results['hands_detected']}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 128, 0), 2)
        
        # Add advanced gesture info
        y_offset = 70
        for i, gesture_info in enumerate(advanced_gestures):
            gesture = gesture_info['gesture']
            color = (0, 255, 255) if gesture != "Unknown Gesture" else (0, 0, 255)
            
            # Main gesture
            cv2.putText(annotated_frame, f"Hand {i+1}: {gesture}", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset += 25
            
            # Number if detected
            if gesture_info['number'] is not None:
                cv2.putText(annotated_frame, f"Number: {gesture_info['number']}", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                y_offset += 25
            
            # Finger states
            finger_states = gesture_info['finger_states']
            fingers_text = f"Fingers: {finger_states['fingers_count']}/5"
            cv2.putText(annotated_frame, fingers_text, 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            y_offset += 35
        
        # Add sentence and translation info
        if self.show_raw_gestures and self.current_sentence:
            current_text = f"Current: {' '.join(self.current_sentence)}"
            cv2.putText(annotated_frame, current_text, 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            y_offset += 25
        
        if self.show_translations and self.translated_sentences:
            recent = self.translated_sentences[-3:]  # Show last 3 translations
            for i, trans in enumerate(recent):
                if trans['status'] == 'completed':
                    text = f"#{trans['id']}: {trans['translated_text']}"
                    cv2.putText(annotated_frame, text, 
                               (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    y_offset += 20
        
        # Add instructions
        instructions = [
            "q:quit s:save t:toggle-trans r:toggle-raw",
            "c:clear n:new-sentence x:cancel-audio SPACE:analysis"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(annotated_frame, instruction, 
                       (10, annotated_frame.shape[0] - 40 + i*20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return annotated_frame
    
    def _annotate_frame(self, image, results, gestures):
        """Add annotations to the video frame (basic version)."""
        annotated_frame = self.detector.draw_landmarks(image, results)
        
        # Add detection info
        cv2.putText(annotated_frame, f"Hands: {results['hands_detected']}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 128, 0), 2)
        
        # Add gesture info
        y_offset = 70
        for i, gesture in enumerate(gestures):
            color = (0, 255, 255) if gesture != "Unknown Gesture" else (0, 0, 255)
            cv2.putText(annotated_frame, f"Gesture {i+1}: {gesture}", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset += 30
        
        # Add instructions
        instructions = [
            "Press 'q' to quit",
            "Press 's' to save landmarks",
            "Press SPACE for analysis"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(annotated_frame, instruction, 
                       (10, annotated_frame.shape[0] - 60 + i*20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return annotated_frame
    
    def _save_landmarks_to_file(self, results, gestures, frame_count):
        """Save landmarks to a continuous log file."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"landmarks_log_{timestamp}.jsonl"
        
        data = {
            'timestamp': time.time(),
            'frame': frame_count,
            'results': results,
            'gestures': gestures
        }
        
        with open(filename, 'a') as f:
            f.write(json.dumps(data) + '\n')
    
    def _save_current_landmarks(self, results, gestures):
        """Save current landmarks to a timestamped file."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"hand_landmarks_{timestamp}.json"
        
        data = {
            'timestamp': timestamp,
            'results': results,
            'gestures': gestures
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Landmarks saved to: {filename}")
    
    def _detailed_analysis_advanced(self, results, advanced_gestures):
        """Perform detailed analysis of current frame with advanced gesture info."""
        print("\n" + "="*60)
        print("🔍 ADVANCED DETAILED LANDMARK ANALYSIS")
        print("="*60)
        
        if results['hands_detected'] == 0:
            print("❌ No hands detected")
            return
        
        for i, hand in enumerate(results['hands']):
            print(f"\n🖐️  HAND {i+1} DETAILED ANALYSIS")
            print(f"   Handedness: {hand['handedness']}")
            print(f"   Confidence: {hand['handedness_confidence']:.4f}")
            
            if i < len(advanced_gestures):
                gesture_info = advanced_gestures[i]
                print(f"   🎯 Gesture: {gesture_info['gesture']}")
                if gesture_info['number'] is not None:
                    print(f"   🔢 Number: {gesture_info['number']}")
                
                # Detailed finger analysis
                finger_states = gesture_info['finger_states']
                print(f"   ✋ Fingers Extended: {finger_states['fingers_count']}/5")
                for name, extended in zip(finger_states['finger_names'], finger_states['fingers_up']):
                    status = "✅ Extended" if extended else "❌ Folded"
                    print(f"      {name}: {status}")
                
                # Hand orientation info
                orientation = gesture_info['orientation']
                print(f"   📐 Hand Angle: {orientation['hand_angle']:.1f}°")
                print(f"   👋 Palm Facing Camera: {'Yes' if orientation['palm_facing_camera'] else 'No'}")
            
            # Calculate hand metrics
            landmarks = hand['landmarks']
            
            # Hand span (thumb to pinky)
            thumb_tip = landmarks[4]
            pinky_tip = landmarks[20]
            hand_span = np.sqrt(
                (thumb_tip['x'] - pinky_tip['x'])**2 + 
                (thumb_tip['y'] - pinky_tip['y'])**2
            )
            
            # Hand length (wrist to middle finger)
            wrist = landmarks[0]
            middle_tip = landmarks[12]
            hand_length = np.sqrt(
                (middle_tip['x'] - wrist['x'])**2 + 
                (middle_tip['y'] - wrist['y'])**2
            )
            
            print(f"   📏 Hand Span: {hand_span:.4f}")
            print(f"   📏 Hand Length: {hand_length:.4f}")
            
            # Key landmark positions
            print("   📍 Key Landmark Positions:")
            key_landmarks = [0, 4, 8, 12, 16, 20]
            key_names = ['Wrist', 'Thumb Tip', 'Index Tip', 'Middle Tip', 'Ring Tip', 'Pinky Tip']
            for idx, name in zip(key_landmarks, key_names):
                landmark = landmarks[idx]
                print(f"      {name}: ({landmark['x']:.4f}, {landmark['y']:.4f}, {landmark['z']:.4f})")
        
        print("="*60)
    
    def _detailed_analysis(self, results, gestures):
        """Perform detailed analysis of current frame."""
        print("\n" + "="*50)
        print("🔍 DETAILED LANDMARK ANALYSIS")
        print("="*50)
        
        if results['hands_detected'] == 0:
            print("❌ No hands detected")
            return
        
        for i, hand in enumerate(results['hands']):
            print(f"\n🖐️  HAND {i+1} ANALYSIS")
            print(f"   Handedness: {hand['handedness']}")
            print(f"   Confidence: {hand['handedness_confidence']:.4f}")
            
            if i < len(gestures):
                print(f"   Gesture: {gestures[i]}")
            
            # Calculate hand metrics
            landmarks = hand['landmarks']
            
            # Hand span (thumb to pinky)
            thumb_tip = landmarks[4]
            pinky_tip = landmarks[20]
            hand_span = np.sqrt(
                (thumb_tip['x'] - pinky_tip['x'])**2 + 
                (thumb_tip['y'] - pinky_tip['y'])**2
            )
            
            # Hand length (wrist to middle finger)
            wrist = landmarks[0]
            middle_tip = landmarks[12]
            hand_length = np.sqrt(
                (middle_tip['x'] - wrist['x'])**2 + 
                (middle_tip['y'] - wrist['y'])**2
            )
            
            print(f"   Hand Span: {hand_span:.4f}")
            print(f"   Hand Length: {hand_length:.4f}")
            
            # Finger extension analysis
            finger_tips = [4, 8, 12, 16, 20]
            finger_pips = [3, 6, 10, 14, 18]
            finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
            
            print("   Finger States:")
            for tip_idx, pip_idx, name in zip(finger_tips, finger_pips, finger_names):
                tip_y = landmarks[tip_idx]['y']
                pip_y = landmarks[pip_idx]['y']
                extended = tip_y < pip_y
                print(f"      {name}: {'Extended' if extended else 'Folded'}")
        
        print("="*50)
    
    def _cleanup(self):
        """Clean up resources."""
        self.running = False
        self.translation_running = False
        self.tts_running = False
        self.audio_running = False
        
        # Wait for threads to finish
        if self.translation_thread and self.translation_thread.is_alive():
            self.translation_thread.join(timeout=2.0)
        if self.tts_thread and self.tts_thread.is_alive():
            self.tts_thread.join(timeout=2.0)
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=2.0)
        
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("🧹 Cleanup completed")

    def _play_audio_sync(self, path: str):
        """Play audio file synchronously using a best-effort, cross-platform approach.

        This is blocking and will wait for the audio to finish playing. On macOS it uses
        `afplay`. On Linux it tries `ffplay` (ffmpeg) or `aplay`. On Windows it
        will try `PowerShell`'s PlaySound via .NET or fallback to `start`.
        """
        try:
            print(f"▶️ Playing audio: {path}")
            if sys.platform == 'darwin':
                # macOS
                player = shutil.which('afplay')
                if player:
                    subprocess.run([player, path], check=False)
                    return
            elif sys.platform.startswith('linux'):
                # Linux: try ffplay (from ffmpeg) without console output
                player = shutil.which('ffplay')
                if player:
                    subprocess.run([player, '-nodisp', '-autoexit', '-loglevel', 'quiet', path], check=False)
                    return
                player = shutil.which('aplay')
                if player:
                    subprocess.run([player, path], check=False)
                    return
            elif sys.platform.startswith('win'):
                # Windows: use PowerShell to play via .NET System.Media.SoundPlayer
                ps = shutil.which('powershell') or shutil.which('pwsh')
                if ps:
                    cmd = [ps, '-NoProfile', '-Command', f"(New-Object Media.SoundPlayer '{path}').PlaySync();"]
                    subprocess.run(cmd, check=False)
                    return

            # Last resort: try opening with default application
            if sys.platform == 'darwin':
                subprocess.run(['open', path], check=False)
            elif sys.platform.startswith('linux'):
                subprocess.run(['xdg-open', path], check=False)
            elif sys.platform.startswith('win'):
                subprocess.run(['start', path], shell=True, check=False)
        except Exception as e:
            # Non-fatal; just log the issue
            print(f"❗ Audio playback failed for {path}: {e}")

    def _play_audio(self, path: str):
        """Play audio file using a best-effort, cross-platform approach.

        This is non-blocking when called in a separate thread. On macOS it uses
        `afplay`. On Linux it tries `ffplay` (ffmpeg) or `aplay`. On Windows it
        will try `PowerShell`'s PlaySound via .NET or fallback to `start`.
        """
        try:
            print(f"▶️ Playing audio: {path}")
            if sys.platform == 'darwin':
                # macOS
                player = shutil.which('afplay')
                if player:
                    subprocess.run([player, path], check=False)
                    return
            elif sys.platform.startswith('linux'):
                # Linux: try ffplay (from ffmpeg) without console output
                player = shutil.which('ffplay')
                if player:
                    subprocess.run([player, '-nodisp', '-autoexit', '-loglevel', 'quiet', path], check=False)
                    return
                player = shutil.which('aplay')
                if player:
                    subprocess.run([player, path], check=False)
                    return
            elif sys.platform.startswith('win'):
                # Windows: use PowerShell to play via .NET System.Media.SoundPlayer
                ps = shutil.which('powershell') or shutil.which('pwsh')
                if ps:
                    cmd = [ps, '-NoProfile', '-Command', f"(New-Object Media.SoundPlayer '{path}').PlaySync();"]
                    subprocess.run(cmd, check=False)
                    return

            # Last resort: try opening with default application
            if sys.platform == 'darwin':
                subprocess.run(['open', path], check=False)
            elif sys.platform.startswith('linux'):
                subprocess.run(['xdg-open', path], check=False)
            elif sys.platform.startswith('win'):
                subprocess.run(['start', path], shell=True, check=False)
        except Exception as e:
            # Non-fatal; just log the issue
            print(f"❗ Audio playback failed for {path}: {e}")

    def cancel_current_audio(self):
        """Cancel the currently playing audio and clear the queue."""
        if self.current_audio_playing:
            print(f"🛑 Cancelling audio playback for id {self.current_audio_playing.get('id')}")
            self.audio_cancelled = True
        
        # Clear the audio queue
        queue_size = len(self.audio_queue)
        self.audio_queue.clear()
        if queue_size > 0:
            print(f"🗑️ Cleared {queue_size} queued audio files")
        
        # Reset current audio
        self.current_audio_playing = None


def main():
    """Main function to start gesture detection."""
    parser = argparse.ArgumentParser(prog="camera_gesture_detection", description="Real-time gesture detector with optional TTS autoplay")
    parser.add_argument('--auto-play-tts', action='store_true', dest='auto_play_tts', help='Automatically play synthesized TTS audio')
    parser.add_argument('--tts-short-threshold', type=int, default=0, help='If >0, sentences with <= N words are auto-enqueued to TTS')
    parser.add_argument('--voice-id', type=str, default=None, help='Default ElevenLabs voice id to use')
    parser.add_argument('--camera-id', type=int, default=0, help='Camera device id')
    parser.add_argument('--no-video', action='store_true', help='Run without showing the video window')

    args = parser.parse_args()

    print("🚀 Real-time Hand Gesture Detection")
    print("=" * 40)

    try:
        detector = RealTimeGestureDetector(camera_id=args.camera_id, auto_play_tts=bool(args.auto_play_tts), tts_auto_enqueue_short_sentences=int(args.tts_short_threshold or 0))

        if args.voice_id:
            detector.tts_voice_id = args.voice_id

        # Start detection
        detector.start_detection(
            show_video=(not args.no_video),
            print_landmarks=True,
            save_to_file=False
        )

    except ValueError as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure your camera is connected and not being used by another application")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def quick_capture():
    """Quick function to capture and return landmarks from current camera frame."""
    detector = RealTimeGestureDetector()
    landmarks = detector.get_current_landmarks()
    detector._cleanup()
    return landmarks


if __name__ == "__main__":
    main()
