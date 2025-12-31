/*
 * Admin Dashboard Component - Outbreak Management
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';

interface Outbreak {
    id: string;
    hospital: {
        name: string;
        location: { lat: number; lng: number };
    };
    disease_type: string;
    patient_count: number;
    severity: string;
    verified: boolean;
    date_reported: string;
}

export const AdminDashboard: React.FC = () => {
    const [outbreaks, setOutbreaks] = useState<Outbreak[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState({
        severity: 'all',
        verified: 'all',
        disease: ''
    });

    useEffect(() => {
        loadOutbreaks();
    }, [filter]);

    const loadOutbreaks = async () => {
        try {
            const params = new URLSearchParams();
            if (filter.severity !== 'all') params.append('severity', filter.severity);
            if (filter.verified !== 'all') params.append('verified', filter.verified);
            if (filter.disease) params.append('disease_type', filter.disease);

            const response = await axios.get(`${API_BASE_URL}/outbreaks/?${params}`);
            setOutbreaks(response.data);
        } catch (error) {
            console.error('Failed to load outbreaks:', error);
        } finally {
            setLoading(false);
        }
    };

    const verifyOutbreak = async (outbreakId: string) => {
        try {
            await axios.post(`${API_BASE_URL}/outbreaks/${outbreakId}/verify`);
            loadOutbreaks();
        } catch (error) {
            console.error('Failed to verify outbreak:', error);
        }
    };

    const getSeverityColor = (severity: string) => {
        const colors = {
            severe: 'bg-red-100 text-red-800 border-red-300',
            moderate: 'bg-amber-100 text-amber-800 border-amber-300',
            mild: 'bg-green-100 text-green-800 border-green-300'
        };
        return colors[severity as keyof typeof colors] || 'bg-gray-100 text-gray-800';
    };

    const [showReportModal, setShowReportModal] = useState(false);
    const [newReport, setNewReport] = useState({
        hospitalName: '',
        diseaseType: 'Viral Fever',
        patientCount: 0,
        severity: 'moderate',
        lat: 19.0760,
        lng: 72.8777
    });

    const handleReportSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            // Get token if configured, assuming simple setup for now or public endpoint if verified
            const token = localStorage.getItem('token');
            const headers = token ? { Authorization: `Bearer ${token}` } : {};

            await axios.post(`${API_BASE_URL}/outbreaks/`, {
                hospital_id: "manual-entry",
                hospital_name: newReport.hospitalName,
                disease_type: newReport.diseaseType,
                patient_count: Number(newReport.patientCount),
                severity: newReport.severity,
                date_started: new Date().toISOString(), // Required by backend
                location: { lat: newReport.lat, lng: newReport.lng }
            }, { headers });

            setShowReportModal(false);
            loadOutbreaks();
            alert("Outbreak reported successfully!");
        } catch (error) {
            console.error("Failed to submit report:", error);
            alert("Failed to submit report. Please try again.");
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="bg-white rounded-lg shadow-sm p-6 mb-6 flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Dashboard</h1>
                        <p className="text-gray-600">Manage outbreaks, verify reports, and monitor system activity</p>
                    </div>
                    <button
                        onClick={() => setShowReportModal(true)}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-medium flex items-center shadow-sm"
                    >
                        <span className="mr-2 text-xl">+</span> Report New Outbreak
                    </button>
                </div>

                {/* Report Modal */}
                {showReportModal && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                        <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl">
                            <h2 className="text-xl font-bold mb-4">Report New Outbreak</h2>
                            <form onSubmit={handleReportSubmit} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Hospital Name</label>
                                    <input
                                        type="text"
                                        required
                                        className="mt-1 w-full border border-gray-300 rounded-md p-2"
                                        value={newReport.hospitalName}
                                        onChange={e => setNewReport({ ...newReport, hospitalName: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Disease Type</label>
                                    <select
                                        className="mt-1 w-full border border-gray-300 rounded-md p-2"
                                        value={newReport.diseaseType}
                                        onChange={e => setNewReport({ ...newReport, diseaseType: e.target.value })}
                                    >
                                        <option value="Viral Fever">Viral Fever</option>
                                        <option value="Dengue">Dengue</option>
                                        <option value="Malaria">Malaria</option>
                                        <option value="Covid-19">Covid-19</option>
                                        <option value="Flu">Flu</option>
                                    </select>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Patient Count</label>
                                        <input
                                            type="number"
                                            required
                                            min="1"
                                            className="mt-1 w-full border border-gray-300 rounded-md p-2"
                                            value={newReport.patientCount}
                                            onChange={e => setNewReport({ ...newReport, patientCount: Number(e.target.value) })}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Severity</label>
                                        <select
                                            className="mt-1 w-full border border-gray-300 rounded-md p-2"
                                            value={newReport.severity}
                                            onChange={e => setNewReport({ ...newReport, severity: e.target.value })}
                                        >
                                            <option value="mild">Mild</option>
                                            <option value="moderate">Moderate</option>
                                            <option value="severe">Severe</option>
                                            <option value="critical">Critical</option>
                                        </select>
                                    </div>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Latitude</label>
                                        <input
                                            type="number"
                                            step="0.0001"
                                            className="mt-1 w-full border border-gray-300 rounded-md p-2"
                                            value={newReport.lat}
                                            onChange={e => setNewReport({ ...newReport, lat: Number(e.target.value) })}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">Longitude</label>
                                        <input
                                            type="number"
                                            step="0.0001"
                                            className="mt-1 w-full border border-gray-300 rounded-md p-2"
                                            value={newReport.lng}
                                            onChange={e => setNewReport({ ...newReport, lng: Number(e.target.value) })}
                                        />
                                    </div>
                                </div>
                                <div className="flex justify-end gap-3 mt-6">
                                    <button
                                        type="button"
                                        onClick={() => setShowReportModal(false)}
                                        className="px-4 py-2 text-gray-600 hover:text-gray-800"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                                    >
                                        Submit Report
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-white p-4 rounded-lg shadow-sm">
                        <div className="text-sm text-gray-600">Total Outbreaks</div>
                        <div className="text-2xl font-bold text-gray-900">{outbreaks.length}</div>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow-sm">
                        <div className="text-sm text-gray-600">Pending Verification</div>
                        <div className="text-2xl font-bold text-amber-600">
                            {outbreaks.filter(o => !o.verified).length}
                        </div>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow-sm">
                        <div className="text-sm text-gray-600">Critical Severity</div>
                        <div className="text-2xl font-bold text-red-600">
                            {outbreaks.filter(o => o.severity === 'severe').length}
                        </div>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow-sm">
                        <div className="text-sm text-gray-600">Total Cases</div>
                        <div className="text-2xl font-bold text-gray-900">
                            {outbreaks.reduce((sum, o) => sum + o.patient_count, 0)}
                        </div>
                    </div>
                </div>

                {/* Filters */}
                <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
                    <div className="flex gap-4">
                        <select
                            value={filter.severity}
                            onChange={(e) => setFilter({ ...filter, severity: e.target.value })}
                            className="border border-gray-300 rounded px-3 py-2"
                        >
                            <option value="all">All Severities</option>
                            <option value="severe">Severe</option>
                            <option value="moderate">Moderate</option>
                            <option value="mild">Mild</option>
                        </select>

                        <select
                            value={filter.verified}
                            onChange={(e) => setFilter({ ...filter, verified: e.target.value })}
                            className="border border-gray-300 rounded px-3 py-2"
                        >
                            <option value="all">All Status</option>
                            <option value="true">Verified</option>
                            <option value="false">Pending</option>
                        </select>

                        <input
                            type="text"
                            placeholder="Filter by disease..."
                            value={filter.disease}
                            onChange={(e) => setFilter({ ...filter, disease: e.target.value })}
                            className="border border-gray-300 rounded px-3 py-2 flex-1"
                        />
                    </div>
                </div>

                {/* Outbreaks Table */}
                <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Hospital</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Disease</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cases</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {loading ? (
                                <tr>
                                    <td colSpan={7} className="px-6 py-4 text-center text-gray-500">
                                        Loading...
                                    </td>
                                </tr>
                            ) : outbreaks.length === 0 ? (
                                <tr>
                                    <td colSpan={7} className="px-6 py-4 text-center text-gray-500">
                                        No outbreaks found
                                    </td>
                                </tr>
                            ) : (
                                outbreaks.map((outbreak) => (
                                    <tr key={outbreak.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 text-sm text-gray-900">{outbreak.hospital.name}</td>
                                        <td className="px-6 py-4 text-sm text-gray-900">{outbreak.disease_type}</td>
                                        <td className="px-6 py-4 text-sm text-gray-900">{outbreak.patient_count}</td>
                                        <td className="px-6 py-4">
                                            <span className={`px-2 py-1 text-xs rounded border ${getSeverityColor(outbreak.severity)}`}>
                                                {outbreak.severity}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            {outbreak.verified ? (
                                                <span className="text-green-600 text-sm">✓ Verified</span>
                                            ) : (
                                                <span className="text-amber-600 text-sm">⚠ Pending</span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-500">
                                            {new Date(outbreak.date_reported).toLocaleDateString()}
                                        </td>
                                        <td className="px-6 py-4">
                                            {!outbreak.verified && (
                                                <button
                                                    onClick={() => verifyOutbreak(outbreak.id)}
                                                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                                                >
                                                    Verify
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
