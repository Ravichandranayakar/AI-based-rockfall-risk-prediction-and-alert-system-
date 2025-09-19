import React from 'react';
import { RefreshCw, Maximize, AlertTriangle } from 'lucide-react';

const MineMap = ({ zones = [], onZoneSelect, selectedZone }) => {
  // Ensure zones is an array
  const zonesArray = Array.isArray(zones) ? zones : [];
  
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

  return (
    <div className="bg-white rounded-lg shadow p-6">
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
          <button className="px-3 py-1 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300 flex items-center transition-colors">
            <Maximize className="h-4 w-4 mr-1" />
            Fullscreen
          </button>
        </div>
      </div>
      
      <div className="relative h-96 bg-gray-200 rounded-lg overflow-hidden">
        <div className="absolute inset-0">
          <div className="grid grid-cols-3 grid-rows-2 h-full w-full gap-2 p-4">
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