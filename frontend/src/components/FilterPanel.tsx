/*
 * Filter Panel Component
 */

import React from 'react';

export const FilterPanel: React.FC = () => {
  return (
    <div className="bg-white p-4 rounded-lg shadow-lg">
      <h3 className="font-semibold mb-3">Filters</h3>

      <div className="space-y-4">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Disease Type</label>
          <select className="w-full border rounded px-2 py-1 text-sm">
            <option>All Diseases</option>
            <option>Dengue</option>
            <option>Malaria</option>
            <option>COVID-19</option>
            <option>Influenza</option>
          </select>
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">Date Range</label>
          <select className="w-full border rounded px-2 py-1 text-sm">
            <option>Last 7 Days</option>
            <option>Last 30 Days</option>
            <option>Last 3 Months</option>
            <option>All Time</option>
          </select>
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">Severity</label>
          <div className="space-y-1">
            <label className="flex items-center text-sm">
              <input type="checkbox" defaultChecked className="mr-2" /> Critical
            </label>
            <label className="flex items-center text-sm">
              <input type="checkbox" defaultChecked className="mr-2" /> Moderate
            </label>
            <label className="flex items-center text-sm">
              <input type="checkbox" defaultChecked className="mr-2" /> Mild
            </label>
          </div>
        </div>
      </div>
    </div>
  );
};
