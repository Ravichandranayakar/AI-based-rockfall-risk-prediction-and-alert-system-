import React, { useEffect, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const Charts = ({ zones = [], alerts = [] }) => {
  // Ensure zones and alerts are arrays
  const zonesArray = Array.isArray(zones) ? zones : [];
  const alertsArray = Array.isArray(alerts) ? alerts : [];
  
  const timeLabels = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00'];

  // Generate sample data based on risk levels
  const generateTrendData = (baseValue, riskLevel) => {
    const multiplier = riskLevel === 'CRITICAL' ? 6 : riskLevel === 'WARNING' ? 3 : 1;
    return timeLabels.map((_, index) => {
      const trend = index * 0.8 * multiplier;
      const noise = (Math.random() - 0.5) * 0.5;
      return Math.max(0, baseValue + trend + noise);
    });
  };

  const displacementData = {
    labels: timeLabels,
    datasets: [
      {
        label: 'Zone B (Critical)',
        data: generateTrendData(2.1, 'CRITICAL'),
        borderColor: '#EF4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.3,
        fill: true,
      },
      {
        label: 'Zone D (Warning)',
        data: generateTrendData(1.8, 'WARNING'),
        borderColor: '#F59E0B',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        tension: 0.3,
        fill: true,
      },
      {
        label: 'Average',
        data: generateTrendData(1.2, 'LOW'),
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.3,
        fill: true,
        borderDash: [5, 5],
      },
    ],
  };

  const vibrationData = {
    labels: timeLabels,
    datasets: [
      {
        label: 'Zone B (Critical)',
        data: generateTrendData(0.8, 'CRITICAL'),
        borderColor: '#EF4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.3,
        fill: true,
      },
      {
        label: 'Zone D (Warning)',
        data: generateTrendData(1.2, 'WARNING'),
        borderColor: '#F59E0B',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        tension: 0.3,
        fill: true,
      },
      {
        label: 'Average',
        data: generateTrendData(0.8, 'LOW'),
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.3,
        fill: true,
        borderDash: [5, 5],
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false,
    },
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      {/* Displacement Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Displacement Trends</h3>
        <div style={{ height: '300px' }}>
          <Line data={displacementData} options={{
            ...chartOptions,
            scales: {
              ...chartOptions.scales,
              y: {
                ...chartOptions.scales.y,
                title: {
                  display: true,
                  text: 'Displacement (mm)'
                }
              }
            }
          }} />
        </div>
      </div>

      {/* Vibration Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Vibration Trends</h3>
        <div style={{ height: '300px' }}>
          <Line data={vibrationData} options={{
            ...chartOptions,
            scales: {
              ...chartOptions.scales,
              y: {
                ...chartOptions.scales.y,
                title: {
                  display: true,
                  text: 'Vibration (g)'
                }
              }
            }
          }} />
        </div>
      </div>
    </div>
  );
};

export default Charts;