"""
MQTT Integration for Real-time Data Streaming
Enhanced version with dashboard integration
"""

import paho.mqtt.client as mqtt
import json
import time
import threading
from datetime import datetime
import logging
import queue
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MQTTStreamingClient:
    """Enhanced MQTT client with dashboard integration"""
    
    def __init__(self, broker_host='localhost', broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client()
        self.connected = False
        self.subscribed_topics = set()
        
        # Data queues for real-time streaming
        self.sensor_data_queue = queue.Queue(maxsize=1000)
        self.alert_queue = queue.Queue(maxsize=100)
        
        # Callbacks
        self.data_callbacks = []
        self.alert_callbacks = []
        
        # Setup MQTT callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        
        # Background thread for processing
        self.processing_thread = None
        self.running = False
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback for MQTT connection"""
        if rc == 0:
            self.connected = True
            logger.info(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            
            # Subscribe to default topics
            self.subscribe_to_sensor_topics()
            self.subscribe_to_alert_topics()
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for MQTT disconnection"""
        self.connected = False
        logger.info("Disconnected from MQTT broker")
    
    def on_message(self, client, userdata, msg):
        """Callback for receiving MQTT messages"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode('utf-8'))
            
            # Add timestamp if not present
            if 'timestamp' not in payload:
                payload['timestamp'] = datetime.now().isoformat()
            
            # Route message based on topic
            if 'sensors' in topic:
                self.handle_sensor_data(topic, payload)
            elif 'alerts' in topic:
                self.handle_alert_data(topic, payload)
            else:
                logger.debug(f"Unhandled topic: {topic}")
                
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def on_subscribe(self, client, userdata, mid, granted_qos):
        """Callback for successful subscription"""
        logger.debug(f"Subscribed to topic with QoS {granted_qos}")
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            # Wait for connection
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < 10:
                time.sleep(0.1)
            
            if self.connected:
                # Start background processing
                self.running = True
                self.processing_thread = threading.Thread(target=self.process_data_queue)
                self.processing_thread.daemon = True
                self.processing_thread.start()
            
            return self.connected
            
        except Exception as e:
            logger.error(f"Error connecting to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        
        self.client.loop_stop()
        self.client.disconnect()
    
    def subscribe_to_sensor_topics(self):
        """Subscribe to sensor data topics"""
        sensor_topics = [
            "rockfall/sensors/+",  # All sensor data
            "rockfall/sensors/A",  # Zone A
            "rockfall/sensors/B",  # Zone B
            "rockfall/sensors/C",  # Zone C
            "rockfall/sensors/D"   # Zone D
        ]
        
        for topic in sensor_topics:
            try:
                self.client.subscribe(topic, qos=1)
                self.subscribed_topics.add(topic)
                logger.debug(f"Subscribed to sensor topic: {topic}")
            except Exception as e:
                logger.error(f"Error subscribing to {topic}: {e}")
    
    def subscribe_to_alert_topics(self):
        """Subscribe to alert topics"""
        alert_topics = [
            "rockfall/alerts/+",     # All alerts
            "rockfall/alerts/new",   # New alerts
            "rockfall/alerts/resolved"  # Resolved alerts
        ]
        
        for topic in alert_topics:
            try:
                self.client.subscribe(topic, qos=2)  # Higher QoS for alerts
                self.subscribed_topics.add(topic)
                logger.debug(f"Subscribed to alert topic: {topic}")
            except Exception as e:
                logger.error(f"Error subscribing to {topic}: {e}")
    
    def handle_sensor_data(self, topic, data):
        """Handle incoming sensor data"""
        try:
            # Extract zone ID from topic
            zone_id = topic.split('/')[-1] if '/' in topic else 'unknown'
            data['zone_id'] = zone_id
            
            # Add to queue
            if not self.sensor_data_queue.full():
                self.sensor_data_queue.put(data)
            else:
                # Remove oldest data if queue is full
                try:
                    self.sensor_data_queue.get_nowait()
                    self.sensor_data_queue.put(data)
                except queue.Empty:
                    pass
            
            # Trigger callbacks
            for callback in self.data_callbacks:
                try:
                    callback(zone_id, data)
                except Exception as e:
                    logger.error(f"Error in data callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling sensor data: {e}")
    
    def handle_alert_data(self, topic, data):
        """Handle incoming alert data"""
        try:
            # Add to queue
            if not self.alert_queue.full():
                self.alert_queue.put(data)
            
            # Trigger callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling alert data: {e}")
    
    def process_data_queue(self):
        """Background thread to process data queues"""
        while self.running:
            try:
                # Process sensor data
                while not self.sensor_data_queue.empty():
                    data = self.sensor_data_queue.get_nowait()
                    self.process_sensor_data(data)
                
                # Process alerts
                while not self.alert_queue.empty():
                    alert = self.alert_queue.get_nowait()
                    self.process_alert_data(alert)
                
                time.sleep(0.1)  # Small delay to prevent CPU spinning
                
            except Exception as e:
                logger.error(f"Error in data processing thread: {e}")
                time.sleep(1)
    
    def process_sensor_data(self, data):
        """Process sensor data (override in subclass if needed)"""
        logger.debug(f"Processing sensor data for zone {data.get('zone_id')}")
    
    def process_alert_data(self, alert):
        """Process alert data (override in subclass if needed)"""
        logger.info(f"Processing alert: {alert.get('alert_level', 'UNKNOWN')}")
    
    def publish_sensor_data(self, zone_id, sensor_data):
        """Publish sensor data to MQTT"""
        if not self.connected:
            return False
        
        topic = f"rockfall/sensors/{zone_id}"
        payload = json.dumps(sensor_data)
        
        try:
            result = self.client.publish(topic, payload, qos=1)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            logger.error(f"Error publishing sensor data: {e}")
            return False
    
    def publish_alert(self, alert_data):
        """Publish alert to MQTT"""
        if not self.connected:
            return False
        
        topic = f"rockfall/alerts/{alert_data.get('status', 'new').lower()}"
        payload = json.dumps(alert_data)
        
        try:
            result = self.client.publish(topic, payload, qos=2)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            logger.error(f"Error publishing alert: {e}")
            return False
    
    def add_data_callback(self, callback):
        """Add callback for sensor data"""
        self.data_callbacks.append(callback)
    
    def add_alert_callback(self, callback):
        """Add callback for alerts"""
        self.alert_callbacks.append(callback)
    
    def get_latest_sensor_data(self, max_items=10):
        """Get latest sensor data from queue"""
        data = []
        count = 0
        
        while count < max_items and not self.sensor_data_queue.empty():
            try:
                item = self.sensor_data_queue.get_nowait()
                data.append(item)
                count += 1
            except queue.Empty:
                break
        
        return data
    
    def get_latest_alerts(self, max_items=5):
        """Get latest alerts from queue"""
        alerts = []
        count = 0
        
        while count < max_items and not self.alert_queue.empty():
            try:
                alert = self.alert_queue.get_nowait()
                alerts.append(alert)
                count += 1
            except queue.Empty:
                break
        
        return alerts

class StreamlitMQTTIntegration:
    """Integration class for Streamlit dashboard with MQTT"""
    
    def __init__(self):
        self.mqtt_client = None
        self.is_connected = False
        
        # Initialize session state for MQTT data
        if 'mqtt_sensor_data' not in st.session_state:
            st.session_state.mqtt_sensor_data = []
        if 'mqtt_alerts' not in st.session_state:
            st.session_state.mqtt_alerts = []
        if 'mqtt_connection_status' not in st.session_state:
            st.session_state.mqtt_connection_status = "Disconnected"
    
    def connect_mqtt(self, broker_host='localhost', broker_port=1883):
        """Connect to MQTT broker"""
        try:
            self.mqtt_client = MQTTStreamingClient(broker_host, broker_port)
            
            # Add callbacks for Streamlit integration
            self.mqtt_client.add_data_callback(self.on_sensor_data)
            self.mqtt_client.add_alert_callback(self.on_alert_data)
            
            # Connect
            self.is_connected = self.mqtt_client.connect()
            
            if self.is_connected:
                st.session_state.mqtt_connection_status = "Connected"
                logger.info("MQTT integration connected successfully")
            else:
                st.session_state.mqtt_connection_status = "Connection Failed"
                logger.error("Failed to connect MQTT integration")
            
            return self.is_connected
            
        except Exception as e:
            logger.error(f"Error in MQTT integration: {e}")
            st.session_state.mqtt_connection_status = f"Error: {str(e)}"
            return False
    
    def disconnect_mqtt(self):
        """Disconnect from MQTT broker"""
        if self.mqtt_client:
            self.mqtt_client.disconnect()
            self.is_connected = False
            st.session_state.mqtt_connection_status = "Disconnected"
    
    def on_sensor_data(self, zone_id, data):
        """Callback for new sensor data"""
        # Add to session state
        st.session_state.mqtt_sensor_data.append({
            'zone_id': zone_id,
            'data': data,
            'received_at': datetime.now().isoformat()
        })
        
        # Keep only last 100 entries
        if len(st.session_state.mqtt_sensor_data) > 100:
            st.session_state.mqtt_sensor_data = st.session_state.mqtt_sensor_data[-100:]
    
    def on_alert_data(self, alert):
        """Callback for new alerts"""
        # Add to session state
        st.session_state.mqtt_alerts.append({
            'alert': alert,
            'received_at': datetime.now().isoformat()
        })
        
        # Keep only last 50 alerts
        if len(st.session_state.mqtt_alerts) > 50:
            st.session_state.mqtt_alerts = st.session_state.mqtt_alerts[-50:]
        
        # Show notification in Streamlit
        if alert.get('alert_level') == 'CRITICAL':
            st.error(f"🚨 MQTT ALERT: Critical situation in Zone {alert.get('zone_id')}")
        elif alert.get('alert_level') == 'WARNING':
            st.warning(f"⚠️ MQTT ALERT: Warning in Zone {alert.get('zone_id')}")
    
    def publish_prediction_result(self, zone_id, prediction_result):
        """Publish prediction result to MQTT"""
        if self.mqtt_client and self.is_connected:
            topic_data = {
                'zone_id': zone_id,
                'prediction': prediction_result,
                'timestamp': datetime.now().isoformat(),
                'source': 'dashboard'
            }
            
            self.mqtt_client.publish_sensor_data(f"{zone_id}/prediction", topic_data)
    
    def get_mqtt_status_widget(self):
        """Get MQTT status widget for dashboard"""
        status = st.session_state.mqtt_connection_status
        
        if status == "Connected":
            st.success(f"🔗 MQTT Status: {status}")
        elif status == "Disconnected":
            st.warning(f"🔌 MQTT Status: {status}")
        else:
            st.error(f"❌ MQTT Status: {status}")
        
        # Show data counts
        sensor_count = len(st.session_state.mqtt_sensor_data)
        alert_count = len(st.session_state.mqtt_alerts)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("MQTT Sensor Messages", sensor_count)
        with col2:
            st.metric("MQTT Alert Messages", alert_count)
    
    def get_latest_mqtt_data(self, zone_id=None, max_items=10):
        """Get latest MQTT sensor data"""
        data = st.session_state.mqtt_sensor_data
        
        if zone_id:
            data = [item for item in data if item['zone_id'] == zone_id]
        
        return data[-max_items:] if data else []
    
    def get_latest_mqtt_alerts(self, max_items=5):
        """Get latest MQTT alerts"""
        alerts = st.session_state.mqtt_alerts
        return alerts[-max_items:] if alerts else []

# Example usage for testing
def test_mqtt_integration():
    """Test MQTT integration"""
    mqtt_client = MQTTStreamingClient()
    
    def sensor_callback(zone_id, data):
        print(f"Received sensor data for zone {zone_id}: {data}")
    
    def alert_callback(alert):
        print(f"Received alert: {alert}")
    
    mqtt_client.add_data_callback(sensor_callback)
    mqtt_client.add_alert_callback(alert_callback)
    
    if mqtt_client.connect():
        print("Connected to MQTT broker")
        
        # Simulate some data
        test_data = {
            'displacement_mm': 5.2,
            'vibration_mm_s': 1.3,
            'temperature_c': 23.5,
            'timestamp': datetime.now().isoformat()
        }
        
        mqtt_client.publish_sensor_data('A', test_data)
        
        # Wait for a bit
        time.sleep(2)
        
        mqtt_client.disconnect()
    else:
        print("Failed to connect to MQTT broker")

if __name__ == "__main__":
    test_mqtt_integration()