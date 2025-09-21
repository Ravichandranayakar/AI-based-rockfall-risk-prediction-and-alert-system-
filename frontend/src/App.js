import React, { useState, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import LoginPage from './components/LoginPage';
import Navigation from './components/Navigation';
import AlertBanner from './components/AlertBanner';
import Dashboard from './components/Dashboard';
import MineMap from './components/MineMap';
import ZoneDetails from './components/ZoneDetails';
import Charts from './components/Charts';
import RecentAlerts from './components/RecentAlerts';
import AlertModal from './components/AlertModal';
import AudioControlPanel from './components/AudioControlPanel';
import { fetchZones, fetchAlerts, fetchPrediction } from './services/api';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [zones, setZones] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [selectedZone, setSelectedZone] = useState(null);
  const [lastPrediction, setLastPrediction] = useState(null);
  const [showAlert, setShowAlert] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [audioAlarmActive, setAudioAlarmActive] = useState(false);
  const [audioAlarmLevel, setAudioAlarmLevel] = useState('');
  const [isAudioMuted, setIsAudioMuted] = useState(false);

  // Check for existing login session
  useEffect(() => {
    // Force logout for testing - remove this line later if you want persistent login
    localStorage.removeItem('rockfall_user');
    
    const savedUser = localStorage.getItem('rockfall_user');
    console.log('Checking saved user:', savedUser);
    if (savedUser) {
      setCurrentUser(savedUser);
      setIsLoggedIn(true);
      console.log('Auto-logged in as:', savedUser);
    } else {
      console.log('No saved user, showing login page');
    }
  }, []);

  // Fetch initial data when logged in
  useEffect(() => {
    if (isLoggedIn) {
      console.log('User logged in, starting data loading with delay...');
      
      // Add 1 second delay before first data load (quick but prevents immediate sounds)
      const initialDelay = setTimeout(() => {
        loadData();
      }, 1000);
      
      // Set up auto-refresh every 20 seconds for faster demo progression
      const refreshInterval = setInterval(loadData, 20000);
      
      return () => {
        clearTimeout(initialDelay);
        clearInterval(refreshInterval);
      };
    }
  }, [isLoggedIn]);

  const loadData = async () => {
    try {
      const [zonesData, alertsData] = await Promise.all([
        fetchZones(),
        fetchAlerts()
      ]);
      
      setZones(zonesData);
      setAlerts(alertsData);

      // Check for critical alerts
      const criticalAlerts = alertsData.filter(alert => 
        alert.alert_level === 'CRITICAL' && alert.status === 'ACTIVE'
      );
      
      const warningAlerts = alertsData.filter(alert => 
        alert.alert_level === 'WARNING' && alert.status === 'ACTIVE'
      );
      
      if (criticalAlerts.length > 0) {
        const alertMsg = `${criticalAlerts[0].zone_name} shows critical conditions. ${criticalAlerts[0].recommended_action}`;
        setAlertMessage(alertMsg);
        setShowAlert(true);
        setShowModal(true);
        setAudioAlarmActive(true);
        setAudioAlarmLevel('CRITICAL');
        toast.error(alertMsg);
      } else if (warningAlerts.length > 0) {
        const alertMsg = `${warningAlerts[0].zone_name} shows warning conditions. ${warningAlerts[0].recommended_action}`;
        setAudioAlarmActive(true);
        setAudioAlarmLevel('WARNING');
        toast.warn(alertMsg);
      } else {
        // No active critical or warning alerts
        setAudioAlarmActive(false);
        setAudioAlarmLevel('');
      }

    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Failed to load data from server');
    }
  };

  const handleZoneSelect = async (zoneId) => {
    console.log('Selecting zone:', zoneId);
    const zone = zones.find(z => z.id === zoneId);
    if (zone) {
      try {
        // Get fresh prediction for selected zone
        const prediction = await fetchPrediction(zone);
        setLastPrediction(prediction);
        setSelectedZone({ ...zone, prediction });
        console.log('Zone selected:', zone);
      } catch (error) {
        console.error('Error getting prediction:', error);
        setSelectedZone(zone);
      }
    }
  };

  const handleLogin = (username) => {
    console.log('Login attempt for:', username);
    setCurrentUser(username);
    setIsLoggedIn(true);
    localStorage.setItem('rockfall_user', username);
    toast.success(`Welcome, ${username}!`);
    console.log('Login successful, isLoggedIn:', true);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setIsLoggedIn(false);
    localStorage.removeItem('rockfall_user');
    toast.info('Logged out successfully');
  };

  const handleRefresh = () => {
    console.log('Manual refresh triggered');
    loadData();
    toast.info('Data refreshed!');
  };

  const dismissAlert = () => {
    setShowAlert(false);
  };

  const closeModal = () => {
    setShowModal(false);
  };

  const handleTestCritical = () => {
    // Simulate critical alert for testing
    setAudioAlarmActive(true);
    setAudioAlarmLevel('CRITICAL');
    setAlertMessage('TEST: Critical danger detected in Zone B - Immediate evacuation required!');
    setShowAlert(true);
    toast.error('🚨 TEST CRITICAL ALERT: Audio alarm triggered!');
    
    // Auto-clear after 10 seconds
    setTimeout(() => {
      setAudioAlarmActive(false);
      setShowAlert(false);
    }, 10000);
  };

  const handleTestWarning = () => {
    // Simulate warning alert for testing
    setAudioAlarmActive(true);
    setAudioAlarmLevel('WARNING');
    setAlertMessage('TEST: Warning conditions detected in Zone D - Increased monitoring required!');
    setShowAlert(true);
    toast.warn('⚠️ TEST WARNING ALERT: Audio beep triggered!');
    
    // Auto-clear after 8 seconds
    setTimeout(() => {
      setAudioAlarmActive(false);
      setShowAlert(false);
    }, 8000);
  };

  // Show login page if not logged in
  if (!isLoggedIn) {
    console.log('Showing login page, isLoggedIn:', isLoggedIn);
    return (
      <>
        <LoginPage onLogin={handleLogin} />
        <ToastContainer 
          position="top-right"
          autoClose={5000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
        />
      </>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Navigation 
        onRefresh={handleRefresh} 
        currentUser={currentUser}
        onLogout={handleLogout}
      />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {showAlert && (
          <AlertBanner 
            message={alertMessage} 
            onDismiss={dismissAlert} 
          />
        )}

        <div id="dashboard">
          <Dashboard 
            zones={zones} 
            lastPrediction={lastPrediction}
            alerts={alerts}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-2">
            <MineMap 
              zones={zones} 
              onZoneSelect={handleZoneSelect}
              selectedZone={selectedZone}
            />
          </div>
          <ZoneDetails zone={selectedZone} />
        </div>

        <Charts zones={zones} alerts={alerts} />
        
        <div id="alerts">
          <RecentAlerts alerts={alerts} />
        </div>

        {/* Reports Section */}
        <div id="reports" className="mt-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">📊 System Reports</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button className="p-4 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors">
                <h3 className="font-semibold text-blue-900">Daily Report</h3>
                <p className="text-sm text-blue-700">Generate today's safety report</p>
              </button>
              <button className="p-4 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors">
                <h3 className="font-semibold text-green-900">Weekly Summary</h3>
                <p className="text-sm text-green-700">Export weekly analysis</p>
              </button>
              <button className="p-4 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 transition-colors">
                <h3 className="font-semibold text-purple-900">Custom Report</h3>
                <p className="text-sm text-purple-700">Create custom date range</p>
              </button>
            </div>
          </div>
        </div>

        {/* Settings Section */}
        <div id="settings" className="mt-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">⚙️ System Settings</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold mb-2">Alert Thresholds</h3>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Critical Alert Level</label>
                    <input type="range" min="1" max="10" defaultValue="8" className="w-full" />
                    <span className="text-sm text-gray-500">Current: 8.0</span>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Warning Alert Level</label>
                    <input type="range" min="1" max="10" defaultValue="6" className="w-full" />
                    <span className="text-sm text-gray-500">Current: 6.0</span>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2">Notification Settings</h3>
                <div className="space-y-3">
                  <label className="flex items-center">
                    <input type="checkbox" defaultChecked className="mr-2" />
                    <span className="text-sm">Email notifications</span>
                  </label>
                  <label className="flex items-center">
                    <input type="checkbox" defaultChecked className="mr-2" />
                    <span className="text-sm">SMS alerts for critical events</span>
                  </label>
                  <label className="flex items-center">
                    <input 
                      type="checkbox" 
                      checked={!isAudioMuted}
                      onChange={(e) => setIsAudioMuted(!e.target.checked)}
                      className="mr-2" 
                    />
                    <span className="text-sm">Sound alerts</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {showModal && (
        <AlertModal 
          message={alertMessage}
          onClose={closeModal}
        />
      )}

      <AudioControlPanel 
        isActive={audioAlarmActive}
        riskLevel={audioAlarmLevel}
        onToggleMute={setIsAudioMuted}
        onTestCritical={handleTestCritical}
        onTestWarning={handleTestWarning}
      />

      <ToastContainer 
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </div>
  );
}

export default App;