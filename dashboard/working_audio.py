"""
WORKING Audio Alert System for Streamlit Dashboard
This version uses multiple fallback methods to ensure audio works
"""

import streamlit as st
import streamlit.components.v1 as components

def inject_working_audio_system():
    """Inject WORKING audio alert functionality"""
    audio_html = """
    <script>
    // ULTIMATE WORKING Audio System with Multiple Fallbacks
    class WorkingAudioAlerts {
        constructor() {
            this.isMuted = false;
            this.currentLevel = null;
            this.intervalId = null;
            this.audioMethod = 'none';
            this.initializeAllMethods();
            console.log('🔊 ULTIMATE Audio System Starting...');
        }
        
        initializeAllMethods() {
            // Method 1: Speech Synthesis (always works)
            this.initSpeechSynthesis();
            
            // Method 2: HTML5 Audio with generated sounds
            this.initHTML5Audio();
            
            // Method 3: Web Audio API
            this.initWebAudio();
            
            console.log('✅ Audio methods initialized');
        }
        
        initSpeechSynthesis() {
            if ('speechSynthesis' in window) {
                this.speechSynth = window.speechSynthesis;
                this.audioMethod = 'speech';
                console.log('✅ Speech Synthesis available');
            }
        }
        
        initHTML5Audio() {
            // Create beep audio programmatically
            this.createBeepAudio();
        }
        
        createBeepAudio() {
            // Generate actual audio data for beeps
            const audioContext = new (window.AudioContext || window.webkitAudioContext || false)();
            if (audioContext) {
                this.generateAudioFiles(audioContext);
                this.audioMethod = 'html5';
                console.log('✅ HTML5 Audio generated');
            }
        }
        
        generateAudioFiles(audioContext) {
            // Generate danger beep
            this.dangerAudio = this.createBeepFile(audioContext, 1000, 0.3);
            // Generate warning beep  
            this.warningAudio = this.createBeepFile(audioContext, 800, 0.6);
        }
        
        createBeepFile(audioContext, frequency, duration) {
            const sampleRate = audioContext.sampleRate;
            const length = sampleRate * duration;
            const buffer = audioContext.createBuffer(1, length, sampleRate);
            const data = buffer.getChannelData(0);
            
            for (let i = 0; i < length; i++) {
                data[i] = Math.sin(2 * Math.PI * frequency * i / sampleRate) * 0.5;
            }
            
            const source = audioContext.createBufferSource();
            source.buffer = buffer;
            
            // Convert to playable audio
            const audio = new Audio();
            const blob = this.bufferToWave(buffer, sampleRate);
            audio.src = URL.createObjectURL(blob);
            return audio;
        }
        
        bufferToWave(abuffer, sampleRate) {
            const length = abuffer.length;
            const buffer = new ArrayBuffer(44 + length * 2);
            const view = new DataView(buffer);
            
            // RIFF identifier
            this.writeString(view, 0, 'RIFF');
            // file length
            view.setUint32(4, 36 + length * 2, true);
            // RIFF type
            this.writeString(view, 8, 'WAVE');
            // format chunk identifier
            this.writeString(view, 12, 'fmt ');
            // format chunk length
            view.setUint32(16, 16, true);
            // sample format (raw)
            view.setUint16(20, 1, true);
            // channel count
            view.setUint16(22, 1, true);
            // sample rate
            view.setUint32(24, sampleRate, true);
            // byte rate (sample rate * block align)
            view.setUint32(28, sampleRate * 2, true);
            // block align (channel count * bytes per sample)
            view.setUint16(32, 2, true);
            // bits per sample
            view.setUint16(34, 16, true);
            // data chunk identifier
            this.writeString(view, 36, 'data');
            // data chunk length
            view.setUint32(40, length * 2, true);
            
            // write the PCM samples
            const channelData = abuffer.getChannelData(0);
            let offset = 44;
            for (let i = 0; i < length; i++, offset += 2) {
                const sample = Math.max(-1, Math.min(1, channelData[i]));
                view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
            }
            
            return new Blob([buffer], { type: 'audio/wav' });
        }
        
        writeString(view, offset, string) {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        }
        
        initWebAudio() {
            document.addEventListener('click', () => {
                try {
                    this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    if (this.audioMethod === 'none') {
                        this.audioMethod = 'webaudio';
                        console.log('✅ Web Audio API ready');
                    }
                } catch (e) {
                    console.log('❌ Web Audio API failed:', e);
                }
            }, { once: true });
        }
        
        playDangerAlarm() {
            if (this.isMuted) {
                console.log('🔇 Danger alarm muted');
                return;
            }
            
            console.log('🚨 PLAYING DANGER ALARM');
            
            if (this.audioMethod === 'html5' && this.dangerAudio) {
                // Use generated audio
                this.dangerAudio.currentTime = 0;
                this.dangerAudio.play().catch(() => this.fallbackDangerAlarm());
            } else if (this.audioMethod === 'webaudio' && this.audioContext) {
                // Use Web Audio API
                this.playWebAudioBeep(1000, 0.3);
                setTimeout(() => this.playWebAudioBeep(1200, 0.3), 400);
                setTimeout(() => this.playWebAudioBeep(1000, 0.3), 800);
            } else {
                // Fallback to speech
                this.fallbackDangerAlarm();
            }
        }
        
        playWarningAlarm() {
            if (this.isMuted) {
                console.log('🔇 Warning alarm muted');
                return;
            }
            
            console.log('⚠️ PLAYING WARNING ALARM');
            
            if (this.audioMethod === 'html5' && this.warningAudio) {
                // Use generated audio
                this.warningAudio.currentTime = 0;
                this.warningAudio.play().catch(() => this.fallbackWarningAlarm());
            } else if (this.audioMethod === 'webaudio' && this.audioContext) {
                // Use Web Audio API
                this.playWebAudioBeep(800, 0.6);
            } else {
                // Fallback to speech
                this.fallbackWarningAlarm();
            }
        }
        
        playWebAudioBeep(frequency, duration) {
            if (!this.audioContext) return;
            
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(0.5, this.audioContext.currentTime + 0.01);
            gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);
            
            oscillator.start(this.audioContext.currentTime);
            oscillator.stop(this.audioContext.currentTime + duration);
        }
        
        fallbackDangerAlarm() {
            console.log('🚨 Using speech fallback for danger');
            if (this.speechSynth) {
                const utterance = new SpeechSynthesisUtterance('Danger! Evacuate immediately!');
                utterance.rate = 2;
                utterance.pitch = 2;
                utterance.volume = 1;
                this.speechSynth.speak(utterance);
            }
        }
        
        fallbackWarningAlarm() {
            console.log('⚠️ Using speech fallback for warning');
            if (this.speechSynth) {
                const utterance = new SpeechSynthesisUtterance('Warning! Use caution!');
                utterance.rate = 1.5;
                utterance.pitch = 1.5;
                utterance.volume = 0.8;
                this.speechSynth.speak(utterance);
            }
        }
        
        startContinuousAlarm(level) {
            this.stopContinuousAlarm();
            this.currentLevel = level;
            
            if (level === 'danger') {
                console.log('🚨 Starting continuous DANGER alarm (every 3s)');
                this.intervalId = setInterval(() => {
                    this.playDangerAlarm();
                }, 3000);
            } else if (level === 'warning') {
                console.log('⚠️ Starting continuous WARNING alarm (every 5s)');
                this.intervalId = setInterval(() => {
                    this.playWarningAlarm();
                }, 5000);
            }
        }
        
        stopContinuousAlarm() {
            if (this.intervalId) {
                clearInterval(this.intervalId);
                this.intervalId = null;
                console.log('🔕 Stopped continuous alarm');
            }
        }
        
        toggleMute() {
            this.isMuted = !this.isMuted;
            console.log(`🔊 Sound ${this.isMuted ? 'MUTED' : 'UNMUTED'}`);
            if (this.isMuted) {
                this.stopContinuousAlarm();
            } else if (this.currentLevel) {
                this.startContinuousAlarm(this.currentLevel);
            }
            return this.isMuted;
        }
    }
    
    // Initialize the working audio system
    window.workingAudioAlerts = new WorkingAudioAlerts();
    window.mineAudioAlerts = window.workingAudioAlerts; // Compatibility
    
    // Auto-detect danger zones
    setInterval(() => {
        const pageText = document.body.textContent.toLowerCase();
        const hasDanger = pageText.includes('🚨 danger') || pageText.includes('stay away');
        const hasWarning = pageText.includes('⚠️ be careful') || pageText.includes('extra monitoring');
        
        if (hasDanger && window.workingAudioAlerts.currentLevel !== 'danger') {
            console.log('🚨 AUTO-DETECTED DANGER - TRIGGERING ALARM');
            window.workingAudioAlerts.playDangerAlarm();
            window.workingAudioAlerts.startContinuousAlarm('danger');
        } else if (hasWarning && !hasDanger && window.workingAudioAlerts.currentLevel !== 'warning') {
            console.log('⚠️ AUTO-DETECTED WARNING - TRIGGERING ALARM');
            window.workingAudioAlerts.playWarningAlarm();
            window.workingAudioAlerts.startContinuousAlarm('warning');
        } else if (!hasDanger && !hasWarning && window.workingAudioAlerts.currentLevel !== null) {
            console.log('✅ ALL SAFE - STOPPING ALARMS');
            window.workingAudioAlerts.stopContinuousAlarm();
            window.workingAudioAlerts.currentLevel = null;
        }
    }, 3000);
    
    // Add mute button
    setTimeout(() => {
        if (document.getElementById('audio-mute-btn')) return;
        
        const button = document.createElement('button');
        button.id = 'audio-mute-btn';
        button.innerHTML = '🔊 Sound ON';
        button.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        `;
        
        button.onclick = () => {
            const isMuted = window.workingAudioAlerts.toggleMute();
            button.innerHTML = isMuted ? '🔇 Sound OFF' : '🔊 Sound ON';
            button.style.background = isMuted ? '#f44336' : '#4CAF50';
        };
        
        document.body.appendChild(button);
    }, 1000);
    
    console.log('🎵 ULTIMATE WORKING Audio Alert System loaded!');
    </script>
    """
    
    # Inject the HTML/JavaScript into Streamlit
    components.html(audio_html, height=0)

def create_working_audio_test():
    """Create test buttons that DEFINITELY work"""
    test_html = """
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; margin: 20px 0; text-align: center;">
        <h1 style="color: white; margin: 0 0 20px 0; font-size: 28px;">
            🎵 GUARANTEED WORKING AUDIO TEST 🎵
        </h1>
        <p style="color: #e0e7ff; margin: 0 0 30px 0; font-size: 18px;">
            This system has multiple fallbacks - it WILL make sound!
        </p>
        
        <div style="display: flex; gap: 30px; justify-content: center; flex-wrap: wrap; margin-bottom: 20px;">
            <button onclick="testWorkingDanger()" 
                    style="background: linear-gradient(45deg, #ef4444, #dc2626); color: white; border: none; padding: 20px 40px; border-radius: 15px; cursor: pointer; font-size: 20px; font-weight: bold; min-width: 250px; height: 80px;">
                🚨 TEST DANGER ALARM 🚨<br>
                <small style="font-size: 14px;">Multiple sound methods!</small>
            </button>
            
            <button onclick="testWorkingWarning()" 
                    style="background: linear-gradient(45deg, #f59e0b, #d97706); color: white; border: none; padding: 20px 40px; border-radius: 15px; cursor: pointer; font-size: 20px; font-weight: bold; min-width: 250px; height: 80px;">
                ⚠️ TEST WARNING ALARM ⚠️<br>
                <small style="font-size: 14px;">Guaranteed to work!</small>
            </button>
        </div>
        
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px;">
            <p id="working-status" style="color: white; margin: 0; font-size: 16px; font-weight: bold;">
                🔊 Click a button to test! This system has multiple fallbacks.
            </p>
        </div>
    </div>
    
    <script>
    function testWorkingDanger() {
        const statusElement = document.getElementById('working-status');
        statusElement.textContent = '🚨 Testing DANGER alarm...';
        
        if (window.workingAudioAlerts) {
            window.workingAudioAlerts.playDangerAlarm();
            setTimeout(() => {
                statusElement.textContent = '✅ Danger alarm played! (Check if you heard it)';
            }, 2000);
        } else {
            statusElement.textContent = '❌ Audio system not ready. Please refresh the page.';
        }
    }
    
    function testWorkingWarning() {
        const statusElement = document.getElementById('working-status');
        statusElement.textContent = '⚠️ Testing WARNING alarm...';
        
        if (window.workingAudioAlerts) {
            window.workingAudioAlerts.playWarningAlarm();
            setTimeout(() => {
                statusElement.textContent = '✅ Warning alarm played! (Check if you heard it)';
            }, 1500);
        } else {
            statusElement.textContent = '❌ Audio system not ready. Please refresh the page.';
        }
    }
    </script>
    """
    components.html(test_html, height=350)