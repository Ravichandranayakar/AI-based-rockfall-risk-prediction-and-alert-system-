import React from 'react';
import { CheckCircle, AlertCircle, AlertTriangle, Clock } from 'lucide-react';

const Dashboard = ({ zones = [], lastPrediction, alerts = [] }) => {
  // Ensure zones is an array
  const zonesArray = Array.isArray(zones) ? zones : [];
  
  const safeZones = zonesArray.filter(z => z.risk_level === 'LOW').length;
  const warningZones = zonesArray.filter(z => z.risk_level === 'WARNING').length;
  const criticalZones = zonesArray.filter(z => z.risk_level === 'CRITICAL').length;
  
  const lastUpdated = new Date().toLocaleTimeString();

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      {/* Risk Summary */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Risk Summary</h3>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center mr-3">
              <CheckCircle className="text-green-600" size={24} />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Safe Zones</p>
              <p className="text-2xl font-semibold text-gray-900">{safeZones}</p>
            </div>
          </div>
          <div className="flex items-center">
            <div className="h-12 w-12 rounded-full bg-yellow-100 flex items-center justify-center mr-3">
              <AlertCircle className="text-yellow-600" size={24} />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Warning Zones</p>
              <p className="text-2xl font-semibold text-gray-900">{warningZones}</p>
            </div>
          </div>
          <div className="flex items-center">
            <div className="h-12 w-12 rounded-full bg-red-100 flex items-center justify-center mr-3">
              <AlertTriangle className="text-red-600" size={24} />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Critical Zones</p>
              <p className="text-2xl font-semibold text-gray-900">{criticalZones}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Last Prediction */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Last Prediction</h3>
        <div className="flex items-center">
          <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center mr-3">
            <Clock className="text-blue-600" size={24} />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Last Updated</p>
            <p className="text-xl font-semibold text-gray-900">{lastUpdated}</p>
          </div>
        </div>
        <div className="mt-4">
          <p className="text-sm font-medium text-gray-500">Next Prediction</p>
          <p className="text-xl font-semibold text-gray-900">In 5 minutes</p>
        </div>
      </div>

      {/* System Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">System Status</h3>
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-gray-500">AI Model</span>
          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
            Active
          </span>
        </div>
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-gray-500">Data Feed</span>
          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
            Receiving
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-500">Alert System</span>
          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
            Enabled
          </span>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;