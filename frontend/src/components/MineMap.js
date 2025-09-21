import React, { useState, useEffect } from 'react';
import { RefreshCw, Maximize, Minimize, AlertTriangle, Mountain, MapPin, Zap, Shield, Activity } from 'lucide-react';

const MineMap = ({ zones = [], onZoneSelect, selectedZone }) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  // Ensure zones is an array
  const zonesArray = Array.isArray(zones) ? zones : [];

  // Listen for fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);
  
  const getZoneColor = (riskLevel) => {
    switch (riskLevel) {
      case 'CRITICAL':
        return 'bg-red-200 border-red-400 text-red-900';
      case 'WARNING':
        return 'bg-yellow-200 border-yellow-400 text-yellow-900';
      case 'LOW':
      default:
        return 'bg-green-200 border-green-400 text-green-900';
    }
  };

  const getRiskText = (riskLevel) => {
    switch (riskLevel) {
      case 'CRITICAL':
        return 'HIGH RISK';
      case 'WARNING':
        return 'MEDIUM RISK';
      case 'LOW':
      default:
        return 'LOW RISK';
    }
  };

  const handleRefresh = () => {
    console.log('Refreshing data...');
    // Trigger a refresh by calling the parent component's refresh function
    if (window.location) {
      window.location.reload();
    }
  };

  const handleFullscreen = () => {
    const mapElement = document.getElementById('mine-map-container');
    if (mapElement) {
      if (!document.fullscreenElement && !isFullscreen) {
        // Try native fullscreen first
        if (mapElement.requestFullscreen) {
          mapElement.requestFullscreen().then(() => {
            setIsFullscreen(true);
            console.log('Entered fullscreen mode');
          }).catch(err => {
            console.log('Fullscreen not supported, using fallback');
            enterFallbackFullscreen(mapElement);
          });
        } else {
          // Fallback for browsers that don't support fullscreen
          enterFallbackFullscreen(mapElement);
        }
      } else if (document.fullscreenElement) {
        document.exitFullscreen().then(() => {
          setIsFullscreen(false);
          console.log('Exited fullscreen mode');
        });
      } else {
        exitFallbackFullscreen(mapElement);
      }
    }
  };

  const enterFallbackFullscreen = (element) => {
    element.classList.add('mine-map-maximized');
    setIsFullscreen(true);
    
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.id = 'fullscreen-close-btn';
    closeBtn.innerHTML = '✕ Close Fullscreen';
    closeBtn.style.cssText = `
      position: absolute;
      top: 1rem;
      right: 1rem;
      background: #ef4444;
      color: white;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 0.5rem;
      cursor: pointer;
      font-weight: bold;
      z-index: 10000;
    `;
    closeBtn.onclick = () => exitFallbackFullscreen(element);
    element.appendChild(closeBtn);
  };

  const exitFallbackFullscreen = (element) => {
    element.classList.remove('mine-map-maximized');
    setIsFullscreen(false);
    
    // Remove close button
    const closeBtn = document.getElementById('fullscreen-close-btn');
    if (closeBtn) {
      closeBtn.remove();
    }
  };

  return (
    <div id="mine-map-container" className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-gray-900">Mine Zone Map</h3>
        <div className="flex space-x-2">
          <button 
            onClick={handleRefresh}
            className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 flex items-center transition-colors"
          >
            <RefreshCw className="h-4 w-4 mr-1" />
            Refresh
          </button>
          <button 
            onClick={handleFullscreen}
            className="px-3 py-1 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300 flex items-center transition-colors"
            title={isFullscreen ? "Exit fullscreen" : "View map in fullscreen"}
          >
            {isFullscreen ? <Minimize className="h-4 w-4 mr-1" /> : <Maximize className="h-4 w-4 mr-1" />}
            {isFullscreen ? "Exit" : "Fullscreen"}
          </button>
        </div>
      </div>
      
      <div className={`relative ${isFullscreen ? 'h-screen' : 'h-96'} bg-gray-200 rounded-lg overflow-hidden`}>
        <div className="absolute inset-0">
          <div className={`grid grid-cols-3 grid-rows-2 h-full w-full gap-2 p-4 ${isFullscreen ? 'gap-4 p-8' : ''}`}>
            {zonesArray.slice(0, 6).map((zone, index) => (
              <div
                key={zone.id}
                className={`map-zone ${getZoneColor(zone.risk_level)} border-4 rounded-lg flex flex-col items-center justify-center cursor-pointer hover:shadow-lg transition-all duration-200 ${
                  selectedZone?.id === zone.id ? 'ring-4 ring-blue-500' : ''
                }`}
                onClick={() => {
                  console.log('Zone clicked:', zone.id);
                  onZoneSelect(zone.id);
                }}
              >
                <span className="text-xl font-bold">Zone {zone.id}</span>
                <span className="text-sm font-semibold">{getRiskText(zone.risk_level)}</span>
                {zone.risk_level === 'CRITICAL' && (
                  <AlertTriangle className="text-red-600 mt-1" size={20} />
                )}
              </div>
            ))}
            
            {/* Fill remaining slots if less than 6 zones */}
            {Array.from({ length: Math.max(0, 6 - zonesArray.length) }, (_, index) => (
              <div
                key={`empty-${index}`}
                className="bg-gray-100 border-2 border-gray-200 rounded-lg flex flex-col items-center justify-center"
              >
                <span className="text-sm text-gray-400">Zone {String.fromCharCode(65 + zonesArray.length + index)}</span>
                <span className="text-xs text-gray-400">No Data</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MineMap;