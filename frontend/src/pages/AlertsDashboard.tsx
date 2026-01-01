/*
 * Alert Management Dashboard
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface Alert {
    id: string;
    alert_type: string;
    severity: string;
    title: string;
    zone_name: string;
    sent_at: string;
    recipients_count: number;
    delivery_status: any;
    acknowledged_count: number;
}

export const AlertsDashboard: React.FC = () => {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [loading, setLoading] = useState(true);
    const [showSendModal, setShowSendModal] = useState(false);

    useEffect(() => {
        loadAlerts();
    }, []);

    const loadAlerts = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/alerts/`);
            setAlerts(response.data);
        } catch (error) {
            console.error('Failed to load alerts:', error);
        } finally {
            setLoading(false);
        }
    };

    const acknowledgeAlert = async (alertId: string) => {
        try {
            await axios.post(`${API_BASE_URL}/alerts/${alertId}/acknowledge`);
            loadAlerts();
        } catch (error) {
            console.error('Failed to acknowledge alert:', error);
        }
    };

    const getSeverityColor = (severity: string) => {
        const colors = {
            critical: 'bg-red-100 text-red-800 border-red-300',
            warning: 'bg-amber-100 text-amber-800 border-amber-300',
            info: 'bg-blue-100 text-blue-800 border-blue-300'
        };
        return colors[severity as keyof typeof colors] || 'bg-gray-100 text-gray-800';
    };

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Alert Management</h1>
                        <p className="text-gray-600">Send and manage outbreak alerts</p>
                    </div>
                    <button
                        onClick={() => setShowSendModal(true)}
                        className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium"
                    >
                        + Send New Alert
                    </button>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-white p-4 rounded-lg shadow-sm">
                        <div className="text-sm text-gray-600">Total Alerts</div>
                        <div className="text-2xl font-bold text-gray-900">{alerts.length}</div>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow-sm">
                        <div className="text-sm text-gray-600">Critical</div>
                        <div className="text-2xl font-bold text-red-600">
                            {alerts.filter(a => a.severity === 'critical').length}
                        </div>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow-sm">
                        <div className="text-sm text-gray-600">Sent Today</div>
                        <div className="text-2xl font-bold text-gray-900">
                            {alerts.filter(a => {
                                const today = new Date().toDateString();
                                return new Date(a.sent_at).toDateString() === today;
                            }).length}
                        </div>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow-sm">
                        <div className="text-sm text-gray-600">Total Recipients</div>
                        <div className="text-2xl font-bold text-gray-900">
                            {alerts.reduce((sum, a) => sum + a.recipients_count, 0)}
                        </div>
                    </div>
                </div>

                {/* Alerts Table */}
                <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Zone</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Recipients</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sent</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {loading ? (
                                <tr>
                                    <td colSpan={7} className="px-6 py-4 text-center text-gray-500">Loading...</td>
                                </tr>
                            ) : alerts.length === 0 ? (
                                <tr>
                                    <td colSpan={7} className="px-6 py-4 text-center text-gray-500">No alerts sent yet</td>
                                </tr>
                            ) : (
                                alerts.map((alert) => (
                                    <tr key={alert.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4">
                                            <span className={`px-2 py-1 text-xs rounded border ${getSeverityColor(alert.severity)}`}>
                                                {alert.severity}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-900">{alert.title}</td>
                                        <td className="px-6 py-4 text-sm text-gray-600">{alert.zone_name}</td>
                                        <td className="px-6 py-4 text-sm text-gray-900">{alert.recipients_count}</td>
                                        <td className="px-6 py-4 text-sm text-gray-600">
                                            {new Date(alert.sent_at).toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="text-green-600 text-sm">
                                                ✓ {alert.delivery_status?.email || 'sent'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <button
                                                onClick={() => acknowledgeAlert(alert.id)}
                                                className="text-blue-600 hover:text-blue-800 text-sm"
                                            >
                                                View
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Send Alert Modal */}
                {showSendModal && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                        <div className="bg-white rounded-lg p-6 max-w-md w-full">
                            <h3 className="text-xl font-bold mb-4">Send New Alert</h3>
                            <p className="text-sm text-gray-600 mb-4">
                                Use the API to send alerts programmatically. See documentation for details.
                            </p>
                            <div className="bg-gray-100 p-3 rounded text-xs font-mono mb-4">
                                POST /api/v1/alerts/send
                            </div>
                            <button
                                onClick={() => setShowSendModal(false)}
                                className="w-full bg-gray-600 text-white py-2 rounded hover:bg-gray-700"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AlertsDashboard;
