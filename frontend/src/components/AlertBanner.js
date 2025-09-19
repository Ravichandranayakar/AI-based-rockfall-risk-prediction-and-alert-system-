import React from 'react';
import { AlertCircle, X } from 'lucide-react';

const AlertBanner = ({ message, onDismiss }) => {
  return (
    <div className="bg-red-600 text-white px-4 py-3 rounded-md mb-6 flex items-center justify-between animate-pulse-red">
      <div className="flex items-center">
        <AlertCircle className="mr-2" size={20} />
        <span className="font-bold">HIGH RISK ALERT:</span>
        <span className="ml-2">{message}</span>
      </div>
      <button 
        onClick={onDismiss}
        className="text-white hover:text-gray-200 transition-colors"
      >
        <X size={20} />
      </button>
    </div>
  );
};

export default AlertBanner;