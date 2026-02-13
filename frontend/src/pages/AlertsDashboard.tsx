import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import {
    AlertCircle, ShieldAlert, Info, Bell,
    MapPin, Eye, CheckCircle2,
    X, Send, Activity, Radio
} from 'lucide-react';
import { API_BASE_URL } from '../config/api';

interface Alert {
    id: string;
    alert_type: string;
    severity: string;
    title: string;
    message?: string;
    zone_name: string;
    sent_at: string;
    recipients_count: number;
    delivery_status: any;
    acknowledged_count: number;
}

interface AlertDetail {
    id: string;
    alert_type: string;
    severity: string;
    title: string;
    message: string;
    zone_name: string;
    sent_at: string;
    recipients: string[];
    delivery_status: any;
    acknowledged_by: any[];
}

export const AlertsDashboard: React.FC = () => {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [loading, setLoading] = useState(true);
    const [showSendModal, setShowSendModal] = useState(false);
    const [showViewModal, setShowViewModal] = useState(false);
    const [selectedAlert, setSelectedAlert] = useState<AlertDetail | null>(null);
    const [viewLoading, setViewLoading] = useState(false);

    useEffect(() => {
        loadAlerts();
    }, []);

    const loadAlerts = async () => {
        setLoading(true);
        try {
            const response = await axios.get(`${API_BASE_URL}/alerts/`);
            setAlerts(Array.isArray(response.data) ? response.data : []);
        } catch (error) {
            console.error('Failed to load alerts:', error);
        } finally {
            setLoading(false);
        }
    };

    const viewAlert = async (alertId: string) => {
        setViewLoading(true);
        setShowViewModal(true);
        try {
            const response = await axios.get(`${API_BASE_URL}/alerts/${alertId}`);
            setSelectedAlert(response.data);
        } catch (error) {
            console.error('Failed to load alert details:', error);
            setSelectedAlert(null);
        } finally {
            setViewLoading(false);
        }
    };

    const acknowledgeAlert = async (alertId: string) => {
        try {
            await axios.post(`${API_BASE_URL}/alerts/${alertId}/acknowledge-public`, {});
            loadAlerts();
            if (selectedAlert && selectedAlert.id === alertId) {
                viewAlert(alertId);
            }
        } catch (error) {
            console.error('Failed to acknowledge alert:', error);
            alert('Failed to acknowledge alert. Please try again.');
        }
    };

    const getSeverityStyles = (severity: string) => {
        const styles: any = {
            critical: 'bg-red-500/10 text-red-500 border-red-500/20 shadow-[0_0_15px_rgba(239,68,68,0.2)]',
            warning: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
            info: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
        };
        return styles[severity] || 'bg-slate-500/10 text-slate-400 border-slate-500/20';
    };

    const getSeverityIcon = (severity: string) => {
        switch (severity) {
            case 'critical': return <ShieldAlert className="w-4 h-4" />;
            case 'warning': return <AlertCircle className="w-4 h-4" />;
            default: return <Info className="w-4 h-4" />;
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-indigo-100 selection:text-indigo-900">
            {/* Professional Header - Enterprise Grade */}
            <header className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-sm backdrop-blur-xl bg-white/80 supports-[backdrop-filter]:bg-white/80">
                <div className="max-w-7xl mx-auto px-6 sm:px-8 py-4">
                    <div className="flex flex-col lg:flex-row justify-between items-center gap-4">
                        <div className="flex items-center gap-4">
                            <div className="bg-indigo-600 text-white p-2.5 rounded-xl shadow-lg shadow-indigo-600/20 animate-pulse">
                                <Radio className="w-6 h-6" />
                            </div>
                            <div>
                                <h1 className="text-xl font-bold text-slate-900 tracking-tight">Broadcast Command</h1>
                                <p className="text-sm text-slate-500 font-medium">Regional Alerting System</p>
                            </div>
                        </div>

                        <button
                            onClick={() => setShowSendModal(true)}
                            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-lg font-semibold transition-all shadow-md shadow-indigo-600/20 active:scale-95 border border-transparent"
                        >
                            <Send className="w-4 h-4" />
                            <span>Dispatch Alert</span>
                        </button>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-6 sm:px-8 py-8">
                {/* Analytics Overview Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
                    {[
                        { label: 'Total Broadcasts', value: alerts.length, icon: Radio, color: 'text-indigo-600', bg: 'bg-indigo-50', border: 'border-indigo-100' },
                        { label: 'Critical Alerts', value: alerts.filter(a => a.severity === 'critical').length, icon: ShieldAlert, color: 'text-rose-600', bg: 'bg-rose-50', border: 'border-rose-100' },
                        { label: 'Active Warnings', value: alerts.filter(a => a.severity === 'warning').length, icon: AlertCircle, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-100' },
                        { label: 'Nodes Reached', value: alerts.reduce((sum, a) => sum + a.recipients_count, 0), icon: Bell, color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-100' },
                    ].map((stat, i) => (
                        <div key={i} className="bg-white border border-slate-200 p-5 rounded-xl shadow-[0_2px_10px_-4px_rgba(6,81,237,0.1)] hover:shadow-lg transition-all duration-300 group">
                            <div className="flex justify-between items-start mb-4">
                                <div className={`p-2.5 rounded-lg ${stat.bg} ${stat.border} border`}>
                                    <stat.icon className={`w-5 h-5 ${stat.color} ${stat.label === 'Total Broadcasts' ? 'animate-pulse' : ''}`} />
                                </div>
                                <span className="flex items-center gap-1.5 text-xs font-semibold text-slate-400 bg-slate-50 px-2.5 py-1 rounded-full border border-slate-100">
                                    <Activity className="w-3 h-3 text-emerald-500" />
                                    ACTIVE
                                </span>
                            </div>
                            <div className="text-3xl font-bold text-slate-800 tracking-tight mb-1">{loading ? '...' : stat.value}</div>
                            <div className="text-sm text-slate-500 font-medium">{stat.label}</div>
                        </div>
                    ))}
                </div>

                {/* Surveillance Table */}
                <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
                    <div className="px-6 py-4 border-b border-slate-200 flex justify-between items-center bg-slate-50/50">
                        <h2 className="text-sm font-bold text-slate-700 uppercase tracking-wide">Recent Transmissions</h2>
                        <div className="flex items-center gap-2 text-xs font-medium text-slate-500 bg-white px-3 py-1 rounded-full border border-slate-200 shadow-sm">
                            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                            System Operational
                        </div>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-slate-50/50 border-b border-slate-200">
                                    <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status & Severity</th>
                                    <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Alert Details</th>
                                    <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Target Zone</th>
                                    <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-center">Reach</th>
                                    <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Timestamp</th>
                                    <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {loading ? (
                                    <tr>
                                        <td colSpan={6} className="px-6 py-16 text-center">
                                            <div className="flex flex-col items-center">
                                                <div className="w-10 h-10 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin mb-3"></div>
                                                <p className="text-slate-500 text-sm font-medium">Syncing broadcast logs...</p>
                                            </div>
                                        </td>
                                    </tr>
                                ) : alerts.length === 0 ? (
                                    <tr>
                                        <td colSpan={6} className="px-6 py-16 text-center">
                                            <div className="bg-slate-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                                                <Radio className="w-8 h-8 text-slate-400" />
                                            </div>
                                            <p className="text-slate-900 font-semibold mb-1">No active alerts</p>
                                            <p className="text-slate-500 text-sm">System is monitoring normally</p>
                                        </td>
                                    </tr>
                                ) : (
                                    alerts.map((a) => (
                                        <tr key={a.id} className="group hover:bg-slate-50/80 transition-colors">
                                            <td className="px-6 py-4">
                                                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wide border ${getSeverityStyles(a.severity)}`}>
                                                    {getSeverityIcon(a.severity)}
                                                    {a.severity}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="text-slate-900 font-semibold text-sm max-w-xs truncate">{a.title}</div>
                                                <div className="text-slate-400 text-xs font-mono mt-0.5">REF: {a.id.substring(0, 8)}</div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-2 text-slate-700 text-sm font-medium">
                                                    <div className="p-1 rounded bg-indigo-50 text-indigo-600">
                                                        <MapPin className="w-3 h-3" />
                                                    </div>
                                                    {a.zone_name}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 text-center">
                                                <div className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-medium border border-slate-200">
                                                    <Radio className="w-3 h-3" />
                                                    {a.recipients_count}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="text-slate-600 text-sm font-medium">
                                                    {new Date(a.sent_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                                                </div>
                                                <div className="text-slate-400 text-xs">
                                                    {new Date(a.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <button
                                                    onClick={() => viewAlert(a.id)}
                                                    className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
                                                    title="Inspect Alert"
                                                >
                                                    <Eye className="w-4 h-4" />
                                                </button>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                    <div className="bg-slate-50 border-t border-slate-200 px-6 py-3 text-xs text-slate-500 text-right">
                        Showing {alerts.length} transmissions
                    </div>
                </div>
            </main>

            {/* View Modal - Clean & Professional */}
            {showViewModal && (
                <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl w-full max-w-xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200 border border-slate-100">
                        {viewLoading ? (
                            <div className="flex items-center justify-center py-20">
                                <div className="w-10 h-10 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
                            </div>
                        ) : selectedAlert ? (
                            <>
                                <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                                    <div className="flex items-center gap-3">
                                        <div className={`p-1.5 rounded-lg border ${getSeverityStyles(selectedAlert.severity)}`}>
                                            {getSeverityIcon(selectedAlert.severity)}
                                        </div>
                                        <h2 className="text-lg font-bold text-slate-900">Alert Details</h2>
                                    </div>
                                    <button onClick={() => setShowViewModal(false)} className="text-slate-400 hover:text-slate-600 transition-colors p-1 hover:bg-slate-100 rounded-full">
                                        <X className="w-5 h-5" />
                                    </button>
                                </div>

                                <div className="p-6 space-y-6">
                                    <div>
                                        <h3 className="text-xl font-bold text-slate-900 mb-2">{selectedAlert.title}</h3>
                                        <div className="bg-slate-50 border border-slate-200 p-4 rounded-xl text-slate-600 text-sm leading-relaxed">
                                            {selectedAlert.message}
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="border border-slate-200 p-3 rounded-xl">
                                            <div className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-1">Impact Zone</div>
                                            <div className="text-slate-900 font-semibold flex items-center gap-2">
                                                <MapPin className="w-4 h-4 text-indigo-500" />
                                                {selectedAlert.zone_name}
                                            </div>
                                        </div>
                                        <div className="border border-slate-200 p-3 rounded-xl">
                                            <div className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-1">Classification</div>
                                            <div className="text-slate-900 font-semibold capitalize flex items-center gap-2">
                                                <Info className="w-4 h-4 text-blue-500" />
                                                {selectedAlert.alert_type}
                                            </div>
                                        </div>
                                    </div>

                                    <div>
                                        <div className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">Target Nodes ({selectedAlert.recipients.length})</div>
                                        <div className="flex flex-wrap gap-2 max-h-24 overflow-y-auto pr-2 custom-scrollbar">
                                            {selectedAlert.recipients.map((email, idx) => (
                                                <span key={idx} className="bg-white border border-slate-200 px-2.5 py-1 rounded-full text-xs font-medium text-slate-600 shadow-sm">
                                                    {email}
                                                </span>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="flex gap-3 pt-2">
                                        <button
                                            onClick={() => acknowledgeAlert(selectedAlert.id)}
                                            className="flex-1 bg-emerald-600 hover:bg-emerald-700 py-2.5 rounded-lg text-white font-semibold shadow-sm transition-all flex items-center justify-center gap-2 active:scale-95"
                                        >
                                            <CheckCircle2 className="w-4 h-4" />
                                            Acknowledge
                                        </button>
                                        <button
                                            onClick={() => setShowViewModal(false)}
                                            className="px-6 py-2.5 bg-white border border-slate-200 hover:bg-slate-50 hover:border-slate-300 rounded-lg text-slate-700 font-semibold transition-all"
                                        >
                                            Close
                                        </button>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <div className="p-12 text-center">
                                <AlertCircle className="w-12 h-12 text-rose-500 mx-auto mb-3 opacity-50" />
                                <p className="text-slate-900 font-medium">Alert data unavailable</p>
                                <button onClick={() => setShowViewModal(false)} className="mt-4 text-indigo-600 text-sm font-semibold hover:underline">Dismiss</button>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Send Modal Mockup */}
            {showSendModal && (
                <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl w-full max-w-md shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200 border border-slate-100">
                        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                            <h2 className="text-lg font-bold text-slate-900">Dispatch System</h2>
                            <button onClick={() => setShowSendModal(false)} className="text-slate-400 hover:text-slate-600 transition-colors">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="p-8 text-center">
                            <div className="w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Send className="w-8 h-8 text-indigo-600" />
                            </div>
                            <h3 className="text-slate-900 font-bold text-lg mb-2">Manual Dispatch Required</h3>
                            <p className="text-slate-500 text-sm mb-6 leading-relaxed">
                                Automated alerting is active. For manual broadcasts, please use the dedicated console.
                            </p>
                            <Link
                                to="/admin/broadcasts"
                                onClick={() => setShowSendModal(false)}
                                className="block w-full bg-indigo-600 hover:bg-indigo-700 py-2.5 rounded-lg text-white font-semibold shadow-md shadow-indigo-600/20 transition-all active:scale-95 mb-3"
                            >
                                Go to Broadcast Console
                            </Link>
                            <button
                                onClick={() => setShowSendModal(false)}
                                className="w-full py-2.5 text-slate-500 hover:text-slate-700 font-medium text-sm transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AlertsDashboard;
