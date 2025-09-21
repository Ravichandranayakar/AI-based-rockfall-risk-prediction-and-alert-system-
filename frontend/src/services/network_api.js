import axios from 'axios';

// Detect if we're running in network mode or local mode
const getApiBaseUrl = () => {
  // Check if we're accessing from another device (not localhost)
  const hostname = window.location.hostname;
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    // Local development
    return 'http://localhost:5000';
  } else {
    // Network access - use the same IP as the frontend
    return `http://${hostname}:5000`;
  }
};

const API_BASE_URL = getApiBaseUrl();

console.log('🌐 API Configuration:', {
  frontend_url: window.location.origin,
  backend_url: API_BASE_URL,
  network_mode: window.location.hostname !== 'localhost'
});

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Mock data for development - with dynamic scenario rotation
let scenarioIndex = 0; // Start with safe scenario (no immediate sound)
const scenarios = [
  // Scenario 1: All Safe (No alarms on startup)
  [
    { id: 'A', name: 'North_Pit_Wall', risk_level: 'LOW', displacement: 2.1, vibration: 1.2, temperature: 22, humidity: 60 },
    { id: 'B', name: 'South_Slope', risk_level: 'LOW', displacement: 3.2, vibration: 1.4, temperature: 25, humidity: 58 },
    { id: 'C', name: 'East_Bench', risk_level: 'LOW', displacement: 1.8, vibration: 1.1, temperature: 21, humidity: 62 },
    { id: 'D', name: 'West_Highwall', risk_level: 'LOW', displacement: 2.5, vibration: 1.3, temperature: 24, humidity: 59 },
    { id: 'E', name: 'Central_Zone', risk_level: 'LOW', displacement: 2.3, vibration: 1.3, temperature: 23, humidity: 61 },
    { id: 'F', name: 'North_Slope', risk_level: 'LOW', displacement: 1.9, vibration: 1.0, temperature: 22, humidity: 63 },
  ],
  // Scenario 2: Warning Conditions 
  [
    { id: 'A', name: 'North_Pit_Wall', risk_level: 'LOW', displacement: 2.1, vibration: 1.2, temperature: 22, humidity: 60 },
    { id: 'B', name: 'South_Slope', risk_level: 'WARNING', displacement: 6.8, vibration: 2.5, temperature: 25, humidity: 58 },
    { id: 'C', name: 'East_Bench', risk_level: 'LOW', displacement: 1.8, vibration: 1.1, temperature: 21, humidity: 62 },
    { id: 'D', name: 'West_Highwall', risk_level: 'WARNING', displacement: 7.2, vibration: 2.9, temperature: 24, humidity: 59 },
    { id: 'E', name: 'Central_Zone', risk_level: 'LOW', displacement: 2.3, vibration: 1.3, temperature: 23, humidity: 61 },
    { id: 'F', name: 'North_Slope', risk_level: 'LOW', displacement: 1.9, vibration: 1.0, temperature: 22, humidity: 63 },
  ],
  // Scenario 3: Critical Emergency 
  [
    { id: 'A', name: 'North_Pit_Wall', risk_level: 'LOW', displacement: 2.1, vibration: 1.2, temperature: 22, humidity: 60 },
    { id: 'B', name: 'South_Slope', risk_level: 'CRITICAL', displacement: 12.5, vibration: 5.8, temperature: 25, humidity: 58 },
    { id: 'C', name: 'East_Bench', risk_level: 'WARNING', displacement: 8.2, vibration: 3.1, temperature: 21, humidity: 62 },
    { id: 'D', name: 'West_Highwall', risk_level: 'LOW', displacement: 2.5, vibration: 1.3, temperature: 24, humidity: 59 },
    { id: 'E', name: 'Central_Zone', risk_level: 'LOW', displacement: 2.3, vibration: 1.3, temperature: 23, humidity: 61 },
    { id: 'F', name: 'North_Slope', risk_level: 'LOW', displacement: 1.9, vibration: 1.0, temperature: 22, humidity: 63 },
  ],
  // Scenario 4: Multiple Warnings
  [
    { id: 'A', name: 'North_Pit_Wall', risk_level: 'WARNING', displacement: 9.1, vibration: 4.2, temperature: 22, humidity: 60 },
    { id: 'B', name: 'South_Slope', risk_level: 'LOW', displacement: 3.2, vibration: 1.4, temperature: 25, humidity: 58 },
    { id: 'C', name: 'East_Bench', risk_level: 'WARNING', displacement: 8.8, vibration: 3.8, temperature: 21, humidity: 62 },
    { id: 'D', name: 'West_Highwall', risk_level: 'WARNING', displacement: 7.2, vibration: 2.9, temperature: 24, humidity: 59 },
    { id: 'E', name: 'Central_Zone', risk_level: 'LOW', displacement: 2.3, vibration: 1.3, temperature: 23, humidity: 61 },
    { id: 'F', name: 'North_Slope', risk_level: 'LOW', displacement: 1.9, vibration: 1.0, temperature: 22, humidity: 63 },
  ]
];

// Advanced rotation logic - changes every 20 seconds with variety
const getCurrentMockZones = () => {
  const now = Date.now();
  const cycleTime = 20000; // 20 seconds per scenario
  const currentCycle = Math.floor(now / cycleTime);
  
  // Rotate through scenarios: 0 -> 1 -> 2 -> 3 -> 1 -> 2 -> 3 -> 0 (skip scenario 0 after first time)
  if (currentCycle === 0) {
    scenarioIndex = 0; // Start safe
  } else {
    scenarioIndex = ((currentCycle - 1) % 3) + 1; // Rotate 1, 2, 3
  }
  
  const selectedScenario = scenarios[scenarioIndex];
  console.log(`🎭 Scenario ${scenarioIndex + 1}/4 active (changes every 20s)`);
  
  return selectedScenario.map(zone => ({
    zone_id: zone.id,
    zone_name: zone.name.replace(/_/g, ' '),
    risk_level: zone.risk_level,
    risk_score: zone.displacement,
    last_updated: new Date().toISOString(),
    sensors: {
      displacement: zone.displacement,
      vibration: zone.vibration,
      temperature: zone.temperature,
      humidity: zone.humidity
    },
    location: {
      x: Math.random() * 400 + 50,
      y: Math.random() * 300 + 50
    }
  }));
};

export const fetchZones = async () => {
  try {
    console.log('🌐 Fetching zones from:', API_BASE_URL);
    const response = await api.get('/zones');
    console.log('✅ API Response received:', response.data);
    return response.data.zones || getCurrentMockZones();
  } catch (error) {
    console.warn('⚠️ API failed, using mock data:', error.message);
    return getCurrentMockZones();
  }
};

export const fetchAlerts = async () => {
  try {
    console.log('🌐 Fetching alerts from:', API_BASE_URL);
    const response = await api.get('/alerts');
    console.log('✅ Alerts received:', response.data);
    return response.data.alerts || [];
  } catch (error) {
    console.warn('⚠️ Alerts API failed:', error.message);
    
    // Generate mock alerts based on current zones
    const zones = getCurrentMockZones();
    const alerts = zones
      .filter(zone => zone.risk_level !== 'LOW')
      .map(zone => ({
        alert_id: `MOCK_${zone.zone_id}_${Date.now()}`,
        zone_id: zone.zone_id,
        zone_name: zone.zone_name,
        alert_level: zone.risk_level,
        risk_score: zone.risk_score,
        timestamp: new Date().toISOString(),
        status: 'ACTIVE',
        message: `${zone.zone_name} shows ${zone.risk_level.toLowerCase()} risk conditions`,
        recommended_action: zone.risk_level === 'CRITICAL' 
          ? 'Immediate evacuation required - rockfall imminent'
          : 'Increase monitoring - restrict access to non-essential personnel'
      }));
    
    return alerts;
  }
};

export const fetchPrediction = async (sensorData) => {
  try {
    console.log('🌐 Sending prediction request to:', API_BASE_URL);
    const response = await api.post('/predict', sensorData);
    return response.data;
  } catch (error) {
    console.warn('⚠️ Prediction API failed:', error.message);
    
    // Mock prediction
    const riskScore = Math.random() * 10;
    const riskLevel = riskScore < 3 ? 'LOW' : riskScore < 6 ? 'WARNING' : 'CRITICAL';
    
    return {
      risk_score: Math.round(riskScore * 100) / 100,
      risk_level: riskLevel,
      confidence: Math.round((Math.random() * 0.2 + 0.8) * 1000) / 1000,
      timestamp: new Date().toISOString()
    };
  }
};

// Test connection on startup
export const testConnection = async () => {
  try {
    console.log('🌐 Testing connection to:', API_BASE_URL);
    const response = await api.get('/health');
    console.log('✅ Backend connection successful:', response.data);
    return true;
  } catch (error) {
    console.warn('⚠️ Backend connection failed, using mock mode:', error.message);
    return false;
  }
};

export default api;