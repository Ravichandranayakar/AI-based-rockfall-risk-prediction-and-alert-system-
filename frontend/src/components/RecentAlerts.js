import React from 'react';
import { AlertTriangle, AlertCircle, CheckCircle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

const RecentAlerts = ({ alerts = [] }) => {
  // Ensure alerts is an array
  const alertsArray = Array.isArray(alerts) ? alerts : [];
  
  const getAlertIcon = (level) => {
    switch (level) {
      case 'CRITICAL':
        return <AlertTriangle className="text-red-600" size={20} />;
      case 'WARNING':
        return <AlertCircle className="text-yellow-600" size={20} />;
      default:
        return <CheckCircle className="text-green-600" size={20} />;
    }
  };

  const getAlertBgColor = (level) => {
    switch (level) {
      case 'CRITICAL':
        return 'bg-red-100';
      case 'WARNING':
        return 'bg-yellow-100';
      default:
        return 'bg-green-100';
    }
  };

  const formatAlertTime = (timestamp) => {
    try {
      return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
    } catch {
      return 'Unknown time';
    }
  };

  const sortedAlerts = alertsArray
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    .slice(0, 5); // Show only latest 5 alerts

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Recent Alerts</h3>
      </div>
      
      {sortedAlerts.length === 0 ? (
        <div className="px-6 py-8 text-center text-gray-500">
          <AlertCircle className="h-8 w-8 mx-auto mb-2" />
          <p>No recent alerts</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-200">
          {sortedAlerts.map((alert) => (
            <div key={alert.alert_id} className="px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
              <div className="flex items-center">
                <div className={`h-10 w-10 rounded-full ${getAlertBgColor(alert.alert_level)} flex items-center justify-center mr-3`}>
                  {getAlertIcon(alert.alert_level)}
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {alert.alert_level === 'CRITICAL' ? 'High Risk Alert' : 
                     alert.alert_level === 'WARNING' ? 'Warning' : 'All Clear'} - Zone {alert.zone_id}
                  </p>
                  <p className="text-sm text-gray-500">
                    {alert.trigger_reason && alert.displacement_mm ? 
                      `${alert.trigger_reason.replace(/_/g, ' ')} (${alert.displacement_mm}mm)` :
                      alert.recommended_action || 'Status update'
                    }
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">
                  {formatAlertTime(alert.timestamp)}
                </p>
                <button className="text-blue-600 text-sm font-medium hover:text-blue-800 transition-colors">
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      
      <div className="px-6 py-4 bg-gray-50 text-right">
        <button className="text-blue-600 text-sm font-medium hover:text-blue-800 transition-colors">
          View All Alerts
        </button>
      </div>
    </div>
  );
};

export default RecentAlerts;