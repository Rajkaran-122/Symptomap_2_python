/*
 * Professional AI Prediction Dashboard
 * Comprehensive outbreak forecasting with interactive visualizations
 */

import React, { useState, useEffect } from 'react';
import { AreaChart, Area, LineChart, Line, Bar, ComposedChart, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, AlertTriangle, Activity, Calendar, Users, Hospital, Target, BarChart3, Layers, Zap } from 'lucide-react';

interface PredictionData {
    generated_at: string;
    scenario: string;
    forecast_days: number;
    summary: {
        current_active_cases: number;
        current_outbreaks: number;
        reproduction_number: number;
        peak_date: string;
        peak_cases: number;
        total_predicted_cases: number;
        risk_assessment: {
            level: string;
            score: number;
            color: string;
            r0: number;
            infection_rate: number;
        };
    };
    time_series: Array<{
        date: string;
        day: number;
        infected: { value: number; lower: number; upper: number };
        exposed: { value: number; lower: number; upper: number };
        recovered: { value: number; lower: number; upper: number };
        new_cases: { value: number; lower: number; upper: number };
    }>;
    geographic_predictions: Array<{
        location: string;
        disease: string;
        current_cases: number;
        predicted_cases_7d: number;
        predicted_cases_14d: number;
        predicted_cases_30d: number;
    }>;
    hospital_capacity: {
        current_hospitalized: number;
        peak_hospitalized: number;
        beds_needed: number;
        critical_date: string;
    };
    recommendations: Array<{
        priority: string;
        action: string;
        impact: string;
    }>;
}

export const PredictionDashboard: React.FC = () => {
    const [prediction, setPrediction] = useState<PredictionData | null>(null);
    const [comparisonData, setComparisonData] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [days, setDays] = useState(30);
    const [scenario, setScenario] = useState('likely');
    const [viewMode, setViewMode] = useState<'single' | 'pulse' | 'comparison'>('single');

    const loadPrediction = async () => {
        setLoading(true);
        try {
            const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';

            // If in comparison mode, fetch all three
            if (viewMode === 'comparison') {
                const scenarios = ['best', 'likely', 'worst'];
                const results = await Promise.all(
                    scenarios.map(s => fetch(`${API_URL}/predictions/forecast?days=${days}&scenario=${s}`).then(r => r.json()))
                );

                // Align time series for comparison
                const aligned = results[0].time_series.map((point: any, idx: number) => ({
                    day: point.day,
                    best: results[0].time_series[idx].infected.value,
                    likely: results[1].time_series[idx].infected.value,
                    worst: results[2].time_series[idx].infected.value,
                }));
                setComparisonData(aligned);
                setPrediction(results[1]); // Use 'likely' as default for metrics
            } else {
                const response = await fetch(`${API_URL}/predictions/forecast?days=${days}&scenario=${scenario}`);
                const data = await response.json();
                setPrediction(data);
            }
        } catch (error) {
            console.error('Failed to load prediction:', error);
            alert('Failed to load predictions. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadPrediction();
    }, [days, scenario, viewMode]);

    if (loading && !prediction) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
                <div className="text-center">
                    <div className="inline-block w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mb-4"></div>
                    <p className="text-gray-600 font-semibold">Generating AI Predictions...</p>
                </div>
            </div>
        );
    }

    if (!prediction) return null;

    const { summary, time_series, geographic_predictions, hospital_capacity, recommendations } = prediction;

    // Prepare chart data
    const chartData = time_series.map(point => ({
        day: point.day,
        infected: point.infected.value,
        exposed: point.exposed.value,
        recovered: point.recovered.value,
        new_cases: point.new_cases.value,
        infected_lower: point.infected.lower,
        infected_upper: point.infected.upper
    }));

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
            <div className="max-w-7xl mx-auto space-y-6">
                {/* Header with Controls */}
                <div className="bg-white rounded-2xl shadow-lg p-6">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                        <div className="flex-1">
                            <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Outbreak Predictions</h1>
                            <p className="text-gray-600">Advanced SEIR model forecasting with real-time data analysis</p>
                        </div>

                        {/* View Mode Switcher */}
                        <div className="flex bg-gray-100 p-1 rounded-xl w-full md:w-auto">
                            <button
                                onClick={() => setViewMode('single')}
                                className={`flex-1 md:w-32 py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-all ${viewMode === 'single' ? 'bg-white shadow-sm text-primary-600' : 'text-gray-500 hover:text-gray-700'
                                    }`}
                            >
                                <Activity className="w-4 h-4" /> Standard
                            </button>
                            <button
                                onClick={() => setViewMode('pulse')}
                                className={`flex-1 md:w-32 py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-all ${viewMode === 'pulse' ? 'bg-white shadow-sm text-primary-600' : 'text-gray-500 hover:text-gray-700'
                                    }`}
                            >
                                <Zap className="w-4 h-4" /> Pulse
                            </button>
                            <button
                                onClick={() => setViewMode('comparison')}
                                className={`flex-1 md:w-32 py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-all ${viewMode === 'comparison' ? 'bg-white shadow-sm text-primary-600' : 'text-gray-500 hover:text-gray-700'
                                    }`}
                            >
                                <Layers className="w-4 h-4" /> Scenarios
                            </button>
                        </div>

                        <div className="flex items-center gap-4 w-full md:w-auto">
                            <div className="flex-1">
                                <label className="block text-sm font-medium text-gray-700 mb-1">Forecast Period</label>
                                <select
                                    value={days}
                                    onChange={(e) => setDays(Number(e.target.value))}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                                >
                                    <option value={7}>7 Days</option>
                                    <option value={14}>14 Days</option>
                                    <option value={30}>30 Days</option>
                                    <option value={60}>60 Days</option>
                                </select>
                            </div>
                            {viewMode !== 'comparison' && (
                                <div className="flex-1">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Scenario</label>
                                    <select
                                        value={scenario}
                                        onChange={(e) => setScenario(e.target.value)}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                                    >
                                        <option value="best">Best Case</option>
                                        <option value="likely">Most Likely</option>
                                        <option value="worst">Worst Case</option>
                                    </select>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Risk Assessment Banner */}
                <div
                    className="rounded-2xl shadow-lg p-6 text-white"
                    style={{ background: `linear-gradient(135deg, ${summary.risk_assessment.color}, ${summary.risk_assessment.color}dd)` }}
                >
                    <div className="flex items-center justify-between">
                        <div>
                            <div className="flex items-center gap-3 mb-2">
                                <AlertTriangle className="w-8 h-8" />
                                <h2 className="text-2xl font-bold">Risk Level: {summary.risk_assessment.level}</h2>
                            </div>
                            <p className="text-sm opacity-90">
                                R₀: {summary.risk_assessment.r0} | Infection Rate: {summary.risk_assessment.infection_rate} per 100k
                            </p>
                        </div>
                        <div className="text-right">
                            <div className="text-4xl font-bold">{summary.risk_assessment.score}/10</div>
                            <div className="text-sm opacity-90">Risk Score</div>
                        </div>
                    </div>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="bg-white rounded-xl shadow-lg p-6">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                                <Activity className="w-6 h-6 text-blue-600" />
                            </div>
                            <div>
                                <div className="text-sm text-gray-500">Current Active</div>
                                <div className="text-2xl font-bold text-gray-900">{summary.current_active_cases.toLocaleString()}</div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-xl shadow-lg p-6">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                                <TrendingUp className="w-6 h-6 text-red-600" />
                            </div>
                            <div>
                                <div className="text-sm text-gray-500">Peak Cases</div>
                                <div className="text-2xl font-bold text-gray-900">{summary.peak_cases.toLocaleString()}</div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-xl shadow-lg p-6">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                                <Calendar className="w-6 h-6 text-green-600" />
                            </div>
                            <div>
                                <div className="text-sm text-gray-500">Peak Date</div>
                                <div className="text-lg font-bold text-gray-900">{new Date(summary.peak_date).toLocaleDateString()}</div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-xl shadow-lg p-6">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                                <Users className="w-6 h-6 text-purple-600" />
                            </div>
                            <div>
                                <div className="text-sm text-gray-500">Total Predicted</div>
                                <div className="text-2xl font-bold text-gray-900">{summary.total_predicted_cases.toLocaleString()}</div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Main Chart - Infection Forecast */}
                <div className="bg-white rounded-2xl shadow-lg p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-xl font-bold text-gray-900">
                            {viewMode === 'comparison' ? 'Scenario Comparison: Best vs Likely vs Worst' :
                                viewMode === 'pulse' ? 'Viral Pulse Intensity Analysis' :
                                    `Infection Forecast - ${days} Day Projection`}
                        </h3>
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                            <div className="w-3 h-3 rounded-full bg-red-400"></div> Infected
                            <div className="w-3 h-3 rounded-full bg-blue-400 ml-2"></div> R₀ Intensity
                        </div>
                    </div>

                    <div className="h-[450px]">
                        <ResponsiveContainer width="100%" height="100%">
                            {viewMode === 'comparison' ? (
                                <LineChart data={comparisonData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                    <XAxis dataKey="day" label={{ value: 'Days Ahead', position: 'insideBottom', offset: -10 }} />
                                    <YAxis label={{ value: 'Active Cases', angle: -90, position: 'insideLeft' }} />
                                    <Tooltip />
                                    <Legend />
                                    <Line type="monotone" dataKey="best" stroke="#10b981" strokeWidth={3} dot={false} name="Best Case (Low R₀)" />
                                    <Line type="monotone" dataKey="likely" stroke="#3b82f6" strokeWidth={3} dot={false} name="Most Likely" />
                                    <Line type="monotone" dataKey="worst" stroke="#ef4444" strokeWidth={3} dot={false} name="Worst Case (High R₀)" />
                                </LineChart>
                            ) : viewMode === 'pulse' ? (
                                <ComposedChart data={chartData}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                                    <XAxis dataKey="day" />
                                    <YAxis yAxisId="left" orientation="left" label={{ value: 'New Cases', angle: -90, position: 'insideLeft' }} />
                                    <YAxis yAxisId="right" orientation="right" label={{ value: 'R₀ Intensity (%)', angle: 90, position: 'insideRight' }} />
                                    <Tooltip />
                                    <Legend />
                                    <Bar yAxisId="left" dataKey="new_cases" fill="#fee2e2" radius={[4, 4, 0, 0]} name="Case Volume" />
                                    <Area yAxisId="left" type="monotone" dataKey="infected" fill="#fee2e2" stroke="#ef4444" name="Total Infected" />
                                    <Line yAxisId="right" type="step" dataKey="infected" stroke="#3b82f6" strokeWidth={2} dot={false} name="Viral Pulse (Velocity)" />
                                </ComposedChart>
                            ) : (
                                <AreaChart data={chartData}>
                                    <defs>
                                        <linearGradient id="colorInfected" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#EF4444" stopOpacity={0.8} />
                                            <stop offset="95%" stopColor="#EF4444" stopOpacity={0.1} />
                                        </linearGradient>
                                        <linearGradient id="colorExposed" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.8} />
                                            <stop offset="95%" stopColor="#F59E0B" stopOpacity={0.1} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                                    <XAxis dataKey="day" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Area type="monotone" dataKey="infected" stroke="#EF4444" fillOpacity={1} fill="url(#colorInfected)" name="Infected" />
                                    <Area type="monotone" dataKey="exposed" stroke="#F59E0B" fillOpacity={1} fill="url(#colorExposed)" name="Exposed" />
                                </AreaChart>
                            )}
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Hospital Capacity & Geographic Spread */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Hospital Capacity */}
                    <div className="bg-white rounded-2xl shadow-lg p-6">
                        <div className="flex items-center gap-3 mb-4">
                            <Hospital className="w-6 h-6 text-primary-600" />
                            <h3 className="text-xl font-bold text-gray-900">Hospital Capacity Forecast</h3>
                        </div>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center p-4 bg-blue-50 rounded-lg">
                                <span className="text-gray-700">Current Hospitalized</span>
                                <span className="text-2xl font-bold text-blue-600">{hospital_capacity.current_hospitalized}</span>
                            </div>
                            <div className="flex justify-between items-center p-4 bg-red-50 rounded-lg">
                                <span className="text-gray-700">Peak Hospitalized</span>
                                <span className="text-2xl font-bold text-red-600">{hospital_capacity.peak_hospitalized}</span>
                            </div>
                            <div className="flex justify-between items-center p-4 bg-amber-50 rounded-lg">
                                <span className="text-gray-700">Additional Beds Needed</span>
                                <span className="text-2xl font-bold text-amber-600">{hospital_capacity.beds_needed}</span>
                            </div>
                            <div className="text-center text-sm text-gray-600 mt-4">
                                Critical Date: <span className="font-bold">{new Date(hospital_capacity.critical_date).toLocaleDateString()}</span>
                            </div>
                        </div>
                    </div>

                    {/* Geographic Predictions */}
                    <div className="bg-white rounded-2xl shadow-lg p-6">
                        <div className="flex items-center gap-3 mb-4">
                            <Target className="w-6 h-6 text-primary-600" />
                            <h3 className="text-xl font-bold text-gray-900">Geographic Spread Forecast</h3>
                        </div>
                        <div className="space-y-3">
                            {geographic_predictions.slice(0, 5).map((area, idx) => (
                                <div key={idx} className="p-4 bg-gray-50 rounded-lg">
                                    <div className="flex justify-between items-center mb-2">
                                        <div className="font-semibold text-gray-900">{area.location}</div>
                                        <div className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">{area.disease}</div>
                                    </div>
                                    <div className="grid grid-cols-4 gap-2 text-sm">
                                        <div className="text-center">
                                            <div className="text-gray-500 text-xs">Current</div>
                                            <div className="font-bold">{area.current_cases}</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-gray-500 text-xs">7 Days</div>
                                            <div className="font-bold text-blue-600">{area.predicted_cases_7d}</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-gray-500 text-xs">14 Days</div>
                                            <div className="font-bold text-amber-600">{area.predicted_cases_14d}</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-gray-500 text-xs">30 Days</div>
                                            <div className="font-bold text-red-600">{area.predicted_cases_30d}</div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* AI Recommendations */}
                <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl shadow-lg p-6 text-white">
                    <div className="flex items-center gap-3 mb-4">
                        <BarChart3 className="w-6 h-6" />
                        <h3 className="text-xl font-bold">AI-Generated Recommendations</h3>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {recommendations.map((rec, idx) => (
                            <div key={idx} className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
                                <div className={`inline-block px-2 py-1 rounded text-xs font-bold mb-2 ${rec.priority === 'HIGH' ? 'bg-red-500' : 'bg-yellow-500'
                                    }`}>
                                    {rec.priority} PRIORITY
                                </div>
                                <div className="font-semibold mb-2">{rec.action}</div>
                                <div className="text-sm opacity-90">{rec.impact}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PredictionDashboard;
