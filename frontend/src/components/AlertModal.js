import React from 'react';
import { AlertTriangle } from 'lucide-react';

const AlertModal = ({ message, onClose }) => {
  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center">
      <div className="relative mx-auto p-5 border max-w-md shadow-lg rounded-md bg-white animate-fade-in">
        <div className="mt-3 text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
            <AlertTriangle className="text-red-600" size={24} />
          </div>
          <h3 className="text-lg leading-6 font-medium text-gray-900 mt-3">
            High Risk Alert
          </h3>
          <div className="mt-2 px-7 py-3">
            <p className="text-sm text-gray-500">
              {message}
            </p>
          </div>
          <div className="items-center px-4 py-3">
            <button 
              onClick={onClose}
              className="px-4 py-2 bg-blue-600 text-white text-base font-medium rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
            >
              Acknowledge
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlertModal;