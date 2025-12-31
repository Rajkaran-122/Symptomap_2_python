/*
 * Reports Dashboard Page
 * Professional report generation and display
 */

import React, { useState, useEffect } from 'react';
import { FileText, Download, Calendar, TrendingUp, Users, MapPin, AlertCircle, BarChart3, PieChart } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';
const WS_URL = API_BASE_URL.replace('http', 'ws').replace('/api/v1', '') + '/api/v1/ws';

interface ReportData {
    report_type: string;
    generated_at: string;
    period_days: number;
    summary: {
        outbreaks: {
            total: number;
            severe: number;
            moderate: number;
            mild: number;
            total_patients: number;
        };
        alerts: {
            total: number;
            critical: number;
            warning: number;
        };
        hospitals: {
            affected: number;
        };
    };
}

export const ReportsPage: React.FC = () => {
    const [reportData, setReportData] = useState<ReportData | null>(null);
    const [loading, setLoading] = useState(false);
    const [days, setDays] = useState(30);

    // Real-time WebSocket connection
    const { lastMessage } = useWebSocket(WS_URL);

    const generateReport = async () => {
        setLoading(true);
        try {
            const response = await fetch(
                `${API_BASE_URL}/reports/comprehensive?days=${days}`
            );
            const data = await response.json();
            setReportData(data);
        } catch (error) {
            console.error('Failed to generate report:', error);
            alert('Failed to generate report. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    // Auto-load report data on mount and when days changes
    useEffect(() => {
        generateReport();
    }, [days]);

    // Listen for real-time events and auto-refresh
    useEffect(() => {
        if (lastMessage?.type === 'NEW_OUTBREAK' || lastMessage?.type === 'NEW_ALERT') {
            console.log('🔄 Reports: Refreshing due to real-time event');
            generateReport();
        }
    }, [lastMessage]);

    const downloadReport = () => {
        if (!reportData) return;

        const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `comprehensive_report_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-4xl font-bold text-gray-900 mb-2">Reports & Analytics</h1>
                            <p className="text-gray-600">Generate comprehensive outbreak and health surveillance reports</p>
                        </div>
                        <div className="flex items-center gap-3">
                            <FileText className="w-12 h-12 text-primary-600" />
                        </div>
                    </div>
                </div>

                {/* Coming Soon Banner */}
                <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-2xl shadow-lg p-8 mb-6 text-white">
                    <div className="flex items-center gap-4 mb-4">
                        <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                            <BarChart3 className="w-8 h-8" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold">Reports Module Coming Soon!</h2>
                            <p className="text-blue-100">Advanced analytics and custom report templates are under development</p>
                        </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                            <PieChart className="w-6 h-6 mb-2" />
                            <p className="text-sm font-semibold">Custom Templates</p>
                        </div>
                        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                            <TrendingUp className="w-6 h-6 mb-2" />
                            <p className="text-sm font-semibold">Trend Analysis</p>
                        </div>
                        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                            <Download className="w-6 h-6 mb-2" />
                            <p className="text-sm font-semibold">PDF Exports</p>
                        </div>
                    </div>
                </div>

                {/* Report Generator */}
                <div className="bg-white rounded-2xl shadow-lg p-8">
                    <h3 className="text-2xl font-bold text-gray-900 mb-6">Generate Detailed Report</h3>

                    {/* Controls */}
                    <div className="flex items-center gap-4 mb-6">
                        <div className="flex items-center gap-2">
                            <Calendar className="w-5 h-5 text-gray-600" />
                            <label className="text-sm font-medium text-gray-700">Time Period:</label>
                            <select
                                value={days}
                                onChange={(e) => setDays(Number(e.target.value))}
                                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            >
                                <option value={7}>Last 7 days</option>
                                <option value={30}>Last 30 days</option>
                                <option value={60}>Last 60 days</option>
                                <option value={90}>Last 90 days</option>
                            </select>
                        </div>

                        <button
                            onClick={generateReport}
                            disabled={loading}
                            className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-2 rounded-lg font-semibold flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                            {loading ? (
                                <>
                                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <FileText className="w-5 h-5" />
                                    Generate Report
                                </>
                            )}
                        </button>

                        {reportData && (
                            <button
                                onClick={downloadReport}
                                className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-semibold flex items-center gap-2 transition-all"
                            >
                                <Download className="w-5 h-5" />
                                Download JSON
                            </button>
                        )}
                    </div>

                    {/* Report Display */}
                    {reportData && (
                        <div className="space-y-6 animate-fadeIn">
                            {/* Report Header */}
                            <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-6 border border-gray-200">
                                <div className="flex items-center justify-between mb-4">
                                    <div>
                                        <h4 className="text-xl font-bold text-gray-900">Comprehensive Health Report</h4>
                                        <p className="text-sm text-gray-600">
                                            Generated: {new Date(reportData.generated_at).toLocaleString()}
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-sm text-gray-600">Period</div>
                                        <div className="text-lg font-bold text-primary-600">{reportData.period_days} Days</div>
                                    </div>
                                </div>
                            </div>

                            {/* Key Metrics */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                {/* Outbreak Stats */}
                                <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-6 border-2 border-red-200">
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="w-12 h-12 bg-red-500 rounded-lg flex items-center justify-center">
                                            <AlertCircle className="w-6 h-6 text-white" />
                                        </div>
                                        <div>
                                            <div className="text-sm text-gray-600 font-medium">Total Outbreaks</div>
                                            <div className="text-3xl font-bold text-red-700">{reportData.summary.outbreaks.total}</div>
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <div className="flex justify-between text-sm">
                                            <span className="text-gray-600">🔴 Severe:</span>
                                            <span className="font-bold text-red-700">{reportData.summary.outbreaks.severe}</span>
                                        </div>
                                        <div className="flex justify-between text-sm">
                                            <span className="text-gray-600">🟡 Moderate:</span>
                                            <span className="font-bold text-amber-600">{reportData.summary.outbreaks.moderate}</span>
                                        </div>
                                        <div className="flex justify-between text-sm">
                                            <span className="text-gray-600">🟢 Mild:</span>
                                            <span className="font-bold text-green-600">{reportData.summary.outbreaks.mild}</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Patient Stats */}
                                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border-2 border-blue-200">
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
                                            <Users className="w-6 h-6 text-white" />
                                        </div>
                                        <div>
                                            <div className="text-sm text-gray-600 font-medium">Total Patients</div>
                                            <div className="text-3xl font-bold text-blue-700">{reportData.summary.outbreaks.total_patients.toLocaleString()}</div>
                                        </div>
                                    </div>
                                    <div className="text-sm text-gray-600">
                                        Across {reportData.summary.hospitals.affected} affected hospitals
                                    </div>
                                </div>

                                {/* Alert Stats */}
                                <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-6 border-2 border-amber-200">
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="w-12 h-12 bg-amber-500 rounded-lg flex items-center justify-center">
                                            <AlertCircle className="w-6 h-6 text-white" />
                                        </div>
                                        <div>
                                            <div className="text-sm text-gray-600 font-medium">Total Alerts</div>
                                            <div className="text-3xl font-bold text-amber-700">{reportData.summary.alerts.total}</div>
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <div className="flex justify-between text-sm">
                                            <span className="text-gray-600">Critical:</span>
                                            <span className="font-bold text-red-600">{reportData.summary.alerts.critical}</span>
                                        </div>
                                        <div className="flex justify-between text-sm">
                                            <span className="text-gray-600">Warning:</span>
                                            <span className="font-bold text-amber-600">{reportData.summary.alerts.warning}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Hospital Coverage */}
                            <div className="bg-white rounded-xl p-6 border-2 border-gray-200">
                                <div className="flex items-center gap-3 mb-4">
                                    <MapPin className="w-6 h-6 text-primary-600" />
                                    <h5 className="text-lg font-bold text-gray-900">Healthcare Coverage</h5>
                                </div>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div className="bg-gray-50 rounded-lg p-4 text-center">
                                        <div className="text-2xl font-bold text-primary-600">{reportData.summary.hospitals.affected}</div>
                                        <div className="text-sm text-gray-600">Affected Hospitals</div>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-4 text-center">
                                        <div className="text-2xl font-bold text-green-600">
                                            {Math.round((reportData.summary.outbreaks.mild / Math.max(reportData.summary.outbreaks.total, 1)) * 100)}%
                                        </div>
                                        <div className="text-sm text-gray-600">Mild Cases</div>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-4 text-center">
                                        <div className="text-2xl font-bold text-amber-600">
                                            {Math.round((reportData.summary.outbreaks.moderate / Math.max(reportData.summary.outbreaks.total, 1)) * 100)}%
                                        </div>
                                        <div className="text-sm text-gray-600">Moderate Cases</div>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-4 text-center">
                                        <div className="text-2xl font-bold text-red-600">
                                            {Math.round((reportData.summary.outbreaks.severe / Math.max(reportData.summary.outbreaks.total, 1)) * 100)}%
                                        </div>
                                        <div className="text-sm text-gray-600">Severe Cases</div>
                                    </div>
                                </div>
                            </div>

                            {/* Report Footer */}
                            <div className="bg-gray-50 rounded-xl p-6 border border-gray-200 text-center">
                                <p className="text-sm text-gray-600">
                                    This report was automatically generated by SymptoMap AI Health Surveillance System
                                </p>
                                <p className="text-xs text-gray-500 mt-2">
                                    Report ID: {reportData.report_type}-{new Date(reportData.generated_at).getTime()}
                                </p>
                            </div>
                        </div>
                    )}

                    {/* Empty State */}
                    {!reportData && !loading && (
                        <div className="text-center py-12">
                            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                            <p className="text-gray-500 text-lg">Click "Generate Report" to create a comprehensive health report</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ReportsPage;
