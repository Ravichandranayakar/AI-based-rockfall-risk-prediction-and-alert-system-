"""
Data Processing Module for Rockfall Risk Prediction System
Handles data cleaning, feature engineering, and ML inference
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Main class for processing sensor data"""
    
    def __init__(self, zones_file=None):
        if zones_file is None:
            zones_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    'sample-data', 'zones.json')
        
        with open(zones_file, 'r') as f:
            self.zones_data = json.load(f)
        
        self.zone_thresholds = {}
        for zone in self.zones_data['zones']:
            self.zone_thresholds[zone['zone_id']] = zone['risk_thresholds']
    
    def clean_sensor_data(self, df):
        """Clean and validate sensor data"""
        logger.info(f"Cleaning {len(df)} sensor records")
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        numeric_columns = [
            'displacement_mm', 'vibration_mm_s', 'temperature_c', 
            'humidity_percent', 'pressure_kpa', 'accelerometer_x',
            'accelerometer_y', 'accelerometer_z'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                # Fill missing with median
                df[col] = df[col].fillna(df[col].median())
                
                # Remove obvious outliers (beyond reasonable sensor ranges)
                if col == 'temperature_c':
                    df[col] = df[col].clip(-20, 60)
                elif col == 'humidity_percent':
                    df[col] = df[col].clip(0, 100)
                elif col == 'pressure_kpa':
                    df[col] = df[col].clip(90, 110)
                elif col == 'displacement_mm':
                    df[col] = df[col].clip(0, 50)  # Max 50mm displacement
                elif col == 'vibration_mm_s':
                    df[col] = df[col].clip(0, 20)  # Max 20 mm/s vibration
        
        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Validate zone IDs
        valid_zones = [zone['zone_id'] for zone in self.zones_data['zones']]
        df = df[df['zone_id'].isin(valid_zones)]
        
        logger.info(f"Cleaned data: {len(df)} records remaining")
        return df
    
    def engineer_features(self, df):
        """Create additional features for ML model"""
        logger.info("Engineering features...")
        
        # Sort by zone and timestamp
        df = df.sort_values(['zone_id', 'timestamp'])
        
        # Calculate rates of change
        df['displacement_rate'] = df.groupby('zone_id')['displacement_mm'].diff()
        df['vibration_rate'] = df.groupby('zone_id')['vibration_mm_s'].diff()
        df['temperature_rate'] = df.groupby('zone_id')['temperature_c'].diff()
        
        # Fill NaN values in rate columns (first record per zone)
        rate_columns = ['displacement_rate', 'vibration_rate', 'temperature_rate']
        for col in rate_columns:
            df[col] = df[col].fillna(0)
        
        # Calculate moving averages (smoothing)
        window = 3  # 3 data points
        df['displacement_ma'] = df.groupby('zone_id')['displacement_mm'].rolling(window, min_periods=1).mean().reset_index(0, drop=True)
        df['vibration_ma'] = df.groupby('zone_id')['vibration_mm_s'].rolling(window, min_periods=1).mean().reset_index(0, drop=True)
        
        # Calculate acceleration magnitude
        df['acceleration_magnitude'] = np.sqrt(
            df['accelerometer_x']**2 + 
            df['accelerometer_y']**2 + 
            df['accelerometer_z']**2
        )
        
        # Calculate deviation from normal gravity (9.8 m/s²)
        df['gravity_deviation'] = np.abs(df['acceleration_magnitude'] - 9.8)
        
        # Time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        # Weather comfort index
        df['weather_index'] = (
            (df['temperature_c'] - 22) ** 2 +  # Deviation from 22°C
            (df['humidity_percent'] - 60) ** 2 / 100  # Deviation from 60%
        )
        
        # Zone stability score (based on historical performance)
        zone_stability = {
            'A': 0.8,  # North Pit Wall - stable
            'B': 0.6,  # South Slope - moderate
            'C': 0.9,  # East Bench - very stable
            'D': 0.4   # West Highwall - unstable
        }
        df['zone_stability'] = df['zone_id'].map(zone_stability).fillna(0.5)
        
        # Risk indicators
        df['displacement_risk_flag'] = df.apply(
            lambda row: self._check_threshold(row, 'displacement_mm', 'displacement'), axis=1
        )
        df['vibration_risk_flag'] = df.apply(
            lambda row: self._check_threshold(row, 'vibration_mm_s', 'vibration'), axis=1
        )
        
        logger.info(f"Feature engineering complete. Shape: {df.shape}")
        return df
    
    def _check_threshold(self, row, column, threshold_type):
        """Check if value exceeds zone threshold"""
        zone_id = row['zone_id']
        value = row[column]
        
        if zone_id not in self.zone_thresholds:
            return 0
        
        thresholds = self.zone_thresholds[zone_id]
        warning_key = f"{threshold_type}_warning"
        critical_key = f"{threshold_type}_critical"
        
        if value >= thresholds.get(critical_key, float('inf')):
            return 2  # Critical
        elif value >= thresholds.get(warning_key, float('inf')):
            return 1  # Warning
        else:
            return 0  # Normal
    
    def calculate_risk_scores(self, df):
        """Calculate comprehensive risk scores"""
        logger.info("Calculating risk scores...")
        
        # Normalize features to 0-1 scale for scoring
        features_to_normalize = [
            'displacement_mm', 'vibration_mm_s', 'displacement_rate', 
            'vibration_rate', 'gravity_deviation', 'weather_index'
        ]
        
        for feature in features_to_normalize:
            if feature in df.columns:
                # Min-max normalization per zone
                df[f'{feature}_norm'] = df.groupby('zone_id')[feature].transform(
                    lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() > x.min() else 0
                )
        
        # Calculate composite risk score
        df['composite_risk_score'] = (
            df['displacement_mm_norm'] * 0.3 +
            df['vibration_mm_s_norm'] * 0.3 +
            df['displacement_rate_norm'] * 0.15 +
            df['vibration_rate_norm'] * 0.15 +
            df['gravity_deviation_norm'] * 0.05 +
            df['weather_index_norm'] * 0.05
        )
        
        # Adjust by zone stability
        df['adjusted_risk_score'] = df['composite_risk_score'] / df['zone_stability']
        
        # Scale to 0-10
        df['risk_score_10'] = df['adjusted_risk_score'] * 10
        df['risk_score_10'] = df['risk_score_10'].clip(0, 10)
        
        # Categorize risk levels
        df['risk_category'] = pd.cut(
            df['risk_score_10'],
            bins=[0, 3, 6, 10],
            labels=['low', 'high', 'critical'],
            include_lowest=True
        )
        
        return df
    
    def detect_anomalies(self, df):
        """Detect anomalies in sensor data"""
        logger.info("Detecting anomalies...")
        
        anomalies = []
        
        for zone_id in df['zone_id'].unique():
            zone_data = df[df['zone_id'] == zone_id].copy()
            
            # Statistical anomaly detection (3-sigma rule)
            for column in ['displacement_mm', 'vibration_mm_s']:
                if len(zone_data) > 5:  # Need enough data
                    mean = zone_data[column].mean()
                    std = zone_data[column].std()
                    threshold = mean + 3 * std
                    
                    anomaly_indices = zone_data[zone_data[column] > threshold].index
                    
                    for idx in anomaly_indices:
                        anomalies.append({
                            'timestamp': zone_data.loc[idx, 'timestamp'],
                            'zone_id': zone_id,
                            'anomaly_type': f'{column}_statistical',
                            'value': zone_data.loc[idx, column],
                            'threshold': threshold,
                            'severity': 'high' if zone_data.loc[idx, column] > threshold * 1.5 else 'medium'
                        })
            
            # Rate of change anomalies
            for column in ['displacement_rate', 'vibration_rate']:
                if column in zone_data.columns:
                    # Sudden spikes in rate of change
                    high_rate_indices = zone_data[np.abs(zone_data[column]) > zone_data[column].std() * 2].index
                    
                    for idx in high_rate_indices:
                        anomalies.append({
                            'timestamp': zone_data.loc[idx, 'timestamp'],
                            'zone_id': zone_id,
                            'anomaly_type': f'{column}_spike',
                            'value': zone_data.loc[idx, column],
                            'severity': 'medium'
                        })
        
        logger.info(f"Detected {len(anomalies)} anomalies")
        return anomalies
    
    def generate_summary_report(self, df):
        """Generate summary report of processed data"""
        report = {
            'processing_timestamp': datetime.now().isoformat(),
            'total_records': len(df),
            'zones_processed': df['zone_id'].nunique(),
            'time_range': {
                'start': df['timestamp'].min().isoformat() if not df.empty else None,
                'end': df['timestamp'].max().isoformat() if not df.empty else None
            },
            'zone_summary': {}
        }
        
        # Per-zone summary
        for zone_id in df['zone_id'].unique():
            zone_data = df[df['zone_id'] == zone_id]
            
            report['zone_summary'][zone_id] = {
                'record_count': len(zone_data),
                'avg_displacement': float(zone_data['displacement_mm'].mean()),
                'max_displacement': float(zone_data['displacement_mm'].max()),
                'avg_vibration': float(zone_data['vibration_mm_s'].mean()),
                'max_vibration': float(zone_data['vibration_mm_s'].max()),
                'current_risk_score': float(zone_data['risk_score_10'].iloc[-1]) if not zone_data.empty else 0,
                'risk_category': str(zone_data['risk_category'].iloc[-1]) if not zone_data.empty else 'unknown'
            }
        
        return report
    
    def process_batch(self, input_file, output_file=None):
        """Process a batch of sensor data"""
        logger.info(f"Processing batch file: {input_file}")
        
        # Load data
        df = pd.read_csv(input_file)
        
        # Process pipeline
        df = self.clean_sensor_data(df)
        df = self.engineer_features(df)
        df = self.calculate_risk_scores(df)
        
        # Detect anomalies
        anomalies = self.detect_anomalies(df)
        
        # Generate report
        report = self.generate_summary_report(df)
        
        # Save processed data
        if output_file:
            df.to_csv(output_file, index=False)
            logger.info(f"Processed data saved to: {output_file}")
        
        # Save anomalies
        if anomalies:
            anomalies_file = output_file.replace('.csv', '_anomalies.json') if output_file else 'anomalies.json'
            with open(anomalies_file, 'w') as f:
                json.dump(anomalies, f, indent=2)
            logger.info(f"Anomalies saved to: {anomalies_file}")
        
        # Save report
        report_file = output_file.replace('.csv', '_report.json') if output_file else 'processing_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Report saved to: {report_file}")
        
        return df, anomalies, report

def main():
    """Main function for testing data processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rockfall Data Processing')
    parser.add_argument('--input', required=True, help='Input CSV file')
    parser.add_argument('--output', help='Output CSV file')
    
    args = parser.parse_args()
    
    # Create processor
    processor = DataProcessor()
    
    # Process data
    try:
        df, anomalies, report = processor.process_batch(args.input, args.output)
        
        print(f"Processing complete!")
        print(f"Records processed: {len(df)}")
        print(f"Anomalies detected: {len(anomalies)}")
        print(f"Zones: {df['zone_id'].unique().tolist()}")
        
    except Exception as e:
        logger.error(f"Error processing data: {e}")

if __name__ == "__main__":
    main()