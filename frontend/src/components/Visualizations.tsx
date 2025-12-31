/*
 * Visualizations Component - Charts for predictions
 */

import React from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    AreaChart, Area
} from 'recharts';

interface VisualizationProps {
    data: any[];
    type: 'seir' | 'spread' | 'trends';
}

export const Visualizations: React.FC<VisualizationProps> = ({ data, type }) => {
    if (type === 'seir') {
        return (
            <div className="h-64 w-full bg-white p-4 rounded-lg shadow-sm">
                <h3 className="text-sm font-semibold mb-2">SEIR Model Projection</h3>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="day" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="susceptible" stroke="#3b82f6" dot={false} />
                        <Line type="monotone" dataKey="exposed" stroke="#eab308" dot={false} />
                        <Line type="monotone" dataKey="infected" stroke="#ef4444" dot={false} />
                        <Line type="monotone" dataKey="recovered" stroke="#22c55e" dot={false} />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        );
    }

    return (
        <div className="h-64 w-full bg-white p-4 rounded-lg shadow-sm">
            <h3 className="text-sm font-semibold mb-2">Trend Analysis</h3>
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="cases" stroke="#8884d8" fill="#8884d8" />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};
