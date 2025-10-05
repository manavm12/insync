/**
 * Hand Gesture Detection System - Frontend JavaScript
 * Handles real-time updates, user interactions, and system control
 */

class GestureDetectionApp {
    constructor() {
        this.isRunning = false;
        this.updateInterval = null;
        this.updateFrequency = 500; // Update every 500ms
        
        // DOM elements
        this.elements = {
            startBtn: document.getElementById('startBtn'),
            stopBtn: document.getElementById('stopBtn'),
            systemStatus: document.getElementById('systemStatus'),
            videoFeed: document.getElementById('videoFeed'),
            cameraOverlay: document.getElementById('cameraOverlay'),
            currentSentence: document.getElementById('currentSentence'),
            currentGesture: document.getElementById('currentGesture'),
            handsDetected: document.getElementById('handsDetected'),
            translationsList: document.getElementById('translationsList'),
            landmarksList: document.getElementById('landmarksList'),
            handsCount: document.getElementById('handsCount'),
            translationsCount: document.getElementById('translationsCount'),
            detailedStatus: document.getElementById('detailedStatus'),
            detailedGesture: document.getElementById('detailedGesture'),
            audioQueue: document.getElementById('audioQueue'),
            audioState: document.getElementById('audioState'),
            forceSentenceBtn: document.getElementById('forceSentenceBtn'),
            clearSentencesBtn: document.getElementById('clearSentencesBtn'),
            cancelAudioBtn: document.getElementById('cancelAudioBtn'),
            customText: document.getElementById('customText'),
            speakBtn: document.getElementById('speakBtn'),
            notificationToast: document.getElementById('notificationToast'),
            toastMessage: document.getElementById('toastMessage')
        };
        
        this.initializeEventListeners();
        this.updateStatus();
    }
    
    initializeEventListeners() {
        // Control buttons
        this.elements.startBtn.addEventListener('click', () => this.startDetection());
        this.elements.stopBtn.addEventListener('click', () => this.stopDetection());
        this.elements.forceSentenceBtn.addEventListener('click', () => this.forceSentence());
        this.elements.clearSentencesBtn.addEventListener('click', () => this.clearSentences());
        this.elements.cancelAudioBtn.addEventListener('click', () => this.cancelAudio());
        this.elements.speakBtn.addEventListener('click', () => this.speakCustomText());
        
        // Custom text input
        this.elements.customText.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.speakCustomText();
            }
        });
        
        // Video feed error handling
        this.elements.videoFeed.addEventListener('error', () => {
            console.log('Video feed error - system may be stopped');
        });
        
        // Initialize Bootstrap toast
        this.toast = new bootstrap.Toast(this.elements.notificationToast);
    }
    
    async startDetection() {
        try {
            this.showLoading(this.elements.startBtn);
            
            const response = await fetch('/api/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.isRunning = true;
                this.updateUI();
                this.startStatusUpdates();
                this.showNotification('System started successfully!', 'success');
            } else {
                this.showNotification('Failed to start system', 'error');
            }
        } catch (error) {
            console.error('Error starting detection:', error);
            this.showNotification('Error starting system', 'error');
        } finally {
            this.hideLoading(this.elements.startBtn, '<i class="fas fa-play"></i> Start');
        }
    }
    
    async stopDetection() {
        try {
            this.showLoading(this.elements.stopBtn);
            
            const response = await fetch('/api/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.isRunning = false;
                this.stopStatusUpdates();
                this.updateUI();
                this.showNotification('System stopped', 'info');
            } else {
                this.showNotification('Failed to stop system', 'error');
            }
        } catch (error) {
            console.error('Error stopping detection:', error);
            this.showNotification('Error stopping system', 'error');
        } finally {
            this.hideLoading(this.elements.stopBtn, '<i class="fas fa-stop"></i> Stop');
        }
    }
    
    async forceSentence() {
        try {
            const response = await fetch('/api/force_sentence', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                this.showNotification('Sentence completed', 'success');
            }
        } catch (error) {
            console.error('Error forcing sentence:', error);
            this.showNotification('Error completing sentence', 'error');
        }
    }
    
    async clearSentences() {
        try {
            const response = await fetch('/api/clear_sentences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                this.showNotification('All sentences cleared', 'info');
            }
        } catch (error) {
            console.error('Error clearing sentences:', error);
            this.showNotification('Error clearing sentences', 'error');
        }
    }
    
    async cancelAudio() {
        try {
            const response = await fetch('/api/cancel_audio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                this.showNotification('Audio cancelled', 'info');
            }
        } catch (error) {
            console.error('Error cancelling audio:', error);
            this.showNotification('Error cancelling audio', 'error');
        }
    }
    
    async speakCustomText() {
        const text = this.elements.customText.value.trim();
        
        if (!text) {
            this.showNotification('Please enter text to speak', 'warning');
            return;
        }
        
        try {
            this.showLoading(this.elements.speakBtn);
            
            const response = await fetch('/api/speak_text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.elements.customText.value = '';
                this.showNotification(`Queued for speech: "${text}"`, 'success');
            } else {
                this.showNotification(result.error || 'Failed to queue text', 'error');
            }
        } catch (error) {
            console.error('Error speaking text:', error);
            this.showNotification('Error queuing text for speech', 'error');
        } finally {
            this.hideLoading(this.elements.speakBtn, '<i class="fas fa-volume-up"></i> Speak');
        }
    }
    
    startStatusUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        this.updateInterval = setInterval(() => {
            this.updateStatus();
        }, this.updateFrequency);
    }
    
    stopStatusUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
    
    async updateStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            if (response.ok) {
                this.updateStatusDisplay(status);
            }
        } catch (error) {
            console.error('Error updating status:', error);
        }
    }
    
    updateStatusDisplay(status) {
        // Update system status
        const statusText = status.system_status.charAt(0).toUpperCase() + status.system_status.slice(1);
        this.elements.systemStatus.textContent = statusText;
        this.elements.systemStatus.className = `badge bg-${this.getStatusColor(status.system_status)}`;
        
        // Update detailed status
        this.elements.detailedStatus.textContent = statusText;
        this.elements.detailedGesture.textContent = status.current_gesture || 'None';
        
        // Update current gesture and hands
        this.elements.currentGesture.textContent = status.current_gesture || 'None';
        this.elements.handsDetected.textContent = `${status.hands_detected} hands`;
        this.elements.handsCount.textContent = status.hands_detected;
        
        // Update current sentence
        if (status.current_sentence && status.current_sentence.trim()) {
            this.elements.currentSentence.innerHTML = `<strong>${status.current_sentence}</strong>`;
        } else {
            this.elements.currentSentence.innerHTML = '<em class="text-muted">No sentence being built...</em>';
        }
        
        // Update translations
        this.updateTranslationsList(status.recent_translations);
        
        // Update landmarks
        this.updateLandmarksList(status.hand_landmarks);
        
        // Update audio status
        this.updateAudioStatus(status.audio_status);
        
        // Update running state
        this.isRunning = status.system_status === 'running';
        this.updateUI();
    }
    
    updateTranslationsList(translations) {
        this.elements.translationsCount.textContent = translations.length;
        
        if (!translations || translations.length === 0) {
            this.elements.translationsList.innerHTML = `
                <div class="text-muted text-center py-3">
                    <i class="fas fa-language fa-2x mb-2"></i>
                    <p class="mb-0">No translations yet</p>
                </div>
            `;
            return;
        }
        
        // Check for new completed translations to show TTS notifications
        if (this.lastTranslationCount && translations.length > this.lastTranslationCount) {
            const newTranslations = translations.slice(this.lastTranslationCount);
            newTranslations.forEach(translation => {
                if (translation.status === 'completed' && translation.translated_text) {
                    this.showNotification(`🔊 Speaking: "${translation.translated_text}"`, 'tts');
                }
            });
        }
        this.lastTranslationCount = translations.length;
        
        const translationsHtml = translations.reverse().map(translation => {
            const statusClass = translation.status === 'completed' ? 'completed' : 
                              translation.status === 'silent' ? 'silent' : 'failed';
            
            return `
                <div class="translation-item fade-in">
                    <div class="translation-id">#${translation.id}</div>
                    <div class="translation-text">${translation.translated_text || 'Processing...'}</div>
                    <div class="translation-raw">Raw: ${translation.raw_text}</div>
                    <span class="translation-status ${statusClass}">${translation.status}</span>
                </div>
            `;
        }).join('');
        
        this.elements.translationsList.innerHTML = translationsHtml;
    }
    
    updateLandmarksList(landmarks) {
        if (!landmarks || landmarks.length === 0) {
            this.elements.landmarksList.innerHTML = `
                <div class="text-muted text-center py-3">
                    <i class="fas fa-hand-paper fa-2x mb-2"></i>
                    <p class="mb-0">No hands detected</p>
                    <small>Visual landmarks are shown on the camera feed</small>
                </div>
            `;
            return;
        }
        
        const landmarksHtml = landmarks.map((hand, index) => {
            return `
                <div class="landmark-hand fade-in">
                    <div class="hand-header">
                        <i class="fas fa-hand-paper me-2"></i>
                        ${hand.handedness} Hand
                    </div>
                    <div class="hand-confidence">
                        <div class="progress mb-2" style="height: 8px;">
                            <div class="progress-bar bg-success" role="progressbar" 
                                 style="width: ${(hand.confidence * 100).toFixed(1)}%" 
                                 aria-valuenow="${(hand.confidence * 100).toFixed(1)}" 
                                 aria-valuemin="0" aria-valuemax="100">
                            </div>
                        </div>
                        <small class="text-muted">Confidence: ${(hand.confidence * 100).toFixed(1)}%</small>
                    </div>
                    <div class="landmark-info">
                        <small class="text-success">
                            <i class="fas fa-eye me-1"></i>
                            ${hand.landmarks.length} landmarks detected
                        </small>
                        <br>
                        <small class="text-info">
                            <i class="fas fa-video me-1"></i>
                            Visual landmarks shown on camera
                        </small>
                    </div>
                </div>
            `;
        }).join('');
        
        this.elements.landmarksList.innerHTML = landmarksHtml;
    }
    
    updateAudioStatus(audioStatus) {
        const audioIndicator = document.querySelector('.audio-indicator');
        const audioIcon = document.getElementById('audioIcon');
        
        if (audioStatus.is_playing) {
            this.elements.audioState.textContent = 'Playing';
            this.elements.audioState.className = 'fw-bold text-success';
            audioIndicator.classList.add('playing');
            audioIcon.className = 'fas fa-volume-up';
        } else {
            this.elements.audioState.textContent = 'Idle';
            this.elements.audioState.className = 'fw-bold text-muted';
            audioIndicator.classList.remove('playing');
            audioIcon.className = 'fas fa-volume-mute';
        }
        
        this.elements.audioQueue.textContent = `${audioStatus.queue_size} items`;
    }
    
    updateUI() {
        // Update button states
        this.elements.startBtn.disabled = this.isRunning;
        this.elements.stopBtn.disabled = !this.isRunning;
        this.elements.forceSentenceBtn.disabled = !this.isRunning;
        this.elements.clearSentencesBtn.disabled = !this.isRunning;
        this.elements.cancelAudioBtn.disabled = !this.isRunning;
        this.elements.customText.disabled = !this.isRunning;
        this.elements.speakBtn.disabled = !this.isRunning;
        
        // Update camera overlay - hide when running
        if (this.isRunning) {
            this.elements.cameraOverlay.style.display = 'none !important';
            this.elements.cameraOverlay.classList.add('d-none');
        } else {
            this.elements.cameraOverlay.style.display = 'flex';
            this.elements.cameraOverlay.classList.remove('d-none');
        }
    }
    
    getStatusColor(status) {
        switch (status) {
            case 'running': return 'success';
            case 'stopped': return 'secondary';
            case 'error': return 'danger';
            default: return 'secondary';
        }
    }
    
    showLoading(button) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Loading...';
    }
    
    hideLoading(button, originalContent) {
        button.disabled = false;
        button.innerHTML = originalContent;
    }
    
    showNotification(message, type = 'info') {
        const iconMap = {
            success: 'fas fa-check-circle text-success',
            error: 'fas fa-exclamation-circle text-danger',
            warning: 'fas fa-exclamation-triangle text-warning',
            info: 'fas fa-info-circle text-info',
            tts: 'fas fa-volume-up text-primary'
        };
        
        this.elements.toastMessage.innerHTML = `
            <i class="${iconMap[type] || iconMap.info} me-2"></i>
            ${message}
        `;
        
        // Auto-hide success and info messages after 3 seconds
        if (type === 'success' || type === 'info' || type === 'tts') {
            setTimeout(() => {
                this.toast.hide();
            }, 3000);
        }
        
        this.toast.show();
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new GestureDetectionApp();
    
    // Make app globally available for debugging
    window.gestureApp = app;
    
    console.log('Hand Gesture Detection System initialized');
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden, reduce update frequency
        if (window.gestureApp && window.gestureApp.updateInterval) {
            window.gestureApp.updateFrequency = 2000; // 2 seconds
        }
    } else {
        // Page is visible, restore normal frequency
        if (window.gestureApp && window.gestureApp.updateInterval) {
            window.gestureApp.updateFrequency = 500; // 500ms
        }
    }
});

// Handle window beforeunload to stop detection
window.addEventListener('beforeunload', () => {
    if (window.gestureApp && window.gestureApp.isRunning) {
        window.gestureApp.stopDetection();
    }
});
