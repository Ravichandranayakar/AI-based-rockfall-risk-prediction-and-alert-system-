import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Mock data for development
const mockZones = [
  { id: 'A', name: 'North_Pit_Wall', risk_level: 'LOW', displacement: 2.1, vibration: 1.2, temperature: 22, humidity: 60 },
  { id: 'B', name: 'South_Slope', risk_level: 'CRITICAL', displacement: 12.4, vibration: 3.8, temperature: 25, humidity: 58 },
  { id: 'C', name: 'East_Bench', risk_level: 'LOW', displacement: 1.8, vibration: 1.1, temperature: 21, humidity: 62 },
  { id: 'D', name: 'West_Highwall', risk_level: 'WARNING', displacement: 7.2, vibration: 2.9, temperature: 24, humidity: 59 },
  { id: 'E', name: 'Central_Zone', risk_level: 'LOW', displacement: 2.3, vibration: 1.3, temperature: 23, humidity: 61 },
  { id: 'F', name: 'North_Slope', risk_level: 'LOW', displacement: 1.9, vibration: 1.0, temperature: 22, humidity: 63 },
];

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
  // Always use mock data for now to ensure colors work
  console.log('Using mock zone data');
  return mockZones;
};

export const fetchAlerts = async () => {
  // Always use mock data for now to ensure alerts work
  console.log('Using mock alert data');
  return mockAlerts;
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