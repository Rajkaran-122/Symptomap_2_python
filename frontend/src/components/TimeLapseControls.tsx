/*
 * Time Lapse Controls Component
 */

import React, { useState, useEffect } from 'react';

export const TimeLapseControls: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentDate, setCurrentDate] = useState(new Date());

  useEffect(() => {
    let interval: any;
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentDate(prev => new Date(prev.getTime() + 86400000)); // +1 day
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isPlaying]);

  return (
    <div className="bg-white p-4 rounded-lg shadow-lg">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold text-sm">Time Lapse</h3>
        <span className="text-xs text-gray-500">
          {currentDate.toLocaleDateString()}
        </span>
      </div>

      <div className="flex items-center space-x-2">
        <button
          onClick={() => setIsPlaying(!isPlaying)}
          className="bg-emerald-600 text-white p-2 rounded hover:bg-emerald-700 w-10 flex justify-center"
        >
          {isPlaying ? '⏸' : '▶'}
        </button>

        <input
          type="range"
          className="flex-1"
          min="0"
          max="100"
          defaultValue="0"
        />
      </div>
    </div>
  );
};
