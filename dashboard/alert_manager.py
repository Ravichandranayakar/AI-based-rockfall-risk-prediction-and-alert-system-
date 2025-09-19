"""
Alert Management System for Rockfall Risk Prediction
Handles alert generation, notification, and logging
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertManager:
    """Manages alert generation, tracking, and notifications"""
    
    def __init__(self, zones_file=None, alerts_file=None):
        # Load zone configuration
        if zones_file is None:
            zones_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    'sample-data', 'zones.json')
        
        with open(zones_file, 'r') as f:
            self.zones_data = json.load(f)
        
        # Alert storage
        if alerts_file is None:
            self.alerts_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                          'sample-data', 'fake_alerts.csv')
        else:
            self.alerts_file = alerts_file
        
        # Active alerts tracking
        self.active_alerts = {}
        self.alert_history = []
        
        # Load existing alerts
        self.load_existing_alerts()
        
        # Notification handlers
        self.notification_handlers = []
    
    def load_existing_alerts(self):
        """Load existing alerts from CSV file"""
        try:
            if os.path.exists(self.alerts_file):
                df = pd.read_csv(self.alerts_file)
                self.alert_history = df.to_dict('records')
                
                # Track active alerts
                active_df = df[df['status'] == 'ACTIVE']
                for _, row in active_df.iterrows():
                    self.active_alerts[row['alert_id']] = row.to_dict()
                
                logger.info(f"Loaded {len(self.alert_history)} alerts, "
                          f"{len(self.active_alerts)} active")
        except Exception as e:
            logger.error(f"Error loading existing alerts: {e}")
    
    def add_notification_handler(self, handler_func):
        """Add a notification handler function"""
        self.notification_handlers.append(handler_func)
    
    def check_alerts(self, current_risks: Dict) -> List[Dict]:
        """Check for new alerts based on current risk data"""
        new_alerts = []
        
        for zone_id, risk_data in current_risks.items():
            sensor_data = risk_data['sensor_data']
            prediction = risk_data['prediction']
            
            # Get zone thresholds
            zone_thresholds = self.get_zone_thresholds(zone_id)
            if not zone_thresholds:
                continue
            
            # Check for threshold violations
            alert_info = self.evaluate_thresholds(zone_id, sensor_data, 
                                                prediction, zone_thresholds)
            
            if alert_info:
                # Check if this is a new alert or escalation
                if self.should_create_alert(zone_id, alert_info):
                    alert = self.create_alert(zone_id, alert_info, sensor_data, prediction)
                    new_alerts.append(alert)
                    
                    # Send notifications
                    self.send_notifications(alert)
        
        return new_alerts
    
    def get_zone_thresholds(self, zone_id: str) -> Optional[Dict]:
        """Get thresholds for a specific zone"""
        for zone in self.zones_data['zones']:
            if zone['zone_id'] == zone_id:
                return zone['risk_thresholds']
        return None
    
    def evaluate_thresholds(self, zone_id: str, sensor_data: Dict, 
                          prediction: Dict, thresholds: Dict) -> Optional[Dict]:
        """Evaluate if sensor data violates thresholds"""
        displacement = sensor_data.get('displacement_mm', 0)
        vibration = sensor_data.get('vibration_mm_s', 0)
        risk_score = prediction.get('risk_score', 0)
        
        alert_level = None
        trigger_reasons = []
        
        # Check displacement thresholds
        if displacement >= thresholds.get('displacement_critical', float('inf')):
            alert_level = 'CRITICAL'
            trigger_reasons.append('critical_displacement')
        elif displacement >= thresholds.get('displacement_warning', float('inf')):
            if alert_level != 'CRITICAL':
                alert_level = 'WARNING'
            trigger_reasons.append('high_displacement')
        
        # Check vibration thresholds
        if vibration >= thresholds.get('vibration_critical', float('inf')):
            alert_level = 'CRITICAL'
            trigger_reasons.append('critical_vibration')
        elif vibration >= thresholds.get('vibration_warning', float('inf')):
            if alert_level != 'CRITICAL':
                alert_level = 'WARNING'
            trigger_reasons.append('high_vibration')
        
        # Check risk score threshold
        if risk_score >= 8.0:
            alert_level = 'CRITICAL'
            trigger_reasons.append('critical_risk_score')
        elif risk_score >= 6.0:
            if alert_level != 'CRITICAL':
                alert_level = 'WARNING'
            trigger_reasons.append('high_risk_score')
        
        # Check for multiple factors
        if len(trigger_reasons) > 1:
            trigger_reasons.append('multiple_factors')
        
        if alert_level:
            return {
                'alert_level': alert_level,
                'trigger_reasons': trigger_reasons,
                'risk_score': risk_score
            }
        
        return None
    
    def should_create_alert(self, zone_id: str, alert_info: Dict) -> bool:
        """Determine if a new alert should be created"""
        alert_level = alert_info['alert_level']
        
        # Check for existing active alerts in this zone
        for alert_id, alert in self.active_alerts.items():
            if alert['zone_id'] == zone_id:
                # If existing alert is same or higher level, don't create new one
                existing_level = alert['alert_level']
                if (existing_level == 'CRITICAL' or 
                    (existing_level == 'WARNING' and alert_level == 'WARNING')):
                    return False
                
                # If new alert is escalation, resolve old one and create new
                if (existing_level == 'WARNING' and alert_level == 'CRITICAL'):
                    self.resolve_alert(alert_id, "Escalated to critical")
                    return True
        
        return True
    
    def create_alert(self, zone_id: str, alert_info: Dict, 
                    sensor_data: Dict, prediction: Dict) -> Dict:
        """Create a new alert"""
        alert_id = f"ALT{len(self.alert_history) + 1:03d}"
        timestamp = datetime.now()
        
        # Get zone name
        zone_name = zone_id
        for zone in self.zones_data['zones']:
            if zone['zone_id'] == zone_id:
                zone_name = zone['zone_name']
                break
        
        # Determine recommended action
        recommended_action = self.get_recommended_action(alert_info['alert_level'], 
                                                       alert_info['trigger_reasons'])
        
        alert = {
            'alert_id': alert_id,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'zone_id': zone_id,
            'zone_name': zone_name,
            'alert_level': alert_info['alert_level'],
            'risk_score': alert_info['risk_score'],
            'trigger_reason': '_'.join(alert_info['trigger_reasons']),
            'recommended_action': recommended_action,
            'status': 'ACTIVE',
            'resolved_timestamp': '',
            'operator_notes': '',
            'displacement_mm': sensor_data.get('displacement_mm', 0),
            'vibration_mm_s': sensor_data.get('vibration_mm_s', 0),
            'temperature_c': sensor_data.get('temperature_c', 0),
            'humidity_percent': sensor_data.get('humidity_percent', 0)
        }
        
        # Add to active alerts and history
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Save to file
        self.save_alerts()
        
        logger.info(f"Created {alert_info['alert_level']} alert {alert_id} for zone {zone_id}")
        return alert
    
    def get_recommended_action(self, alert_level: str, trigger_reasons: List[str]) -> str:
        """Get recommended action based on alert level and triggers"""
        if alert_level == 'CRITICAL':
            if 'critical_displacement' in trigger_reasons:
                return 'immediate_evacuation_and_equipment_removal'
            elif 'critical_vibration' in trigger_reasons:
                return 'immediate_evacuation_required'
            elif 'multiple_factors' in trigger_reasons:
                return 'emergency_evacuation_protocol_activated'
            else:
                return 'immediate_evacuation_required'
        
        elif alert_level == 'WARNING':
            if 'high_displacement' in trigger_reasons:
                return 'monitor_closely_and_restrict_access'
            elif 'high_vibration' in trigger_reasons:
                return 'reduce_blast_intensity_in_adjacent_areas'
            else:
                return 'increase_monitoring_frequency'
        
        else:
            return 'routine_monitoring'
    
    def resolve_alert(self, alert_id: str, resolution_notes: str = ""):
        """Resolve an active alert"""
        if alert_id in self.active_alerts:
            # Update alert status
            self.active_alerts[alert_id]['status'] = 'RESOLVED'
            self.active_alerts[alert_id]['resolved_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.active_alerts[alert_id]['operator_notes'] = resolution_notes
            
            # Update in history
            for i, alert in enumerate(self.alert_history):
                if alert['alert_id'] == alert_id:
                    self.alert_history[i] = self.active_alerts[alert_id]
                    break
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            
            # Save changes
            self.save_alerts()
            
            logger.info(f"Resolved alert {alert_id}: {resolution_notes}")
        else:
            logger.warning(f"Alert {alert_id} not found in active alerts")
    
    def auto_resolve_alerts(self, current_risks: Dict):
        """Automatically resolve alerts when conditions improve"""
        resolved_count = 0
        
        for alert_id, alert in list(self.active_alerts.items()):
            zone_id = alert['zone_id']
            
            if zone_id not in current_risks:
                continue
            
            # Check if conditions have improved
            current_risk = current_risks[zone_id]
            current_level = current_risk['prediction']['risk_level']
            current_score = current_risk['prediction']['risk_score']
            
            should_resolve = False
            resolution_reason = ""
            
            # Auto-resolve if risk has significantly decreased
            if alert['alert_level'] == 'CRITICAL' and current_level == 'low':
                should_resolve = True
                resolution_reason = "Risk level decreased to low"
            elif alert['alert_level'] == 'WARNING' and current_level == 'low':
                should_resolve = True
                resolution_reason = "Risk level decreased to low"
            elif current_score < alert['risk_score'] * 0.7:  # 30% improvement
                should_resolve = True
                resolution_reason = f"Risk score improved from {alert['risk_score']:.1f} to {current_score:.1f}"
            
            if should_resolve:
                self.resolve_alert(alert_id, f"Auto-resolved: {resolution_reason}")
                resolved_count += 1
        
        if resolved_count > 0:
            logger.info(f"Auto-resolved {resolved_count} alerts")
        
        return resolved_count
    
    def send_notifications(self, alert: Dict):
        """Send notifications for new alert"""
        try:
            for handler in self.notification_handlers:
                handler(alert)
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
    
    def save_alerts(self):
        """Save alerts to CSV file"""
        try:
            df = pd.DataFrame(self.alert_history)
            df.to_csv(self.alerts_file, index=False)
        except Exception as e:
            logger.error(f"Error saving alerts: {e}")
    
    def get_alert_summary(self) -> Dict:
        """Get summary of alerts"""
        total_alerts = len(self.alert_history)
        active_alerts = len(self.active_alerts)
        
        # Count by level in last 24 hours
        last_24h = datetime.now() - timedelta(hours=24)
        recent_alerts = [
            alert for alert in self.alert_history
            if datetime.strptime(alert['timestamp'], '%Y-%m-%d %H:%M:%S') >= last_24h
        ]
        
        critical_24h = sum(1 for alert in recent_alerts if alert['alert_level'] == 'CRITICAL')
        warning_24h = sum(1 for alert in recent_alerts if alert['alert_level'] == 'WARNING')
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'critical_alerts_24h': critical_24h,
            'warning_alerts_24h': warning_24h,
            'recent_alerts_24h': len(recent_alerts)
        }
    
    def get_zone_alert_history(self, zone_id: str, days: int = 7) -> List[Dict]:
        """Get alert history for a specific zone"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        zone_alerts = []
        for alert in self.alert_history:
            if (alert['zone_id'] == zone_id and 
                datetime.strptime(alert['timestamp'], '%Y-%m-%d %H:%M:%S') >= cutoff_date):
                zone_alerts.append(alert)
        
        return sorted(zone_alerts, key=lambda x: x['timestamp'], reverse=True)

# Notification handlers
def email_notification_handler(alert: Dict):
    """Email notification handler (placeholder)"""
    logger.info(f"EMAIL ALERT: {alert['alert_level']} in Zone {alert['zone_id']}")
    # Here you would implement actual email sending

def sms_notification_handler(alert: Dict):
    """SMS notification handler (placeholder)"""
    message = f"ROCKFALL ALERT: {alert['alert_level']} risk in Zone {alert['zone_id']}. {alert['recommended_action'].replace('_', ' ').title()}."
    logger.info(f"SMS ALERT: {message}")
    # Here you would implement actual SMS sending

def dashboard_notification_handler(alert: Dict):
    """Dashboard notification handler"""
    logger.info(f"DASHBOARD ALERT: Broadcasting {alert['alert_level']} alert for Zone {alert['zone_id']}")
    # Here you would broadcast to dashboard websocket or similar

def emergency_notification_handler(alert: Dict):
    """Emergency services notification handler"""
    if alert['alert_level'] == 'CRITICAL':
        logger.warning(f"EMERGENCY ALERT: Critical situation in Zone {alert['zone_id']} - "
                      f"Contact emergency services if needed")
        # Here you would implement emergency services integration

# Example usage and testing
def test_alert_manager():
    """Test the alert manager functionality"""
    # Create alert manager
    alert_manager = AlertManager()
    
    # Add notification handlers
    alert_manager.add_notification_handler(email_notification_handler)
    alert_manager.add_notification_handler(sms_notification_handler)
    alert_manager.add_notification_handler(dashboard_notification_handler)
    alert_manager.add_notification_handler(emergency_notification_handler)
    
    # Test with sample risk data
    sample_risks = {
        'A': {
            'sensor_data': {
                'displacement_mm': 6.5,
                'vibration_mm_s': 1.8,
                'temperature_c': 23.0,
                'humidity_percent': 65.0
            },
            'prediction': {
                'risk_level': 'high',
                'risk_score': 7.2
            }
        },
        'D': {
            'sensor_data': {
                'displacement_mm': 12.0,
                'vibration_mm_s': 3.5,
                'temperature_c': 26.0,
                'humidity_percent': 50.0
            },
            'prediction': {
                'risk_level': 'critical',
                'risk_score': 9.1
            }
        }
    }
    
    # Check for alerts
    new_alerts = alert_manager.check_alerts(sample_risks)
    print(f"Generated {len(new_alerts)} new alerts")
    
    # Print alert summary
    summary = alert_manager.get_alert_summary()
    print(f"Alert summary: {summary}")
    
    return alert_manager

if __name__ == "__main__":
    test_alert_manager()