import React, { useEffect, useRef, useState } from 'react';
import { Volume2, VolumeX, AlertTriangle, TestTube, Play, Speaker, Zap, Shield } from 'lucide-react';

const AudioControlPanel = ({ isActive, riskLevel, onToggleMute, onTestCritical, onTestWarning }) => {
  const audioRef = useRef(null);
  const [isMuted, setIsMuted] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioContext, setAudioContext] = useState(null);

  // Initialize audio context
  useEffect(() => {
    try {
      const context = new (window.AudioContext || window.webkitAudioContext)();
      setAudioContext(context);
    } catch (e) {
      console.warn('Audio context not supported');
    }
  }, []);

  const createAlarmSound = (frequency, duration, volume = 0.3) => {
    if (!audioContext || isMuted) {
      return;
    }
    
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0, audioContext.currentTime);
    gainNode.gain.linearRampToValueAtTime(volume, audioContext.currentTime + 0.1);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + duration);
    
    return { oscillator, gainNode };
  };

  const playDangerAlarm = () => {
    if (isMuted || !audioContext) {
      return;
    }
    
    // Critical: Rapid high-pitched beeps
    const sequence = [
      { freq: 1000, duration: 0.2, delay: 0 },
      { freq: 1200, duration: 0.2, delay: 0.3 },
      { freq: 1000, duration: 0.2, delay: 0.6 },
      { freq: 1400, duration: 0.3, delay: 0.9 }
    ];
    
    sequence.forEach(({ freq, duration, delay }) => {
      setTimeout(() => createAlarmSound(freq, duration, 0.4), delay * 1000);
    });
    
    setIsPlaying(true);
    setTimeout(() => setIsPlaying(false), 1200);
  };

  const playWarningAlarm = () => {
    if (isMuted || !audioContext) {
      console.log('Warning alarm blocked:', { isMuted, audioContext: !!audioContext });
      return;
    }
    
    console.log('🔔 Playing WARNING alarm sound');
    
    // Warning: Two-tone alarm sequence 
    const sequence = [
      { freq: 600, duration: 0.4, delay: 0 },
      { freq: 800, duration: 0.4, delay: 0.5 },
      { freq: 600, duration: 0.4, delay: 1.0 }
    ];
    
    sequence.forEach(({ freq, duration, delay }) => {
      setTimeout(() => createAlarmSound(freq, duration, 0.4), delay * 1000);
    });
    
    setIsPlaying(true);
    setTimeout(() => setIsPlaying(false), 1500);
  };

  // Auto-play based on risk level
  useEffect(() => {
    console.log('🎵 Audio effect triggered:', { isActive, riskLevel, isMuted });
    
    if (isActive && !isMuted && audioContext) {
      if (riskLevel === 'CRITICAL') {
        console.log('🚨 Playing CRITICAL alarm');
        playDangerAlarm();
        const interval = setInterval(playDangerAlarm, 2000); // Fast: every 2 seconds
        return () => clearInterval(interval);
      } else if (riskLevel === 'WARNING') {
        console.log('⚠️ Playing WARNING alarm');
        playWarningAlarm();
        const interval = setInterval(playWarningAlarm, 3000); // Fast: every 3 seconds
        return () => clearInterval(interval);
      }
    } else {
      console.log('🔇 Audio blocked or inactive:', { 
        isActive, 
        isMuted, 
        hasAudioContext: !!audioContext,
        riskLevel 
      });
    }
  }, [isActive, riskLevel, isMuted, audioContext]);

  const toggleMute = () => {
    setIsMuted(!isMuted);
    if (onToggleMute) {
      onToggleMute(!isMuted);
    }
  };

  const handleTestCritical = () => {
    playDangerAlarm();
    if (onTestCritical) {
      onTestCritical();
    }
  };

  const handleTestWarning = () => {
    playWarningAlarm();
    if (onTestWarning) {
      onTestWarning();
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Active Alert Display */}
      {isActive && (
        <div className={`mb-4 p-4 rounded-lg shadow-lg ${
          riskLevel === 'CRITICAL' ? 'bg-red-600' : 'bg-orange-500'
        } text-white animate-pulse`}>
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              {isPlaying && (
                <div className="flex space-x-1">
                  <div className="w-2 h-4 bg-white animate-bounce"></div>
                  <div className="w-2 h-4 bg-white animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-4 bg-white animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              )}
              <AlertTriangle size={20} />
              <span className="font-bold">
                {riskLevel === 'CRITICAL' ? '🚨 CRITICAL ALERT' : '⚠️ WARNING ALERT'}
              </span>
            </div>
          </div>
          
          <div className="mt-2 text-sm">
            {riskLevel === 'CRITICAL' 
              ? 'Immediate evacuation required!' 
              : 'Increased monitoring required!'}
          </div>
        </div>
      )}

      {/* Audio Control Panel */}
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-bold text-gray-900 flex items-center">
            <Speaker className="mr-2 text-blue-600" size={16} />
            Audio System
          </h3>
          <button
            onClick={toggleMute}
            className={`p-2 rounded-full transition-colors ${
              isMuted 
                ? 'bg-red-100 text-red-600 hover:bg-red-200' 
                : 'bg-green-100 text-green-600 hover:bg-green-200'
            }`}
            title={isMuted ? 'Unmute audio alerts' : 'Mute audio alerts'}
          >
            {isMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
          </button>
        </div>
        
        <div className="space-y-2">
          <button
            onClick={handleTestCritical}
            className="w-full flex items-center justify-center space-x-2 bg-red-500 hover:bg-red-600 text-white px-3 py-2 rounded text-sm font-medium transition-colors"
          >
            <Zap size={14} />
            <span>Test Critical Alarm</span>
          </button>
          
          <button
            onClick={handleTestWarning}
            className="w-full flex items-center justify-center space-x-2 bg-orange-500 hover:bg-orange-600 text-white px-3 py-2 rounded text-sm font-medium transition-colors"
          >
            <Shield size={14} />
            <span>Test Warning Alarm</span>
          </button>
        </div>
        
        <div className="mt-3 text-xs text-gray-600">
          <div className={`flex items-center space-x-1 ${isActive ? 'text-red-600 font-medium' : ''}`}>
            <div className={`w-2 h-2 rounded-full ${isActive ? 'bg-red-500 animate-pulse' : 'bg-green-500'}`}></div>
            <span>{isActive ? '🚨 Alert Active' : '✅ Monitoring'}</span>
          </div>
          <div className="mt-1 flex items-center">
            {isMuted ? <VolumeX size={12} className="mr-1 text-red-500" /> : <Volume2 size={12} className="mr-1 text-green-500" />}
            <span>{isMuted ? 'Audio Muted' : 'Audio Armed'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AudioControlPanel;