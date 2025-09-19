"""
Dashboard Utilities for Rockfall Risk Prediction System
Helper functions for data loading, visualization, and alert formatting
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_zones_data():
    """Load zone configuration data"""
    try:
        zones_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                 'sample-data', 'zones.json')
        with open(zones_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading zones data: {e}")
        return None

def load_sensor_data():
    """Load sensor data from CSV"""
    try:
        sensor_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  'sample-data', 'demo_sensor.csv')
        df = pd.read_csv(sensor_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        logger.error(f"Error loading sensor data: {e}")
        return pd.DataFrame()

def load_alerts_data():
    """Load alerts data from CSV"""
    try:
        alerts_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  'sample-data', 'fake_alerts.csv')
        df = pd.read_csv(alerts_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        logger.error(f"Error loading alerts data: {e}")
        return pd.DataFrame()

def create_mine_map(zones_data, current_risks):
    """Create interactive mine map with risk indicators"""
    if not zones_data:
        return go.Figure()
    
    fig = go.Figure()
    
    # Add zones to map
    for zone in zones_data['zones']:
        zone_id = zone['zone_id']
        coords = zone['coordinates']
        
        # Get risk level for coloring
        risk_level = 'low'
        risk_score = 0
        if zone_id in current_risks:
            risk_level = current_risks[zone_id]['prediction']['risk_level']
            risk_score = current_risks[zone_id]['prediction']['risk_score']
        
        # Color based on risk
        color = get_risk_color(risk_level)
        
        # Add zone marker
        fig.add_trace(go.Scattermapbox(
            lat=[coords['lat']],
            lon=[coords['lon']],
            mode='markers',
            marker=dict(
                size=20 + risk_score * 2,  # Size based on risk score
                color=color,
                opacity=0.8
            ),
            text=f"Zone {zone_id}: {zone['zone_name']}<br>"
                 f"Risk Level: {risk_level.upper()}<br>"
                 f"Risk Score: {risk_score:.1f}/10",
            hoverinfo='text',
            name=f"Zone {zone_id}"
        ))
        
        # Add zone boundary if available
        if 'geometry' in zone and zone['geometry']['type'] == 'polygon':
            boundary_coords = zone['geometry']['coordinates']
            lats = [coord[0] for coord in boundary_coords]
            lons = [coord[1] for coord in boundary_coords]
            
            fig.add_trace(go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode='lines',
                line=dict(width=2, color=color),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    # Update layout
    center_lat = np.mean([zone['coordinates']['lat'] for zone in zones_data['zones']])
    center_lon = np.mean([zone['coordinates']['lon'] for zone in zones_data['zones']])
    
    fig.update_layout(
        mapbox=dict(
            accesstoken='',  # Add your Mapbox token if needed
            style='open-street-map',
            center=dict(lat=center_lat, lon=center_lon),
            zoom=14
        ),
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True
    )
    
    return fig

def create_risk_gauge(risk_score, title="Risk Level"):
    """Create a risk gauge chart"""
    # Determine color based on risk score
    if risk_score >= 7:
        color = 'red'
    elif risk_score >= 4:
        color = 'orange'
    else:
        color = 'green'
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        delta={'reference': 5, 'increasing': {'color': "red"}},
        gauge={
            'axis': {'range': [None, 10]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 3], 'color': "lightgreen"},
                {'range': [3, 6], 'color': "yellow"},
                {'range': [6, 10], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 8
            }
        }
    ))
    
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def get_risk_color(risk_level):
    """Get color for risk level"""
    color_map = {
        'low': 'green',
        'normal': 'green',
        'high': 'orange',
        'warning': 'orange',
        'critical': 'red',
        'danger': 'red'
    }
    return color_map.get(risk_level.lower(), 'gray')

def format_alert_message(alert):
    """Format alert message for display"""
    timestamp = pd.to_datetime(alert['timestamp']).strftime('%Y-%m-%d %H:%M')
    
    message = f"**{alert['alert_level']}** - Zone {alert['zone_id']} ({alert['zone_name']})"
    message += f"\n\n📅 {timestamp}"
    message += f"\n\n📊 Risk Score: {alert['risk_score']:.1f}/10"
    message += f"\n\n⚠️ Trigger: {alert['trigger_reason'].replace('_', ' ').title()}"
    message += f"\n\n💡 Action: {alert['recommended_action'].replace('_', ' ').title()}"
    message += f"\n\n📝 Status: {alert['status']}"
    
    if alert['operator_notes'] and pd.notna(alert['operator_notes']):
        message += f"\n\n📋 Notes: {alert['operator_notes']}"
    
    return message

def calculate_zone_status(sensor_data, thresholds):
    """Calculate zone status based on sensor data and thresholds"""
    displacement = sensor_data.get('displacement_mm', 0)
    vibration = sensor_data.get('vibration_mm_s', 0)
    
    # Check thresholds
    displacement_status = 'normal'
    vibration_status = 'normal'
    
    if displacement >= thresholds.get('displacement_critical', float('inf')):
        displacement_status = 'critical'
    elif displacement >= thresholds.get('displacement_warning', float('inf')):
        displacement_status = 'warning'
    
    if vibration >= thresholds.get('vibration_critical', float('inf')):
        vibration_status = 'critical'
    elif vibration >= thresholds.get('vibration_warning', float('inf')):
        vibration_status = 'warning'
    
    # Overall status is the worst of the two
    if displacement_status == 'critical' or vibration_status == 'critical':
        return 'critical'
    elif displacement_status == 'warning' or vibration_status == 'warning':
        return 'warning'
    else:
        return 'normal'

def create_time_series_chart(data, x_col, y_col, color_col=None, title="Time Series"):
    """Create a time series chart"""
    if color_col:
        fig = px.line(data, x=x_col, y=y_col, color=color_col, title=title)
    else:
        fig = px.line(data, x=x_col, y=y_col, title=title)
    
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title=y_col.replace('_', ' ').title(),
        height=400
    )
    
    return fig

def create_correlation_heatmap(data, numerical_cols):
    """Create correlation heatmap"""
    if len(numerical_cols) < 2:
        return go.Figure()
    
    corr_matrix = data[numerical_cols].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=np.round(corr_matrix.values, 2),
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title="Sensor Data Correlation Matrix",
        height=400,
        margin=dict(l=80, r=20, t=60, b=80)
    )
    
    return fig

def create_distribution_plot(data, column, bins=20):
    """Create distribution plot for a column"""
    fig = px.histogram(
        data, x=column, nbins=bins,
        title=f"Distribution of {column.replace('_', ' ').title()}",
        marginal="box"
    )
    
    fig.update_layout(
        xaxis_title=column.replace('_', ' ').title(),
        yaxis_title="Frequency",
        height=400
    )
    
    return fig

def create_zone_comparison_chart(current_risks, metric='risk_score'):
    """Create comparison chart across zones"""
    if not current_risks:
        return go.Figure()
    
    zones = list(current_risks.keys())
    
    if metric == 'risk_score':
        values = [current_risks[zone]['prediction']['risk_score'] for zone in zones]
        title = "Risk Score Comparison"
        y_title = "Risk Score (0-10)"
    elif metric == 'displacement':
        values = [current_risks[zone]['sensor_data']['displacement_mm'] for zone in zones]
        title = "Displacement Comparison"
        y_title = "Displacement (mm)"
    elif metric == 'vibration':
        values = [current_risks[zone]['sensor_data']['vibration_mm_s'] for zone in zones]
        title = "Vibration Comparison"
        y_title = "Vibration (mm/s)"
    else:
        return go.Figure()
    
    # Color based on values
    colors = ['red' if v >= 7 else 'orange' if v >= 4 else 'green' for v in values]
    
    fig = go.Figure(data=go.Bar(
        x=zones,
        y=values,
        marker_color=colors,
        text=[f"{v:.1f}" for v in values],
        textposition='auto'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Zone",
        yaxis_title=y_title,
        height=300
    )
    
    return fig

def create_alert_timeline(alerts_data):
    """Create timeline of alerts"""
    if alerts_data.empty:
        return go.Figure()
    
    # Sort by timestamp
    alerts_data = alerts_data.sort_values('timestamp')
    
    # Create timeline
    fig = px.scatter(
        alerts_data, 
        x='timestamp', 
        y='zone_id',
        color='alert_level',
        size='risk_score',
        hover_data=['trigger_reason', 'recommended_action', 'status'],
        title="Alert Timeline"
    )
    
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Zone",
        height=400
    )
    
    return fig

def export_dashboard_data(current_risks, alerts_data, filename=None):
    """Export dashboard data to CSV"""
    if filename is None:
        filename = f"dashboard_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        # Prepare export data
        export_data = []
        
        for zone_id, risk_data in current_risks.items():
            sensor_data = risk_data['sensor_data']
            prediction = risk_data['prediction']
            
            export_data.append({
                'timestamp': datetime.now().isoformat(),
                'zone_id': zone_id,
                'displacement_mm': sensor_data['displacement_mm'],
                'vibration_mm_s': sensor_data['vibration_mm_s'],
                'temperature_c': sensor_data['temperature_c'],
                'risk_level': prediction['risk_level'],
                'risk_score': prediction['risk_score'],
                'recommended_action': risk_data['recommendation']['action']
            })
        
        # Convert to DataFrame and save
        df = pd.DataFrame(export_data)
        export_path = os.path.join(os.path.dirname(__file__), filename)
        df.to_csv(export_path, index=False)
        
        return export_path
        
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return None

def validate_sensor_data(sensor_data):
    """Validate sensor data for reasonable ranges"""
    issues = []
    
    # Check displacement range
    if sensor_data.get('displacement_mm', 0) > 50:
        issues.append("Displacement exceeds maximum expected range (50mm)")
    
    # Check vibration range
    if sensor_data.get('vibration_mm_s', 0) > 20:
        issues.append("Vibration exceeds maximum expected range (20 mm/s)")
    
    # Check temperature range
    temp = sensor_data.get('temperature_c', 20)
    if temp < -20 or temp > 60:
        issues.append("Temperature outside expected range (-20°C to 60°C)")
    
    # Check humidity range
    humidity = sensor_data.get('humidity_percent', 50)
    if humidity < 0 or humidity > 100:
        issues.append("Humidity outside valid range (0-100%)")
    
    # Check accelerometer readings
    accel_magnitude = np.sqrt(
        sensor_data.get('accelerometer_x', 0)**2 +
        sensor_data.get('accelerometer_y', 0)**2 +
        sensor_data.get('accelerometer_z', 9.8)**2
    )
    
    if abs(accel_magnitude - 9.8) > 2:
        issues.append("Accelerometer readings suggest sensor malfunction")
    
    return issues

def calculate_statistics(data, column):
    """Calculate basic statistics for a column"""
    if data.empty or column not in data.columns:
        return {}
    
    return {
        'mean': float(data[column].mean()),
        'median': float(data[column].median()),
        'std': float(data[column].std()),
        'min': float(data[column].min()),
        'max': float(data[column].max()),
        'count': int(data[column].count())
    }