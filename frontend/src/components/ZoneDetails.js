import React from 'react';
import { MapPin, CheckCircle, AlertCircle, AlertTriangle } from 'lucide-react';

const ZoneDetails = ({ zone }) => {
  if (!zone) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Zone Details</h3>
        <div className="text-center py-10 text-gray-400">
          <MapPin className="h-10 w-10 mx-auto mb-2" />
          <p>Select a zone to view details</p>
        </div>
      </div>
    );
  }

  const getRiskIcon = (riskLevel) => {
    switch (riskLevel) {
      case 'CRITICAL':
        return <AlertTriangle className="text-red-600" size={32} />;
      case 'WARNING':
        return <AlertCircle className="text-yellow-600" size={32} />;
      case 'LOW':
      default:
        return <CheckCircle className="text-green-600" size={32} />;
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'CRITICAL':
        return 'red';
      case 'WARNING':
        return 'yellow';
      case 'LOW':
      default:
        return 'green';
    }
  };

  const getRecommendation = (riskLevel) => {
    switch (riskLevel) {
      case 'CRITICAL':
        return 'Immediate evacuation recommended';
      case 'WARNING':
        return 'Increased monitoring required';
      case 'LOW':
      default:
        return 'Continue normal operations';
    }
  };

  const riskColor = getRiskColor(zone.risk_level);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Zone Details</h3>
      <div className="text-center mb-4">
        <div className={`h-16 w-16 rounded-full bg-${riskColor}-100 flex items-center justify-center mx-auto mb-2`}>
          {getRiskIcon(zone.risk_level)}
        </div>
        <h4 className={`text-xl font-bold text-${riskColor}-800`}>Zone {zone.id}</h4>
        <p className={`text-sm text-${riskColor}-600`}>
          {zone.risk_level === 'LOW' ? 'Normal operating conditions' : 
           zone.risk_level === 'WARNING' ? 'Elevated risk detected' : 
           'Critical conditions detected'}
        </p>
      </div>
      
      <div className="space-y-3">
        <div className="flex justify-between">
          <span className="text-sm font-medium text-gray-500">Risk Level</span>
          <span className={`text-sm font-medium text-${riskColor}-600`}>
            {zone.risk_level === 'LOW' ? 'Low' : 
             zone.risk_level === 'WARNING' ? 'Medium' : 'High'}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm font-medium text-gray-500">Displacement</span>
          <span className="text-sm font-medium text-gray-900">
            {zone.displacement ? `${zone.displacement} mm` : '2.1 mm'}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm font-medium text-gray-500">Vibration</span>
          <span className="text-sm font-medium text-gray-900">
            {zone.vibration ? `${zone.vibration} g` : '1.2 g'}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm font-medium text-gray-500">Last Updated</span>
          <span className="text-sm font-medium text-gray-900">
            {new Date().toLocaleTimeString()}
          </span>
        </div>
        
        <div className="pt-3 mt-3 border-t border-gray-200">
          <p className="text-sm font-medium text-gray-500">Recommendation</p>
          <p className="text-sm text-gray-900 mt-1">
            {getRecommendation(zone.risk_level)}
          </p>
        </div>
      </div>
      
      <button className="mt-4 w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors">
        View Detailed Report
      </button>
    </div>
  );
};

export default ZoneDetails;