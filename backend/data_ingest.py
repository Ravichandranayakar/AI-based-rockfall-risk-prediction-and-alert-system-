"""
Data Ingestion Module for Rockfall Risk Prediction System
Handles real-time sensor data simulation and MQTT integration
"""

import pandas as pd
import numpy as np
import json
import time
import threading
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
import requests
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SensorDataSimulator:
    """Simulates real-time sensor data for demo purposes"""
    
    def __init__(self, zones_file=None):
        if zones_file is None:
            zones_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    'sample-data', 'zones.json')
        
        with open(zones_file, 'r') as f:
            self.zones_data = json.load(f)
        
        self.zones = [zone['zone_id'] for zone in self.zones_data['zones']]
        self.current_data = {}
        self.running = False
        
        # Initialize current data for each zone
        for zone in self.zones:
            self.current_data[zone] = self.generate_baseline_data(zone)
    
    def generate_baseline_data(self, zone_id):
        """Generate baseline sensor data for a zone"""
        # Get zone characteristics for realistic data
        zone_info = None
        for zone in self.zones_data['zones']:
            if zone['zone_id'] == zone_id:
                zone_info = zone
                break
        
        if zone_info is None:
            zone_info = {'characteristics': {'stability_rating': 'stable'}}
        
        stability = zone_info['characteristics'].get('stability_rating', 'stable')
        
        # Base values depending on stability
        if stability == 'unstable':
            base_displacement = np.random.uniform(3, 8)
            base_vibration = np.random.uniform(0.8, 2.0)
        elif stability == 'moderate':
            base_displacement = np.random.uniform(1, 5)
            base_vibration = np.random.uniform(0.3, 1.2)
        else:  # stable or very_stable
            base_displacement = np.random.uniform(0.5, 3)
            base_vibration = np.random.uniform(0.1, 0.8)
        
        return {
            'zone_id': zone_id,
            'displacement_mm': base_displacement,
            'vibration_mm_s': base_vibration,
            'temperature_c': np.random.uniform(20, 26),
            'humidity_percent': np.random.uniform(50, 75),
            'pressure_kpa': np.random.uniform(100.5, 101.5),
            'accelerometer_x': np.random.uniform(-0.2, 0.2),
            'accelerometer_y': np.random.uniform(-0.2, 0.2),
            'accelerometer_z': np.random.uniform(9.6, 9.9),
            'timestamp': datetime.now().isoformat()
        }
    
    def update_sensor_data(self, zone_id, add_noise=True, trend=None):
        """Update sensor data with realistic variations"""
        current = self.current_data[zone_id]
        
        # Add random variations
        if add_noise:
            displacement_change = np.random.normal(0, 0.3)
            vibration_change = np.random.normal(0, 0.1)
            temp_change = np.random.normal(0, 0.5)
            humidity_change = np.random.normal(0, 2)
        else:
            displacement_change = 0
            vibration_change = 0
            temp_change = 0
            humidity_change = 0
        
        # Apply trend if specified
        if trend == 'increasing_risk':
            displacement_change += 0.2
            vibration_change += 0.05
        elif trend == 'decreasing_risk':
            displacement_change -= 0.1
            vibration_change -= 0.02
        
        # Update values with bounds
        current['displacement_mm'] = max(0, current['displacement_mm'] + displacement_change)
        current['vibration_mm_s'] = max(0, current['vibration_mm_s'] + vibration_change)
        current['temperature_c'] = np.clip(current['temperature_c'] + temp_change, 15, 35)
        current['humidity_percent'] = np.clip(current['humidity_percent'] + humidity_change, 30, 95)
        current['pressure_kpa'] = np.clip(current['pressure_kpa'] + np.random.normal(0, 0.1), 99, 103)
        
        # Update accelerometer with small variations
        current['accelerometer_x'] += np.random.normal(0, 0.01)
        current['accelerometer_y'] += np.random.normal(0, 0.01)
        current['accelerometer_z'] = 9.8 + np.random.normal(0, 0.02)
        
        current['timestamp'] = datetime.now().isoformat()
        
        return current.copy()
    
    def get_all_current_data(self):
        """Get current data for all zones"""
        return [self.current_data[zone].copy() for zone in self.zones]
    
    def simulate_event(self, zone_id, event_type='high_risk'):
        """Simulate a specific event in a zone"""
        if event_type == 'high_risk':
            self.current_data[zone_id]['displacement_mm'] += np.random.uniform(2, 5)
            self.current_data[zone_id]['vibration_mm_s'] += np.random.uniform(0.5, 1.5)
        elif event_type == 'critical_risk':
            self.current_data[zone_id]['displacement_mm'] += np.random.uniform(5, 10)
            self.current_data[zone_id]['vibration_mm_s'] += np.random.uniform(1.5, 3)
        elif event_type == 'equipment_vibration':
            self.current_data[zone_id]['vibration_mm_s'] += np.random.uniform(1, 2)
        
        self.current_data[zone_id]['timestamp'] = datetime.now().isoformat()

class MQTTClient:
    """MQTT client for real-time data streaming"""
    
    def __init__(self, broker_host='localhost', broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client()
        self.connected = False
        
        # Setup callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info("Connected to MQTT broker")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        logger.info("Disconnected from MQTT broker")
    
    def on_publish(self, client, userdata, mid):
        logger.debug(f"Message published: {mid}")
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            time.sleep(1)  # Give time for connection
            return self.connected
        except Exception as e:
            logger.error(f"Error connecting to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
    
    def publish_sensor_data(self, zone_id, sensor_data):
        """Publish sensor data to MQTT topic"""
        if not self.connected:
            logger.warning("Not connected to MQTT broker")
            return False
        
        topic = f"rockfall/sensors/{zone_id}"
        payload = json.dumps(sensor_data)
        
        try:
            result = self.client.publish(topic, payload)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            logger.error(f"Error publishing to MQTT: {e}")
            return False

class DataIngestionService:
    """Main service for data ingestion and streaming"""
    
    def __init__(self, api_url='http://localhost:5000', use_mqtt=False):
        self.api_url = api_url
        self.simulator = SensorDataSimulator()
        self.mqtt_client = None
        self.running = False
        self.update_interval = 15  # seconds
        
        if use_mqtt:
            self.mqtt_client = MQTTClient()
            if not self.mqtt_client.connect():
                logger.warning("MQTT not available, using API only")
                self.mqtt_client = None
    
    def start_simulation(self, duration_minutes=None):
        """Start the data simulation"""
        self.running = True
        start_time = datetime.now()
        
        logger.info("Starting data simulation...")
        
        while self.running:
            try:
                # Update sensor data for all zones
                for zone in self.simulator.zones:
                    # Add some variability - occasionally simulate events
                    if np.random.random() < 0.05:  # 5% chance of event
                        event_type = np.random.choice(['high_risk', 'equipment_vibration'])
                        self.simulator.simulate_event(zone, event_type)
                    else:
                        self.simulator.update_sensor_data(zone)
                
                # Get current data
                current_data = self.simulator.get_all_current_data()
                
                # Send to API and MQTT
                for data in current_data:
                    self.send_data(data)
                
                logger.info(f"Sent data for {len(current_data)} zones")
                
                # Check if duration is exceeded
                if duration_minutes:
                    elapsed = (datetime.now() - start_time).total_seconds() / 60
                    if elapsed >= duration_minutes:
                        break
                
                time.sleep(self.update_interval)
                
            except KeyboardInterrupt:
                logger.info("Simulation interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in simulation: {e}")
                time.sleep(5)  # Wait before retrying
        
        self.stop_simulation()
    
    def stop_simulation(self):
        """Stop the data simulation"""
        self.running = False
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        logger.info("Data simulation stopped")
    
    def send_data(self, sensor_data):
        """Send sensor data to API and MQTT"""
        # Send to REST API
        try:
            response = requests.post(f"{self.api_url}/predict", json=sensor_data, timeout=5)
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"API response for zone {sensor_data['zone_id']}: "
                           f"Risk={result['prediction']['risk_level']}")
            else:
                logger.warning(f"API request failed: {response.status_code}")
        except Exception as e:
            logger.debug(f"API request failed: {e}")
        
        # Send to MQTT
        if self.mqtt_client:
            self.mqtt_client.publish_sensor_data(sensor_data['zone_id'], sensor_data)
    
    def load_historical_data(self, csv_file=None):
        """Load and replay historical sensor data"""
        if csv_file is None:
            csv_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  'sample-data', 'demo_sensor.csv')
        
        try:
            df = pd.read_csv(csv_file)
            logger.info(f"Loaded {len(df)} historical records")
            
            # Group by timestamp and send in batches
            for timestamp, group in df.groupby('timestamp'):
                logger.info(f"Sending data for timestamp: {timestamp}")
                
                for _, row in group.iterrows():
                    sensor_data = row.to_dict()
                    self.send_data(sensor_data)
                
                time.sleep(2)  # Small delay between timestamps
                
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")

def main():
    """Main function for testing data ingestion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rockfall Data Ingestion Service')
    parser.add_argument('--mode', choices=['simulate', 'historical'], 
                       default='simulate', help='Data ingestion mode')
    parser.add_argument('--duration', type=int, default=None,
                       help='Simulation duration in minutes')
    parser.add_argument('--mqtt', action='store_true',
                       help='Enable MQTT publishing')
    parser.add_argument('--api-url', default='http://localhost:5000',
                       help='API base URL')
    
    args = parser.parse_args()
    
    # Create service
    service = DataIngestionService(api_url=args.api_url, use_mqtt=args.mqtt)
    
    try:
        if args.mode == 'simulate':
            service.start_simulation(duration_minutes=args.duration)
        elif args.mode == 'historical':
            service.load_historical_data()
    except KeyboardInterrupt:
        logger.info("Service interrupted")
    finally:
        service.stop_simulation()

if __name__ == "__main__":
    main()