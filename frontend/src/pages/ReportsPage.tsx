/*
 * Reports Dashboard Page
 * Professional report generation and display
 */

import React, { useState, useEffect } from 'react';
import { FileText, Download, Calendar, Users, MapPin, AlertCircle, BarChart3, Sparkles, Clock, Share2 } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';
import EmailNotification from '../components/EmailNotification';

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
    const [showEmailModal, setShowEmailModal] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Real-time WebSocket connection
    const { lastMessage } = useWebSocket(WS_URL);

    const generateReport = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(
                `${API_BASE_URL}/reports/comprehensive?days=${days}`
            );
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            const data = await response.json();
            setReportData(data);
        } catch (error: any) {
            console.error('Failed to generate report:', error);
            // Check if it's a CORS/Network error
            if (error.message?.includes('Failed to fetch') || error.message?.includes('NetworkError')) {
                setError('Unable to connect to server. The backend may be updating. Please try again in a few minutes.');
            } else {
                setError(error.message || 'Failed to generate report. Please try again.');
            }
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
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Pro Header with Glassmorphism */}
                <div className="relative bg-white/70 backdrop-blur-xl rounded-3xl shadow-xl border border-white/50 p-8 mb-6 overflow-hidden">
                    {/* Background decorations */}
                    <div className="absolute top-0 right-0 w-72 h-72 bg-gradient-to-br from-blue-400/20 to-indigo-500/10 rounded-full blur-3xl -z-10"></div>
                    <div className="absolute bottom-0 left-0 w-48 h-48 bg-gradient-to-tr from-emerald-400/10 to-cyan-500/5 rounded-full blur-3xl -z-10"></div>

                    <div className="flex items-center justify-between relative">
                        <div>
                            <div className="flex items-center gap-3 mb-2">
                                <div className="p-2 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg shadow-blue-200">
                                    <FileText className="w-6 h-6 text-white" />
                                </div>
                                <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-indigo-900 bg-clip-text text-transparent">
                                    Reports & Analytics
                                </h1>
                            </div>
                            <p className="text-gray-500 ml-14">Generate comprehensive outbreak and health surveillance reports</p>
                        </div>
                        <div className="flex items-center gap-3">
                            <button
                                onClick={() => setShowEmailModal(true)}
                                className="p-3 rounded-xl bg-gradient-to-br from-gray-100 to-gray-200 hover:from-gray-200 hover:to-gray-300 transition-all shadow-sm"
                                title="Email Notifications"
                            >
                                <Share2 className="w-5 h-5 text-gray-600" />
                            </button>
                            <div className="p-4 rounded-2xl bg-gradient-to-br from-blue-100 to-indigo-100">
                                <Sparkles className="w-8 h-8 text-indigo-600" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Quick Stats Row */}
                <div className="grid grid-cols-4 gap-4 mb-6">
                    {[
                        { label: 'Reports Generated', value: '24', icon: FileText, color: 'blue' },
                        { label: 'Last Updated', value: 'Just now', icon: Clock, color: 'green' },
                        { label: 'Data Sources', value: '3', icon: BarChart3, color: 'purple' },
                        { label: 'Export Formats', value: 'JSON, CSV', icon: Download, color: 'amber' },
                    ].map((stat, idx) => (
                        <div key={idx} className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 border border-white/50 shadow-sm hover:shadow-md transition-all">
                            <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-lg bg-${stat.color}-100`}>
                                    <stat.icon className={`w-4 h-4 text-${stat.color}-600`} />
                                </div>
                                <div>
                                    <div className="text-lg font-bold text-gray-900">{stat.value}</div>
                                    <div className="text-xs text-gray-500">{stat.label}</div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Email Modal */}
                {showEmailModal && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center">
                        <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={() => setShowEmailModal(false)} />
                        <div className="relative z-10 w-full max-w-md mx-4">
                            <EmailNotification onClose={() => setShowEmailModal(false)} />
                        </div>
                    </div>
                )}

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

                    {/* Error Display */}
                    {error && (
                        <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-3">
                            <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                            <div>
                                <p className="text-amber-800 font-medium">Connection Issue</p>
                                <p className="text-amber-700 text-sm">{error}</p>
                                <button
                                    onClick={generateReport}
                                    className="mt-2 text-sm text-amber-800 underline hover:text-amber-900"
                                >
                                    Try Again
                                </button>
                            </div>
                        </div>
                    )}

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
