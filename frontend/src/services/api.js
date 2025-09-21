import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

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
    { id: 'B', name: 'South_Slope', risk_level: 'CRITICAL', displacement: 12.4, vibration: 3.8, temperature: 25, humidity: 58 },
    { id: 'C', name: 'East_Bench', risk_level: 'WARNING', displacement: 5.5, vibration: 2.1, temperature: 21, humidity: 62 },
    { id: 'D', name: 'West_Highwall', risk_level: 'WARNING', displacement: 7.2, vibration: 2.9, temperature: 24, humidity: 59 },
    { id: 'E', name: 'Central_Zone', risk_level: 'LOW', displacement: 2.3, vibration: 1.3, temperature: 23, humidity: 61 },
    { id: 'F', name: 'North_Slope', risk_level: 'LOW', displacement: 1.9, vibration: 1.0, temperature: 22, humidity: 63 },
  ]
];

const getCurrentMockZones = () => {
  // Rotate scenarios every 1 refresh (20 seconds each for FAST jury demo)
  return scenarios[scenarioIndex % scenarios.length];
};

// Function to manually set scenario for immediate testing
export const setDemoScenario = (scenarioNumber) => {
  if (scenarioNumber >= 1 && scenarioNumber <= 3) {
    scenarioIndex = (scenarioNumber - 1) * 2; // Set to start of that scenario
    console.log(`🎯 Manually set to Scenario ${scenarioNumber}`);
  }
};

const mockAlerts = [
  {
    alert_id: 'ALT001',
    timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
    zone_id: 'B',
    zone_name: 'South_Slope',
    alert_level: 'CRITICAL',
    risk_score: 9.2,
    trigger_reason: 'critical_displacement',
    recommended_action: 'Immediate evacuation required',
    status: 'ACTIVE',
    displacement_mm: 12.4,
    vibration_mm_s: 3.8
  },
  {
    alert_id: 'ALT002',
    timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
    zone_id: 'D',
    zone_name: 'West_Highwall',
    alert_level: 'WARNING',
    risk_score: 7.2,
    trigger_reason: 'high_vibration',
    recommended_action: 'Increased monitoring required',
    status: 'RESOLVED',
    displacement_mm: 7.2,
    vibration_mm_s: 2.9
  },
  {
    alert_id: 'ALT003',
    timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
    zone_id: 'A',
    zone_name: 'North_Pit_Wall',
    alert_level: 'INFO',
    risk_score: 4.1,
    trigger_reason: 'routine_inspection',
    recommended_action: 'Continue normal operations',
    status: 'RESOLVED',
    displacement_mm: 2.1,
    vibration_mm_s: 1.2
  },
];

export const fetchZones = async () => {
  // Use dynamic scenario rotation for realistic demo
  scenarioIndex++;
  const currentZones = getCurrentMockZones();
  const scenarioNum = (scenarioIndex - 1) % scenarios.length + 1;
  const scenarioName = scenarioNum === 1 ? 'ALL SAFE' : 
                      scenarioNum === 2 ? 'WARNING CONDITIONS' : 'CRITICAL EMERGENCY';
  console.log(`🎯 Demo Scenario ${scenarioNum}: ${scenarioName} (Fast Mode)`);
  return currentZones;
};

export const fetchAlerts = async () => {
  // Generate alerts based on current scenario
  const currentZones = getCurrentMockZones();
  const dynamicAlerts = [];
  
  // Create alerts for zones with WARNING or CRITICAL risk levels
  currentZones.forEach(zone => {
    if (zone.risk_level === 'WARNING') {
      dynamicAlerts.push({
        alert_id: `ALT_${zone.id}_${Date.now()}`,
        timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(), // 5 minutes ago
        zone_id: zone.id,
        zone_name: zone.name,
        alert_level: 'WARNING',
        risk_score: 7.2,
        trigger_reason: 'high_displacement_vibration',
        recommended_action: 'Increased monitoring required',
        status: 'ACTIVE',
        displacement_mm: zone.displacement,
        vibration_mm_s: zone.vibration
      });
    } else if (zone.risk_level === 'CRITICAL') {
      dynamicAlerts.push({
        alert_id: `ALT_${zone.id}_${Date.now()}`,
        timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(), // 2 minutes ago
        zone_id: zone.id,
        zone_name: zone.name,
        alert_level: 'CRITICAL',
        risk_score: 9.2,
        trigger_reason: 'critical_displacement',
        recommended_action: 'Immediate evacuation required',
        status: 'ACTIVE',
        displacement_mm: zone.displacement,
        vibration_mm_s: zone.vibration
      });
    }
  });
  
  // Add some historical alerts if no current alerts
  if (dynamicAlerts.length === 0) {
    dynamicAlerts.push({
      alert_id: 'ALT003',
      timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
      zone_id: 'A',
      zone_name: 'North_Pit_Wall',
      alert_level: 'INFO',
      risk_score: 4.1,
      trigger_reason: 'routine_inspection',
      recommended_action: 'Continue normal operations',
      status: 'RESOLVED',
      displacement_mm: 2.1,
      vibration_mm_s: 1.2
    });
  }
  
  console.log(`📊 Generated ${dynamicAlerts.length} active alerts`);
  return dynamicAlerts;
};

export const fetchPrediction = async (zoneData) => {
  try {
    const response = await api.post('/predict', zoneData);
    return response.data;
  } catch (error) {
    console.warn('API not available, using mock prediction');
    return {
      risk_level: zoneData.risk_level || 'LOW',
      risk_score: zoneData.displacement * 0.7 + zoneData.vibration * 0.3,
      prediction: `Zone ${zoneData.id} assessment complete`,
      timestamp: new Date().toISOString()
    };
  }
};

export default api;