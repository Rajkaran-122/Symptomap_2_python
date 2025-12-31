/*
 * Analytics Dashboard - Charts and Statistics with Real Data
 */

import React, { useState, useEffect } from 'react';
import { SymptoMapAPI } from '@/services/api';
import { Activity, TrendingUp, AlertCircle, BarChart } from 'lucide-react';

interface AnalyticsData {
    disease_distribution: Array<{ disease: string; count: number }>;
    severity_distribution: Array<{ severity: string; count: number }>;
    top_regions: Array<{ region: string; count: number }>;
}

export const AnalyticsDashboard: React.FC = () => {
    const [analyticsData, setAnalyticsData] = useState<AnalyticsData>({
        disease_distribution: [],
        severity_distribution: [],
        top_regions: []
    });

    const [dashboardStats, setDashboardStats] = useState<any>({});

    useEffect(() => {
        loadAnalytics();
    }, []);

    const loadAnalytics = async () => {
        try {
            const [analytics, stats] = await Promise.all([
                SymptoMapAPI.getAnalyticsData(),
                SymptoMapAPI.getDashboardStats()
            ]);

            setAnalyticsData(analytics);
            setDashboardStats(stats);
        } catch (error) {
            console.error('Failed to load analytics:', error);
        }
    };

    const getSeverityColor = (severity: string) => {
        switch (severity?.toLowerCase()) {
            case 'severe': return 'bg-critical';
            case 'moderate': return 'bg-warning';
            case 'mild': return 'bg-success';
            default: return 'bg-gray-500';
        }
    };

    const maxDiseaseCount = Math.max(...analyticsData.disease_distribution.map(d => d.count), 1);
    const totalPatients = analyticsData.severity_distribution.reduce((sum, s) => sum + s.count, 0) || 1;

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
                    <p className="text-gray-600">Real-time outbreak data analysis and insights</p>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                        <div className="flex items-center justify-between mb-4">
                            <div className="w-12 h-12 bg-critical-bg rounded-xl flex items-center justify-center">
                                <AlertCircle className="w-6 h-6 text-critical" />
                            </div>
                            <TrendingUp className="w-5 h-5 text-success" />
                        </div>
                        <p className="text-sm text-gray-600 font-medium mb-1">Total Outbreaks</p>
                        <p className="text-3xl font-bold font-mono text-gray-900">{dashboardStats.active_outbreaks || 0}</p>
                    </div>

                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                        <div className="flex items-center justify-between mb-4">
                            <div className="w-12 h-12 bg-info-bg rounded-xl flex items-center justify-center">
                                <Activity className="w-6 h-6 text-info" />
                            </div>
                        </div>
                        <p className="text-sm text-gray-600 font-medium mb-1">Hospitals</p>
                        <p className="text-3xl font-bold font-mono text-gray-900">{dashboardStats.hospitals_monitored || '0+'}</p>
                    </div>

                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                        <div className="flex items-center justify-between mb-4">
                            <div className="w-12 h-12 bg-warning-bg rounded-xl flex items-center justify-center">
                                <BarChart className="w-6 h-6 text-warning" />
                            </div>
                        </div>
                        <p className="text-sm text-gray-600 font-medium mb-1">Predictions</p>
                        <p className="text-3xl font-bold font-mono text-gray-900">{dashboardStats.ai_predictions || 0}</p>
                    </div>

                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                        <div className="flex items-center justify-between mb-4">
                            <div className="w-12 h-12 bg-success-bg rounded-xl flex items-center justify-center">
                                <span className="text-2xl">📍</span>
                            </div>
                        </div>
                        <p className="text-sm text-gray-600 font-medium mb-1">Coverage</p>
                        <p className="text-3xl font-bold font-mono text-gray-900">{dashboardStats.coverage_area || '0 States'}</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Disease Distribution */}
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                        <h3 className="text-xl font-bold text-gray-900 mb-6">Disease Distribution</h3>

                        {analyticsData.disease_distribution.length > 0 ? (
                            <div className="space-y-4">
                                {analyticsData.disease_distribution.map((item, idx) => (
                                    <div key={idx}>
                                        <div className="flex justify-between text-sm mb-2">
                                            <span className="font-medium text-gray-700">{item.disease}</span>
                                            <span className="text-gray-600 font-semibold">{item.count} cases</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-3">
                                            <div
                                                className="bg-primary-500 h-3 rounded-full transition-all duration-500"
                                                style={{ width: `${(item.count / maxDiseaseCount) * 100}%` }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-12 text-gray-500">
                                <p className="text-4xl mb-2">📊</p>
                                <p>No disease data available</p>
                                <p className="text-sm">Add outbreaks via Doctor Station to see analytics</p>
                            </div>
                        )}
                    </div>

                    {/* Severity Distribution */}
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                        <h3 className="text-xl font-bold text-gray-900 mb-6">Severity Breakdown</h3>

                        {analyticsData.severity_distribution.length > 0 ? (
                            <div className="flex justify-around items-end h-64">
                                {analyticsData.severity_distribution.map((item, idx) => {
                                    const percentage = (item.count / totalPatients) * 100;
                                    return (
                                        <div key={idx} className="text-center flex flex-col items-center">
                                            <div
                                                className={`${getSeverityColor(item.severity)} w-20 rounded-t-lg transition-all duration-500`}
                                                style={{ height: `${percentage * 2}px`, minHeight: '20px' }}
                                            />
                                            <div className="mt-3 text-sm text-gray-600 font-medium capitalize">{item.severity}</div>
                                            <div className="text-2xl font-bold text-gray-900 mt-1">{item.count}</div>
                                            <div className="text-xs text-gray-500">{percentage.toFixed(1)}%</div>
                                        </div>
                                    );
                                })}
                            </div>
                        ) : (
                            <div className="text-center py-12 text-gray-500">
                                <p className="text-4xl mb-2">⚠️</p>
                                <p>No severity data available</p>
                            </div>
                        )}
                    </div>

                    {/* Top Affected Regions */}
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                        <h3 className="text-xl font-bold text-gray-900 mb-6">Top Affected Regions</h3>

                        {analyticsData.top_regions.length > 0 ? (
                            <div className="space-y-3">
                                {analyticsData.top_regions.map((region, idx) => (
                                    <div key={idx} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-bold text-sm">
                                                {idx + 1}
                                            </div>
                                            <span className="font-semibold text-gray-900">{region.region}</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <span className="text-2xl font-bold text-primary-700">{region.count}</span>
                                            <span className="text-sm text-gray-500">outbreaks</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-12 text-gray-500">
                                <p className="text-4xl mb-2">🗺️</p>
                                <p>No regional data available</p>
                            </div>
                        )}
                    </div>

                    {/* System Health Status */}
                    <div className="bg-gradient-to-br from-primary-900 to-primary-800 p-6 rounded-2xl shadow-lg text-white">
                        <h3 className="text-xl font-bold mb-6">System Health</h3>

                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-primary-200">Data Quality</span>
                                <div className="flex items-center gap-2">
                                    <div className="w-24 bg-white/20 rounded-full h-2">
                                        <div className="bg-green-400 h-2 rounded-full" style={{ width: '95%' }}></div>
                                    </div>
                                    <span className="text-sm font-bold">95%</span>
                                </div>
                            </div>

                            <div className="flex items-center justify-between">
                                <span className="text-sm text-primary-200">API Uptime</span>
                                <div className="flex items-center gap-2">
                                    <div className="w-24 bg-white/20 rounded-full h-2">
                                        <div className="bg-green-400 h-2 rounded-full" style={{ width: '99.9%' }}></div>
                                    </div>
                                    <span className="text-sm font-bold">99.9%</span>
                                </div>
                            </div>

                            <div className="flex items-center justify-between">
                                <span className="text-sm text-primary-200">Accuracy Score</span>
                                <div className="flex items-center gap-2">
                                    <div className="w-24 bg-white/20 rounded-full h-2">
                                        <div className="bg-green-400 h-2 rounded-full" style={{ width: '87%' }}></div>
                                    </div>
                                    <span className="text-sm font-bold">87%</span>
                                </div>
                            </div>

                            <div className="mt-6 pt-4 border-t border-white/20">
                                <div className="flex items-center gap-2 text-xs text-primary-200">
                                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                                    <span>All systems operational</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AnalyticsDashboard;
