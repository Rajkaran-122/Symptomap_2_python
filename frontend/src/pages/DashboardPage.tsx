
import { useEffect } from 'react';
import { useRealTimeStats } from '@/hooks/useRealTimeStats';
import { useToast } from '@/hooks/useToast';
import { useWebSocket } from '@/hooks/useWebSocket';
import { OutbreakMap } from '@/components/OutbreakMap';
import { FilterPanel } from '@/components/FilterPanel';
import ActivityFeed from '@/components/ActivityFeed';
import WeekComparison from '@/components/WeekComparison';
import { Activity, Clock, Users, Zap, TrendingUp, Shield, AlertCircle, FileText, MapPin, Target } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ToastContainer } from '@/components/Toast';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';
const WS_URL = API_BASE_URL.replace('http', 'ws').replace('/api/v1', '') + '/api/v1/ws';

// Mock SEIR data for the chart
const seirData = [
    { day: 1, susceptible: 950, exposed: 30, infected: 15, recovered: 5 },
    { day: 5, susceptible: 800, exposed: 80, infected: 90, recovered: 30 },
    { day: 10, susceptible: 600, exposed: 120, infected: 180, recovered: 100 },
    { day: 15, susceptible: 400, exposed: 100, infected: 250, recovered: 250 },
    { day: 20, susceptible: 200, exposed: 50, infected: 150, recovered: 600 },
];

const DashboardPage = () => {
    // Use real-time stats hook for all dashboard data
    const { stats: dashboardStats, performance, riskZones: riskData, isConnected } = useRealTimeStats();
    const { toasts, addToast, removeToast } = useToast();
    const { lastMessage } = useWebSocket(WS_URL);

    // Use fetched performance data or fallback to defaults
    const performanceMetrics = performance || {
        api_latency: '0ms',
        api_latency_trend: 0,
        active_users: '0',
        active_users_trend: 0,
        system_uptime: '0%',
        uptime_trend: 0,
        last_sync: 'N/A'
    };

    // Use fetched risk data or fallback to defaults
    const riskZones = riskData || {
        high_risk_zones: 0,
        at_risk_population: '0'
    };

    // Show toast notification when new outbreak arrives
    useEffect(() => {
        if (lastMessage?.type === 'NEW_OUTBREAK') {
            const outbreak = lastMessage.data;
            addToast(
                `🚨 New ${outbreak.severity} outbreak: ${outbreak.disease} in ${outbreak.location?.city}`,
                outbreak.severity === 'severe' ? 'error' : outbreak.severity === 'moderate' ? 'warning' : 'info'
            );
        } else if (lastMessage?.type === 'NEW_ALERT') {
            const alert = lastMessage.data;
            addToast(
                `⚠️ New ${alert.alert_type} alert: ${alert.title}`,
                'warning'
            );
        }
    }, [lastMessage, addToast]);
    // WebSocket and data loading removed - OutbreakMap component handles its own data fetching

    return (
        <>
            <ToastContainer toasts={toasts} removeToast={removeToast} />
            <div className="space-y-6">
                {/* Hero Stats Bar */}
                <div className="bg-gradient-to-br from-primary-900 via-primary-800 to-primary-900 rounded-3xl p-8 text-white shadow-xl relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-96 h-96 bg-primary-700/20 rounded-full blur-3xl"></div>
                    <div className="relative z-10">
                        <div className="flex items-center justify-between mb-6">
                            <div>
                                <h2 className="text-3xl font-bold mb-2">Disease Surveillance Dashboard</h2>
                                <p className="text-primary-200 text-sm font-medium">Real-time analytics and AI-powered predictions</p>
                            </div>
                            <div className="flex items-center gap-3 bg-white/10 backdrop-blur-md px-6 py-3 rounded-full border border-white/20">
                                <div className="relative flex h-3 w-3">
                                    {isConnected ? (
                                        <>
                                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                                        </>
                                    ) : (
                                        <span className="relative inline-flex rounded-full h-3 w-3 bg-yellow-500"></span>
                                    )}
                                </div>
                                <span className="text-sm font-semibold">
                                    {isConnected ? 'Real-Time Active' : 'Connecting...'}
                                </span>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div className="flex items-center gap-3 bg-white/50 backdrop-blur-sm px-5 py-3 rounded-xl border border-white/20">
                                <div className="w-2 h-2 rounded-full bg-critical animate-pulse"></div>
                                <div>
                                    <p className="text-xs text-gray-700 font-medium">Active Outbreaks</p>
                                    <p className="text-lg font-bold text-gray-900">{dashboardStats?.active_outbreaks || 0}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3 bg-white/50 backdrop-blur-sm px-5 py-3 rounded-xl border border-white/20">
                                <div className="w-2 h-2 rounded-full bg-info animate-pulse"></div>
                                <div>
                                    <p className="text-xs text-gray-700 font-medium">Hospitals Monitored</p>
                                    <p className="text-lg font-bold text-gray-900">{dashboardStats?.hospitals_monitored || '0+'}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3 bg-white/50 backdrop-blur-sm px-5 py-3 rounded-xl border border-white/20">
                                <div className="w-2 h-2 rounded-full bg-warning animate-pulse"></div>
                                <div>
                                    <p className="text-xs text-gray-700 font-medium">AI Predictions</p>
                                    <p className="text-lg font-bold text-gray-900">{dashboardStats?.ai_predictions || 0}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3 bg-white/50 backdrop-blur-sm px-5 py-3 rounded-xl border border-white/20">
                                <div className="w-2 h-2 rounded-full bg-success animate-pulse"></div>
                                <div>
                                    <p className="text-xs text-gray-700 font-medium">Coverage Area</p>
                                    <p className="text-lg font-bold text-gray-900">{dashboardStats?.coverage_area || '0 States'}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* ROW 1: Filters + AI Shield Card */}
                <div className="grid grid-cols-12 gap-6">
                    {/* Filters Panel */}
                    <div className="col-span-12 lg:col-span-8">
                        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                            <FilterPanel />
                        </div>
                    </div>

                    {/* AI Shield Active Card */}
                    <div className="col-span-12 lg:col-span-4">
                        <div className="bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl p-6 text-white shadow-lg h-full flex flex-col justify-between">
                            <div>
                                <div className="flex items-center gap-3 mb-4">
                                    <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                                        <Shield className="w-6 h-6" />
                                    </div>
                                    <h3 className="text-xl font-bold">AI Shield Active</h3>
                                </div>
                                <p className="text-sm text-emerald-50 leading-relaxed mb-4">
                                    Monitoring {dashboardStats?.hospitals_monitored || '0+'} hospitals across {dashboardStats?.coverage_area || '0 States'}. Early warning system is actively scanning for anomalies.
                                </p>
                            </div>
                            <div className="flex items-center gap-2 text-xs font-semibold bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg w-fit">
                                <AlertCircle className="w-4 h-4" />
                                <span>{riskZones.high_risk_zones} high risk zones detected</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* ROW 2: Full Width Map */}
                <div className="bg-white rounded-3xl shadow-md border border-gray-100 overflow-hidden">
                    <div className="h-[500px] bg-gray-50">
                        <OutbreakMap />
                    </div>
                </div>

                {/* ROW 3: SEIR Model + Risk Assessment */}
                <div className="grid grid-cols-12 gap-6">
                    {/* SEIR Model Projection */}
                    <div className="col-span-12 lg:col-span-8">
                        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                            <div className="mb-6">
                                <h3 className="text-xl font-bold text-gray-900 mb-1">SEIR Model Projection</h3>
                                <p className="text-sm text-gray-500">30-day projection based on current infection rate (R₀ = 2.5)</p>
                            </div>

                            <ResponsiveContainer width="100%" height={300}>
                                <LineChart data={seirData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                                    <XAxis
                                        dataKey="day"
                                        stroke="#64748b"
                                        style={{ fontSize: '12px', fontWeight: 500 }}
                                    />
                                    <YAxis
                                        stroke="#64748b"
                                        style={{ fontSize: '12px', fontWeight: 500 }}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: '#fff',
                                            border: '1px solid #e2e8f0',
                                            borderRadius: '8px',
                                            fontSize: '12px'
                                        }}
                                    />
                                    <Legend
                                        wrapperStyle={{ fontSize: '13px', fontWeight: 600 }}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="susceptible"
                                        stroke="#8b5cf6"
                                        strokeWidth={2.5}
                                        dot={{ r: 4 }}
                                        activeDot={{ r: 6 }}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="exposed"
                                        stroke="#f59e0b"
                                        strokeWidth={2.5}
                                        dot={{ r: 4 }}
                                        activeDot={{ r: 6 }}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="infected"
                                        stroke="#ef4444"
                                        strokeWidth={2.5}
                                        dot={{ r: 4 }}
                                        activeDot={{ r: 6 }}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="recovered"
                                        stroke="#10b981"
                                        strokeWidth={2.5}
                                        dot={{ r: 4 }}
                                        activeDot={{ r: 6 }}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Risk Assessment */}
                    <div className="col-span-12 lg:col-span-4">
                        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 h-full flex flex-col">
                            <h3 className="text-xl font-bold text-gray-900 mb-6">Risk Assessment</h3>

                            <div className="space-y-4 flex-1">
                                {/* High Risk Zones */}
                                <div className="bg-critical-bg border border-critical/20 rounded-xl p-5">
                                    <div className="flex items-center gap-3 mb-2">
                                        <MapPin className="w-5 h-5 text-critical" />
                                        <p className="text-sm font-semibold text-gray-600">High Risk Zones</p>
                                    </div>
                                    <p className="text-4xl font-bold text-critical">{riskZones.high_risk_zones}</p>
                                </div>

                                {/* At Risk Population */}
                                <div className="bg-warning-bg border border-warning/20 rounded-xl p-5">
                                    <div className="flex items-center gap-3 mb-2">
                                        <Target className="w-5 h-5 text-warning" />
                                        <p className="text-sm font-semibold text-gray-600">At Risk Population</p>
                                    </div>
                                    <p className="text-4xl font-bold text-warning">{riskZones.at_risk_population}</p>
                                </div>
                            </div>

                            {/* Generate Report Button */}
                            <button
                                onClick={async () => {
                                    try {
                                        const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';
                                        const response = await fetch(`${API_URL}/reports/download/summary`);

                                        if (!response.ok) throw new Error('Network response was not ok');

                                        const blob = await response.blob();
                                        const url = window.URL.createObjectURL(blob);
                                        const a = document.createElement('a');
                                        a.style.display = 'none';
                                        a.href = url;
                                        a.download = `symptomap_report_${new Date().toISOString().split('T')[0]}.txt`;
                                        document.body.appendChild(a);
                                        a.click();
                                        window.URL.revokeObjectURL(url);
                                    } catch (error) {
                                        console.error('Failed to generate report:', error);
                                        alert('Failed to generate report. Please try again.');
                                    }
                                }}
                                className="mt-6 w-full bg-primary-700 hover:bg-primary-800 text-white font-semibold py-4 px-6 rounded-xl transition-colors flex items-center justify-center gap-2 shadow-sm"
                            >
                                <FileText className="w-5 h-5" />
                                Generate Detailed Report
                            </button>
                        </div>
                    </div>
                </div>

                {/* ROW 4: Activity Feed and Week Comparison */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    <div className="col-span-12 lg:col-span-8">
                        <ActivityFeed limit={8} className="h-full" />
                    </div>
                    <div className="col-span-12 lg:col-span-4">
                        <WeekComparison className="h-full" />
                    </div>
                </div>

                {/* ROW 5: System Performance Metrics */}
                <div className="bg-gradient-to-br from-gray-50 to-white rounded-3xl p-8 border border-gray-100 shadow-sm">
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h3 className="text-2xl font-bold text-gray-900">System Performance</h3>
                            <p className="text-sm text-gray-500 mt-1">Real-time monitoring of platform health and usage</p>
                        </div>
                        <div className="px-4 py-2 bg-success-bg text-success rounded-full text-xs font-bold uppercase tracking-wider">
                            Optimal
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {/* API Latency */}
                        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-300 group">
                            <div className="flex items-start justify-between mb-6">
                                <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-green-400 to-emerald-500 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                                    <Zap className="w-7 h-7 text-white" />
                                </div>
                                {performanceMetrics.api_latency_trend !== 0 && (
                                    <div className={`flex items-center gap-1 text-sm font-bold ${performanceMetrics.api_latency_trend < 0 ? 'text-success' : 'text-warning'}`}>
                                        <TrendingUp className={`w-4 h-4 ${performanceMetrics.api_latency_trend < 0 ? 'rotate-180' : ''}`} />
                                        <span>{Math.abs(performanceMetrics.api_latency_trend)}%</span>
                                    </div>
                                )}
                            </div>
                            <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider mb-2">API Latency</p>
                            <p className="text-4xl font-bold font-mono text-gray-900">{performanceMetrics.api_latency}</p>
                        </div>

                        {/* Active Users */}
                        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-300 group">
                            <div className="flex items-start justify-between mb-6">
                                <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                                    <Users className="w-7 h-7 text-white" />
                                </div>
                                {performanceMetrics.active_users_trend !== 0 && (
                                    <div className="flex items-center gap-1 text-sm font-bold text-success">
                                        <TrendingUp className="w-4 h-4" />
                                        <span>{performanceMetrics.active_users_trend}%</span>
                                    </div>
                                )}
                            </div>
                            <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider mb-2">Active Users</p>
                            <p className="text-4xl font-bold font-mono text-gray-900">{performanceMetrics.active_users}</p>
                        </div>

                        {/* System Uptime */}
                        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-300 group">
                            <div className="flex items-start justify-between mb-6">
                                <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-purple-400 to-violet-500 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                                    <Activity className="w-7 h-7 text-white" />
                                </div>
                                {performanceMetrics.uptime_trend !== 0 && (
                                    <div className="flex items-center gap-1 text-sm font-bold text-success">
                                        <TrendingUp className="w-4 h-4" />
                                        <span>{performanceMetrics.uptime_trend}%</span>
                                    </div>
                                )}
                            </div>
                            <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider mb-2">System Uptime</p>
                            <p className="text-4xl font-bold font-mono text-gray-900">{performanceMetrics.system_uptime}</p>
                        </div>

                        {/* Last Sync */}
                        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-all duration-300 group">
                            <div className="flex items-start justify-between mb-6">
                                <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-orange-400 to-amber-500 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                                    <Clock className="w-7 h-7 text-white" />
                                </div>
                                <div className="relative flex h-2 w-2">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                                </div>
                            </div>
                            <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider mb-2">Last Sync</p>
                            <p className="text-4xl font-bold font-mono text-gray-900">{performanceMetrics.last_sync}</p>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};

export default DashboardPage;
