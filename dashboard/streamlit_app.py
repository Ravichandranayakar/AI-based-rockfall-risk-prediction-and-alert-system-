"""
Streamlit Dashboard for Rockfall Risk Prediction System
Interactive web interface for monitoring mine safety
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import requests
import json
import time
from datetime import datetime, timedelta
import os
import logging

# Configure page
st.set_page_config(
    page_title="Rockfall Risk Monitoring System",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import dashboard utilities
from dashboard_utils import (
    load_zones_data, load_sensor_data, load_alerts_data,
    create_mine_map, create_risk_gauge, format_alert_message,
    get_risk_color, calculate_zone_status
)

# Constants
API_BASE_URL = "http://localhost:5000"
REFRESH_INTERVAL = 15  # seconds

def main():
    """Main dashboard application"""
    
    # Title and header
    st.title("🏔️ Rockfall Risk Monitoring System")
    st.markdown("**Mountain View Open Pit Mine - Real-time Safety Dashboard**")
    
    # Initialize session state
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    if 'alerts_shown' not in st.session_state:
        st.session_state.alerts_shown = set()
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = True
    
    # Sidebar controls
    st.sidebar.header("⚙️ Controls")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto Refresh", value=st.session_state.auto_refresh)
    st.session_state.auto_refresh = auto_refresh
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Now"):
        st.session_state.last_refresh = datetime.now()
        st.rerun()
    
    # Settings
    st.sidebar.header("📊 Display Settings")
    show_detailed_metrics = st.sidebar.checkbox("Show Detailed Metrics", value=True)
    show_historical_data = st.sidebar.checkbox("Show Historical Trends", value=True)
    alert_threshold = st.sidebar.slider("Alert Threshold", 1.0, 10.0, 6.0, 0.5)
    
    # Emergency contacts
    st.sidebar.header("🚨 Emergency Contacts")
    st.sidebar.markdown("""
    **Site Manager:** +1-555-0101  
    **Safety Officer:** +1-555-0102  
    **Emergency:** 911
    """)
    
    try:
        # Load data
        zones_data = load_zones_data()
        sensor_data = load_sensor_data()
        alerts_data = load_alerts_data()
        
        # Get current risk predictions
        current_risks = get_current_risk_predictions(sensor_data)
        
        # Check for new alerts
        check_for_alerts(current_risks, alert_threshold)
        
        # Main content area
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.header("🗺️ Mine Overview Map")
            mine_map = create_mine_map(zones_data, current_risks)
            st.plotly_chart(mine_map, use_container_width=True)
        
        with col2:
            st.header("⚠️ Risk Status")
            display_risk_status(current_risks)
        
        with col3:
            st.header("📈 Live Metrics")
            display_live_metrics(current_risks)
        
        # Detailed zone information
        st.header("🎯 Zone Details")
        display_zone_details(zones_data, current_risks, show_detailed_metrics)
        
        if show_historical_data:
            st.header("📊 Historical Trends")
            display_historical_trends(sensor_data)
        
        # Alerts section
        st.header("🚨 Recent Alerts")
        display_alerts_panel(alerts_data)
        
        # System status
        display_system_status()
        
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")
        logger.error(f"Dashboard error: {e}")
    
    # Auto-refresh logic
    if auto_refresh:
        time_since_refresh = (datetime.now() - st.session_state.last_refresh).seconds
        if time_since_refresh >= REFRESH_INTERVAL:
            st.session_state.last_refresh = datetime.now()
            st.rerun()
        
        # Show countdown
        remaining = REFRESH_INTERVAL - time_since_refresh
        st.sidebar.write(f"⏱️ Next refresh in: {remaining}s")

def get_current_risk_predictions(sensor_data):
    """Get current risk predictions for all zones"""
    try:
        # Get latest data for each zone
        latest_data = sensor_data.groupby('zone_id').last().reset_index()
        
        predictions = {}
        for _, row in latest_data.iterrows():
            try:
                # Prepare data for API
                api_data = {
                    'zone_id': row['zone_id'],
                    'displacement_mm': float(row['displacement_mm']),
                    'vibration_mm_s': float(row['vibration_mm_s']),
                    'temperature_c': float(row.get('temperature_c', 22.0)),
                    'humidity_percent': float(row.get('humidity_percent', 60.0)),
                    'pressure_kpa': float(row.get('pressure_kpa', 101.3)),
                    'accelerometer_x': float(row.get('accelerometer_x', 0.1)),
                    'accelerometer_y': float(row.get('accelerometer_y', 0.1)),
                    'accelerometer_z': float(row.get('accelerometer_z', 9.8))
                }
                
                # Call API
                response = requests.post(f"{API_BASE_URL}/predict", 
                                       json=api_data, timeout=5)
                
                if response.status_code == 200:
                    result = response.json()
                    predictions[row['zone_id']] = {
                        'sensor_data': api_data,
                        'prediction': result['prediction'],
                        'recommendation': result['recommendation'],
                        'timestamp': result['timestamp']
                    }
                else:
                    # Fallback prediction
                    predictions[row['zone_id']] = create_fallback_prediction(api_data)
                    
            except Exception as e:
                logger.warning(f"Error getting prediction for zone {row['zone_id']}: {e}")
                predictions[row['zone_id']] = create_fallback_prediction(row.to_dict())
        
        return predictions
        
    except Exception as e:
        logger.error(f"Error getting risk predictions: {e}")
        return {}

def create_fallback_prediction(sensor_data):
    """Create fallback prediction when API is unavailable"""
    displacement = sensor_data.get('displacement_mm', 0)
    vibration = sensor_data.get('vibration_mm_s', 0)
    
    # Simple rule-based prediction
    if displacement > 8 or vibration > 2.5:
        risk_level = 'critical'
        risk_score = 8.5
        color = 'red'
        action = 'IMMEDIATE_EVACUATION'
    elif displacement > 5 or vibration > 1.5:
        risk_level = 'high'
        risk_score = 6.5
        color = 'orange'
        action = 'INCREASED_MONITORING'
    else:
        risk_level = 'low'
        risk_score = 3.0
        color = 'green'
        action = 'NORMAL_OPERATIONS'
    
    return {
        'sensor_data': sensor_data,
        'prediction': {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_probabilities': {risk_level: 0.8}
        },
        'recommendation': {
            'action': action,
            'color': color,
            'message': f'{risk_level.title()} risk detected'
        },
        'timestamp': datetime.now().isoformat()
    }

def check_for_alerts(current_risks, threshold):
    """Check for new alerts and display notifications"""
    for zone_id, risk_data in current_risks.items():
        risk_score = risk_data['prediction']['risk_score']
        risk_level = risk_data['prediction']['risk_level']
        
        alert_key = f"{zone_id}_{risk_level}_{int(risk_score)}"
        
        if (risk_score >= threshold and 
            alert_key not in st.session_state.alerts_shown):
            
            # Show alert
            if risk_level == 'critical':
                st.error(f"🚨 CRITICAL ALERT - Zone {zone_id}: {risk_data['recommendation']['message']}")
            elif risk_level == 'high':
                st.warning(f"⚠️ WARNING - Zone {zone_id}: {risk_data['recommendation']['message']}")
            
            # Mark as shown
            st.session_state.alerts_shown.add(alert_key)
            
            # Auto-clear old alerts
            if len(st.session_state.alerts_shown) > 10:
                st.session_state.alerts_shown.clear()

def display_risk_status(current_risks):
    """Display overall risk status"""
    if not current_risks:
        st.warning("No data available")
        return
    
    # Calculate overall status
    risk_scores = [r['prediction']['risk_score'] for r in current_risks.values()]
    critical_zones = sum(1 for r in current_risks.values() 
                        if r['prediction']['risk_level'] == 'critical')
    warning_zones = sum(1 for r in current_risks.values() 
                       if r['prediction']['risk_level'] == 'high')
    
    # Overall status indicator
    max_risk = max(risk_scores) if risk_scores else 0
    avg_risk = np.mean(risk_scores) if risk_scores else 0
    
    # Status gauge
    fig = create_risk_gauge(max_risk, "Overall Risk")
    st.plotly_chart(fig, use_container_width=True)
    
    # Status metrics
    st.metric("Average Risk", f"{avg_risk:.1f}/10")
    st.metric("Critical Zones", critical_zones)
    st.metric("Warning Zones", warning_zones)
    
    # Status color
    if critical_zones > 0:
        st.error("🚨 CRITICAL STATUS")
    elif warning_zones > 0:
        st.warning("⚠️ WARNING STATUS")
    else:
        st.success("✅ NORMAL STATUS")

def display_live_metrics(current_risks):
    """Display live sensor metrics"""
    if not current_risks:
        return
    
    # Latest displacement and vibration readings
    displacements = []
    vibrations = []
    
    for zone_id, risk_data in current_risks.items():
        sensor_data = risk_data['sensor_data']
        displacements.append(sensor_data['displacement_mm'])
        vibrations.append(sensor_data['vibration_mm_s'])
    
    # Metrics
    st.metric("Max Displacement", f"{max(displacements):.1f} mm")
    st.metric("Max Vibration", f"{max(vibrations):.1f} mm/s")
    st.metric("Active Sensors", len(current_risks))
    
    # Mini charts
    st.subheader("Live Readings")
    
    # Displacement bar chart
    zones = list(current_risks.keys())
    fig_disp = px.bar(
        x=zones, y=displacements,
        title="Displacement (mm)",
        color=displacements,
        color_continuous_scale="Reds"
    )
    fig_disp.update_layout(height=200, showlegend=False)
    st.plotly_chart(fig_disp, use_container_width=True)
    
    # Vibration bar chart
    fig_vib = px.bar(
        x=zones, y=vibrations,
        title="Vibration (mm/s)",
        color=vibrations,
        color_continuous_scale="Oranges"
    )
    fig_vib.update_layout(height=200, showlegend=False)
    st.plotly_chart(fig_vib, use_container_width=True)

def display_zone_details(zones_data, current_risks, show_detailed=True):
    """Display detailed information for each zone"""
    if not zones_data or not current_risks:
        return
    
    # Zone selection tabs
    zone_tabs = st.tabs([f"Zone {zone['zone_id']}" for zone in zones_data['zones']])
    
    for i, zone in enumerate(zones_data['zones']):
        zone_id = zone['zone_id']
        
        with zone_tabs[i]:
            if zone_id in current_risks:
                risk_data = current_risks[zone_id]
                sensor_data = risk_data['sensor_data']
                prediction = risk_data['prediction']
                recommendation = risk_data['recommendation']
                
                # Zone header
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.subheader(f"{zone['zone_name']}")
                    st.write(f"**Rock Type:** {zone['characteristics']['rock_type'].title()}")
                    st.write(f"**Slope Angle:** {zone['characteristics']['slope_angle']}°")
                    st.write(f"**Height:** {zone['characteristics']['height_m']}m")
                
                with col2:
                    # Risk gauge
                    gauge_fig = create_risk_gauge(prediction['risk_score'], f"Zone {zone_id}")
                    st.plotly_chart(gauge_fig, use_container_width=True)
                
                with col3:
                    # Current status
                    risk_color = get_risk_color(prediction['risk_level'])
                    st.markdown(f"### Status: <span style='color: {risk_color}'>{prediction['risk_level'].upper()}</span>", 
                              unsafe_allow_html=True)
                    st.write(f"**Action:** {recommendation['action'].replace('_', ' ')}")
                
                if show_detailed:
                    # Detailed metrics
                    st.subheader("📊 Current Sensor Readings")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Displacement", f"{sensor_data['displacement_mm']:.1f} mm")
                        st.metric("Temperature", f"{sensor_data['temperature_c']:.1f}°C")
                    with col2:
                        st.metric("Vibration", f"{sensor_data['vibration_mm_s']:.1f} mm/s")
                        st.metric("Humidity", f"{sensor_data['humidity_percent']:.1f}%")
                    with col3:
                        st.metric("Accel-X", f"{sensor_data['accelerometer_x']:.2f} m/s²")
                        st.metric("Pressure", f"{sensor_data['pressure_kpa']:.1f} kPa")
                    with col4:
                        st.metric("Accel-Y", f"{sensor_data['accelerometer_y']:.2f} m/s²")
                        st.metric("Accel-Z", f"{sensor_data['accelerometer_z']:.2f} m/s²")
                    
                    # Risk probabilities
                    st.subheader("🎯 Risk Analysis")
                    prob_data = prediction['risk_probabilities']
                    
                    fig_prob = px.bar(
                        x=list(prob_data.keys()),
                        y=list(prob_data.values()),
                        title="Risk Probability Distribution",
                        color=list(prob_data.values()),
                        color_continuous_scale="RdYlGn_r"
                    )
                    st.plotly_chart(fig_prob, use_container_width=True)
                
                # Recommendation panel
                st.subheader("💡 Recommendations")
                st.info(f"**{recommendation['message']}**")
                
            else:
                st.warning(f"No current data available for Zone {zone_id}")

def display_historical_trends(sensor_data):
    """Display historical sensor trends"""
    if sensor_data.empty:
        st.warning("No historical data available")
        return
    
    # Convert timestamp to datetime
    sensor_data['timestamp'] = pd.to_datetime(sensor_data['timestamp'])
    
    # Time range selector
    col1, col2 = st.columns(2)
    with col1:
        time_range = st.selectbox("Time Range", 
                                 ["Last Hour", "Last 6 Hours", "Last Day", "All Data"])
    with col2:
        selected_zones = st.multiselect("Select Zones", 
                                       sensor_data['zone_id'].unique(),
                                       default=sensor_data['zone_id'].unique())
    
    # Filter data
    now = datetime.now()
    if time_range == "Last Hour":
        start_time = now - timedelta(hours=1)
    elif time_range == "Last 6 Hours":
        start_time = now - timedelta(hours=6)
    elif time_range == "Last Day":
        start_time = now - timedelta(days=1)
    else:
        start_time = sensor_data['timestamp'].min()
    
    filtered_data = sensor_data[
        (sensor_data['timestamp'] >= start_time) &
        (sensor_data['zone_id'].isin(selected_zones))
    ]
    
    if filtered_data.empty:
        st.warning("No data available for selected filters")
        return
    
    # Trend charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Displacement trend
        fig_disp = px.line(
            filtered_data, x='timestamp', y='displacement_mm',
            color='zone_id', title="Displacement Trends",
            labels={'displacement_mm': 'Displacement (mm)'}
        )
        fig_disp.update_layout(height=400)
        st.plotly_chart(fig_disp, use_container_width=True)
    
    with col2:
        # Vibration trend
        fig_vib = px.line(
            filtered_data, x='timestamp', y='vibration_mm_s',
            color='zone_id', title="Vibration Trends",
            labels={'vibration_mm_s': 'Vibration (mm/s)'}
        )
        fig_vib.update_layout(height=400)
        st.plotly_chart(fig_vib, use_container_width=True)
    
    # Summary statistics
    st.subheader("📈 Summary Statistics")
    summary_stats = filtered_data.groupby('zone_id').agg({
        'displacement_mm': ['mean', 'max', 'std'],
        'vibration_mm_s': ['mean', 'max', 'std']
    }).round(2)
    
    st.dataframe(summary_stats, use_container_width=True)

def display_alerts_panel(alerts_data):
    """Display recent alerts"""
    if alerts_data.empty:
        st.info("No recent alerts")
        return
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Status", ["All", "ACTIVE", "RESOLVED"])
    with col2:
        level_filter = st.selectbox("Level", ["All", "CRITICAL", "WARNING", "INFO"])
    with col3:
        zone_filter = st.selectbox("Zone", ["All"] + list(alerts_data['zone_id'].unique()))
    
    # Apply filters
    filtered_alerts = alerts_data.copy()
    if status_filter != "All":
        filtered_alerts = filtered_alerts[filtered_alerts['status'] == status_filter]
    if level_filter != "All":
        filtered_alerts = filtered_alerts[filtered_alerts['alert_level'] == level_filter]
    if zone_filter != "All":
        filtered_alerts = filtered_alerts[filtered_alerts['zone_id'] == zone_filter]
    
    # Sort by timestamp (newest first)
    filtered_alerts = filtered_alerts.sort_values('timestamp', ascending=False)
    
    # Display alerts
    for _, alert in filtered_alerts.head(10).iterrows():
        alert_message = format_alert_message(alert)
        
        # Color based on level
        if alert['alert_level'] == 'CRITICAL':
            st.error(alert_message)
        elif alert['alert_level'] == 'WARNING':
            st.warning(alert_message)
        else:
            st.info(alert_message)
    
    # Alert summary
    st.subheader("📊 Alert Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        active_alerts = len(alerts_data[alerts_data['status'] == 'ACTIVE'])
        st.metric("Active Alerts", active_alerts)
    
    with col2:
        critical_alerts = len(alerts_data[alerts_data['alert_level'] == 'CRITICAL'])
        st.metric("Critical Alerts (24h)", critical_alerts)
    
    with col3:
        total_alerts = len(alerts_data)
        st.metric("Total Alerts", total_alerts)

def display_system_status():
    """Display system status information"""
    st.header("🔧 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # API Status
        try:
            response = requests.get(f"{API_BASE_URL}/", timeout=5)
            if response.status_code == 200:
                st.success("✅ API Server: Online")
            else:
                st.error("❌ API Server: Error")
        except:
            st.error("❌ API Server: Offline")
    
    with col2:
        # Data freshness
        last_update = st.session_state.last_refresh
        st.info(f"🕒 Last Update: {last_update.strftime('%H:%M:%S')}")
    
    with col3:
        # Auto-refresh status
        if st.session_state.auto_refresh:
            st.success("🔄 Auto-refresh: Enabled")
        else:
            st.warning("⏸️ Auto-refresh: Disabled")

if __name__ == "__main__":
    main()