/*
 * Prediction Panel Component
 * Shows SEIR models and spreadsheet predictions
 */

import React from 'react';
import { Visualizations } from './Visualizations';

export const PredictionPanel: React.FC = () => {
  // Mock data for MVP
  const seirData = [
    { day: 1, susceptible: 1000, exposed: 0, infected: 1, recovered: 0 },
    { day: 5, susceptible: 950, exposed: 40, infected: 10, recovered: 0 },
    { day: 10, susceptible: 800, exposed: 150, infected: 45, recovered: 5 },
    { day: 15, susceptible: 500, exposed: 300, infected: 150, recovered: 50 },
    { day: 20, susceptible: 200, exposed: 400, infected: 300, recovered: 100 },
  ];

  return (
    <div className="bg-white p-4 rounded-lg shadow-lg w-96 max-h-[80vh] overflow-y-auto">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold">Predictive Analytics</h2>
        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Beta</span>
      </div>

      <div className="space-y-6">
        <div>
          <h3 className="text-sm font-semibold mb-2 text-gray-700">Disease Spread Forecast (SEIR)</h3>
          <p className="text-xs text-gray-500 mb-2">30-day projection based on current infection rate (R0 = 2.5)</p>
          <Visualizations data={seirData} type="seir" />
        </div>

        <div>
          <h3 className="text-sm font-semibold mb-2 text-gray-700">Risk Assessment</h3>
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-red-50 p-3 rounded border border-red-100">
              <div className="text-xs text-gray-500">High Risk Zones</div>
              <div className="text-xl font-bold text-red-600">3</div>
            </div>
            <div className="bg-amber-50 p-3 rounded border border-amber-100">
              <div className="text-xs text-gray-500">At Risk Population</div>
              <div className="text-xl font-bold text-amber-600">12.5K</div>
            </div>
          </div>
        </div>

        <button
          onClick={async () => {
            try {
              const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';
              const response = await fetch(`${API_URL}/reports/outbreak-summary?format=csv&days=30`);
              const blob = await response.blob();
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `outbreak_summary_${new Date().toISOString().split('T')[0]}.csv`;
              a.click();
              URL.revokeObjectURL(url);
            } catch (error) {
              console.error('Failed to download report:', error);
              alert('Failed to download report. Please try again.');
            }
          }}
          className="w-full bg-blue-600 text-white py-2 rounded text-sm hover:bg-blue-700"
        >
          Generate Detailed Report
        </button>
      </div>
    </div>
  );
};
