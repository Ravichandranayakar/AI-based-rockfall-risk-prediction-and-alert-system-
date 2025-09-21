import React, { useState } from 'react';
import { AlertTriangle, User, Maximize, RefreshCw, Settings, FileText, AlertCircle, Home, LogOut, Shield, Activity, BarChart3, Map, Bell } from 'lucide-react';

const Navigation = ({ onRefresh, currentUser, onLogout }) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().then(() => {
        setIsFullscreen(true);
      }).catch(err => {
        console.log('Error attempting to enable fullscreen:', err);
      });
    } else {
      document.exitFullscreen().then(() => {
        setIsFullscreen(false);
      });
    }
  };

  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh();
    }
    // Visual feedback
    const refreshButton = document.getElementById('refresh-btn');
    if (refreshButton) {
      refreshButton.classList.add('animate-spin');
      setTimeout(() => {
        refreshButton.classList.remove('animate-spin');
      }, 1000);
    }
  };

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      if (onLogout) {
        onLogout();
      }
    }
  };

  const handleTabClick = (tab) => {
    setActiveTab(tab);
    // Scroll to different sections or show/hide components
    const element = document.getElementById(tab);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <nav className="bg-gray-900 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center">
            <AlertTriangle className="text-red-500 mr-2" size={24} />
            <span className="text-xl font-bold">Rockfall AI Prediction System</span>
          </div>
          
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              <button 
                onClick={() => handleTabClick('dashboard')}
                className={`px-3 py-2 rounded-md text-sm font-medium flex items-center ${
                  activeTab === 'dashboard' ? 'bg-gray-800 text-white' : 'text-gray-300 hover:text-white hover:bg-gray-700'
                }`}
              >
                <Home className="mr-1" size={16} />
                Dashboard
              </button>
              <button 
                onClick={() => handleTabClick('alerts')}
                className={`px-3 py-2 rounded-md text-sm font-medium flex items-center ${
                  activeTab === 'alerts' ? 'bg-gray-800 text-white' : 'text-gray-300 hover:text-white hover:bg-gray-700'
                }`}
              >
                <AlertCircle className="mr-1" size={16} />
                Alerts
              </button>
              <button 
                onClick={() => handleTabClick('reports')}
                className={`px-3 py-2 rounded-md text-sm font-medium flex items-center ${
                  activeTab === 'reports' ? 'bg-gray-800 text-white' : 'text-gray-300 hover:text-white hover:bg-gray-700'
                }`}
              >
                <FileText className="mr-1" size={16} />
                Reports
              </button>
              <button 
                onClick={() => handleTabClick('settings')}
                className={`px-3 py-2 rounded-md text-sm font-medium flex items-center ${
                  activeTab === 'settings' ? 'bg-gray-800 text-white' : 'text-gray-300 hover:text-white hover:bg-gray-700'
                }`}
              >
                <Settings className="mr-1" size={16} />
                Settings
              </button>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Refresh Button */}
            <button
              id="refresh-btn"
              onClick={handleRefresh}
              className="p-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
              title="Refresh Data"
            >
              <RefreshCw size={18} />
            </button>
            
            {/* Fullscreen Button */}
            <button
              onClick={toggleFullscreen}
              className="p-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
              title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
            >
              <Maximize size={18} />
            </button>
            
            {/* User Menu */}
            <div className="relative">
              <span className="text-sm mr-2 hidden md:block">
                Operator: <span className="font-medium">{currentUser || 'John Doe'}</span>
              </span>
              <button 
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="bg-gray-800 flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-white"
              >
                <User className="h-8 w-8 p-1 rounded-full bg-gray-700 text-gray-300 hover:bg-gray-600" />
              </button>
              
              {/* User Dropdown Menu */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50">
                  <button 
                    onClick={() => {setShowUserMenu(false); alert('Profile settings coming soon!');}}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <User className="inline mr-2" size={16} />
                    Profile Settings
                  </button>
                  <button 
                    onClick={() => {setShowUserMenu(false); alert('System settings coming soon!');}}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <Settings className="inline mr-2" size={16} />
                    System Settings
                  </button>
                  <hr className="my-1" />
                  <button 
                    onClick={() => {setShowUserMenu(false); handleLogout();}}
                    className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
                  >
                    <LogOut className="inline mr-2" size={16} />
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;