import React, { useEffect, useRef, useState } from 'react';
import { Volume2, VolumeX } from 'lucide-react';

const AudioAlarm = ({ isActive, riskLevel, onToggleMute }) => {
  const audioRef = useRef(null);
  const [isMuted, setIsMuted] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  // Create audio context and generate alarm sounds
  useEffect(() => {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    const createAlarmSound = (frequency, duration) => {
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);
      oscillator.type = 'sine';
      
      gainNode.gain.setValueAtTime(0, audioContext.currentTime);
      gainNode.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + 0.1);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
      
      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + duration);
      
      return { oscillator, gainNode };
    };

    const playAlarmSequence = () => {
      if (isMuted || !isActive) {
        return;
      }
      
      if (riskLevel === 'CRITICAL') {
        // Critical: Rapid high-pitched beeps
        const sequence = [
          { freq: 1000, duration: 0.2 },
          { freq: 0, duration: 0.1 },
          { freq: 1000, duration: 0.2 },
          { freq: 0, duration: 0.1 },
          { freq: 1200, duration: 0.3 },
          { freq: 0, duration: 0.2 }
        ];
        
        let delay = 0;
        sequence.forEach(({ freq, duration }) => {
          if (freq > 0) {
            setTimeout(() => createAlarmSound(freq, duration), delay * 1000);
          }
          delay += duration;
        });
        
        setIsPlaying(true);
        setTimeout(() => setIsPlaying(false), delay * 1000);
        
      } else if (riskLevel === 'WARNING') {
        // Warning: Moderate beeps
        createAlarmSound(800, 0.5);
        setIsPlaying(true);
        setTimeout(() => setIsPlaying(false), 500);
      }
    };

    if (isActive && !isMuted) {
      playAlarmSequence();
      
      // Repeat alarm for critical alerts
      const interval = riskLevel === 'CRITICAL' ? 
        setInterval(playAlarmSequence, 3000) : null;
      
      return () => {
        if (interval) {
          clearInterval(interval);
        }
      };
    }
  }, [isActive, riskLevel, isMuted]);

  const toggleMute = () => {
    setIsMuted(!isMuted);
    if (onToggleMute) {
      onToggleMute(!isMuted);
    }
  };

  if (!isActive) {
    return null;
  }

  return (
    <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
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
          <span className="font-bold">
            {riskLevel === 'CRITICAL' ? '🚨 CRITICAL ALERT' : '⚠️ WARNING ALERT'}
          </span>
        </div>
        
        <button
          onClick={toggleMute}
          className="p-1 rounded hover:bg-black hover:bg-opacity-20 transition-colors"
          title={isMuted ? 'Unmute alarm' : 'Mute alarm'}
        >
          {isMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
        </button>
      </div>
      
      <div className="mt-2 text-sm">
        {riskLevel === 'CRITICAL' 
          ? 'Immediate evacuation required!' 
          : 'Increased monitoring required!'}
      </div>
    </div>
  );
};

export default AudioAlarm;