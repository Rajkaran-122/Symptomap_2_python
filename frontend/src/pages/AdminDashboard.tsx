import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import {
    Activity, ShieldCheck, AlertTriangle, Search,
    Clock, Plus, X,
    Eye, LayoutDashboard, Radio, Bell
} from 'lucide-react';
import { API_BASE_URL } from '../config/api';

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
        setLoading(true);
        try {
            const token = localStorage.getItem('symptomap_access_token') || localStorage.getItem('access_token');
            const response = await axios.get(`${API_BASE_URL}/outbreaks/all?days=30`, {
                headers: token ? { 'Authorization': `Bearer ${token}` } : {}
            });
            const data = response.data.outbreaks || [];
            const transformed = data.map((o: any) => ({
                id: o.id,
                hospital: { name: o.location?.name || o.disease || 'Unknown', location: { lat: o.location?.latitude || 0, lng: o.location?.longitude || 0 } },
                disease_type: o.disease || 'Unknown',
                patient_count: o.cases || 0,
                severity: o.severity || 'moderate',
                verified: o.verified || false,
                date_reported: o.reported_date || new Date().toISOString()
            }));

            // Apply local filters since backend /all implementation is simple
            let filtered = transformed;
            if (filter.severity !== 'all') filtered = filtered.filter((o: Outbreak) => o.severity === filter.severity);
            if (filter.verified !== 'all') filtered = filtered.filter((o: Outbreak) => String(o.verified) === filter.verified);
            if (filter.disease) filtered = filtered.filter((o: Outbreak) => o.disease_type.toLowerCase().includes(filter.disease.toLowerCase()));

            setOutbreaks(filtered);
        } catch (error) {
            console.error('Failed to load outbreaks:', error);
        } finally {
            setLoading(false);
        }
    };

    const verifyOutbreak = async (outbreakId: string) => {
        try {
            await axios.post(`${API_BASE_URL}/outbreaks/${outbreakId}/verify-public`, {});
            loadOutbreaks();
        } catch (error) {
            console.error('Failed to verify outbreak:', error);
            alert('Failed to verify outbreak. Please try again.');
        }
    };

    const getSeverityStyles = (severity: string) => {
        const styles: any = {
            severe: 'bg-red-500/10 text-red-500 border-red-500/20 shadow-[0_0_15px_rgba(239,68,68,0.1)]',
            moderate: 'bg-amber-500/10 text-amber-500 border-amber-500/20 shadow-[0_0_15px_rgba(245,158,11,0.1)]',
            mild: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.1)]'
        };
        return styles[severity] || 'bg-slate-500/10 text-slate-500 border-slate-500/20';
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
            const token = localStorage.getItem('access_token');
            const headers = token ? { Authorization: `Bearer ${token}` } : {};

            await axios.post(`${API_BASE_URL}/outbreaks/`, {
                hospital_id: "manual-entry",
                hospital_name: newReport.hospitalName,
                disease_type: newReport.diseaseType,
                patient_count: Number(newReport.patientCount),
                severity: newReport.severity,
                date_started: new Date().toISOString(),
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
        <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-indigo-100 selection:text-indigo-900">
            {/* Professional Header - Enterprise Grade */}
            <header className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-sm backdrop-blur-xl bg-white/80 supports-[backdrop-filter]:bg-white/80">
                <div className="max-w-7xl mx-auto px-6 sm:px-8 py-4">
                    <div className="flex flex-col lg:flex-row justify-between items-center gap-4">
                        <div className="flex items-center gap-4">
                            <div className="bg-indigo-600 text-white p-2.5 rounded-xl shadow-lg shadow-indigo-600/20">
                                <LayoutDashboard className="w-6 h-6" />
                            </div>
                            <div>
                                <h1 className="text-xl font-bold text-slate-900 tracking-tight">Admin Console</h1>
                                <p className="text-sm text-slate-500 font-medium">SymptoMap Intelligence Unit</p>
                            </div>
                        </div>

                        <div className="flex items-center gap-3">
                            <Link to="/admin/approvals" className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50 hover:border-slate-300 transition-all text-sm font-semibold shadow-sm hover:shadow">
                                <ShieldCheck className="w-4 h-4 text-emerald-500" />
                                <span>Verifications</span>
                            </Link>
                            <Link to="/admin/broadcasts" className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50 hover:border-slate-300 transition-all text-sm font-semibold shadow-sm hover:shadow">
                                <Radio className="w-4 h-4 text-indigo-500" />
                                <span>Broadcasts</span>
                            </Link>
                            <button
                                onClick={() => setShowReportModal(true)}
                                className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-lg font-semibold transition-all shadow-md shadow-indigo-600/20 active:scale-95"
                            >
                                <Plus className="w-4 h-4" />
                                <span>New Report</span>
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-6 sm:px-8 py-8">
                {/* Analytics Overview Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
                    {[
                        { label: 'Total Reports', value: outbreaks.length, icon: Activity, color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-100' },
                        { label: 'Pending Review', value: outbreaks.filter(o => !o.verified).length, icon: Clock, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-100' },
                        { label: 'High Priority', value: outbreaks.filter(o => o.severity === 'severe').length, icon: AlertTriangle, color: 'text-rose-600', bg: 'bg-rose-50', border: 'border-rose-100' },
                        { label: 'Active Cases', value: outbreaks.reduce((sum, o) => sum + o.patient_count, 0), icon: Bell, color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-100' },
                    ].map((stat, i) => (
                        <div key={i} className={`bg-white border border-slate-200 p-5 rounded-xl shadow-[0_2px_10px_-4px_rgba(6,81,237,0.1)] hover:shadow-lg transition-all duration-300 group`}>
                            <div className="flex justify-between items-start mb-4">
                                <div className={`p-2.5 rounded-lg ${stat.bg} ${stat.border} border`}>
                                    <stat.icon className={`w-5 h-5 ${stat.color}`} />
                                </div>
                                <span className="flex items-center gap-1.5 text-xs font-semibold text-slate-400 bg-slate-50 px-2.5 py-1 rounded-full border border-slate-100">
                                    <span className="relative flex h-2 w-2">
                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-slate-400 opacity-75"></span>
                                        <span className="relative inline-flex rounded-full h-2 w-2 bg-slate-500"></span>
                                    </span>
                                    LIVE
                                </span>
                            </div>
                            <div className="text-3xl font-bold text-slate-800 tracking-tight mb-1">{loading ? '...' : stat.value}</div>
                            <div className="text-sm text-slate-500 font-medium">{stat.label}</div>
                        </div>
                    ))}
                </div>

                {/* Filters & Actions Toolbar */}
                <div className="bg-white border border-slate-200 p-4 rounded-xl shadow-sm mb-6 flex flex-col sm:flex-row gap-4 items-center justify-between">
                    <div className="relative w-full sm:w-96">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <Search className="h-4 w-4 text-slate-400" />
                        </div>
                        <input
                            type="text"
                            placeholder="Search by disease or hospital..."
                            className="pl-10 pr-4 py-2.5 w-full bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 focus:bg-white focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all outline-none"
                            value={filter.disease}
                            onChange={(e) => setFilter({ ...filter, disease: e.target.value })}
                        />
                    </div>

                    <div className="flex items-center gap-3 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
                        <select
                            value={filter.severity}
                            onChange={(e) => setFilter({ ...filter, severity: e.target.value })}
                            className="px-3 py-2.5 bg-white border border-slate-200 rounded-lg text-sm text-slate-600 font-medium hover:border-slate-300 focus:ring-2 focus:ring-indigo-500/20 outline-none cursor-pointer transition-all"
                        >
                            <option value="all">All Severities</option>
                            <option value="severe">Severe</option>
                            <option value="moderate">Moderate</option>
                            <option value="mild">Mild</option>
                        </select>

                        <select
                            value={filter.verified}
                            onChange={(e) => setFilter({ ...filter, verified: e.target.value })}
                            className="px-3 py-2.5 bg-white border border-slate-200 rounded-lg text-sm text-slate-600 font-medium hover:border-slate-300 focus:ring-2 focus:ring-indigo-500/20 outline-none cursor-pointer transition-all"
                        >
                            <option value="all">All Statuses</option>
                            <option value="true">Verified</option>
                            <option value="false">Pending Audit</option>
                        </select>

                        <button
                            onClick={loadOutbreaks}
                            className="p-2.5 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors border border-transparent hover:border-indigo-100"
                            title="Refresh Data"
                        >
                            <Activity className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Data Datagrid */}
                <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-slate-50/50 border-b border-slate-200">
                                    <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Hospital / Source</th>
                                    <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Disease Profile</th>
                                    <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-center">Impact</th>
                                    <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-center">Severity</th>
                                    <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Verification</th>
                                    <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {loading ? (
                                    <tr>
                                        <td colSpan={6} className="px-6 py-16 text-center">
                                            <div className="flex flex-col items-center">
                                                <div className="w-10 h-10 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin mb-3"></div>
                                                <p className="text-slate-500 text-sm font-medium">Updating satellite feed...</p>
                                            </div>
                                        </td>
                                    </tr>
                                ) : outbreaks.length === 0 ? (
                                    <tr>
                                        <td colSpan={6} className="px-6 py-16 text-center">
                                            <div className="bg-slate-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                                                <Search className="w-8 h-8 text-slate-400" />
                                            </div>
                                            <p className="text-slate-900 font-semibold mb-1">No reports found</p>
                                            <p className="text-slate-500 text-sm">Adjust filters to broaden your search</p>
                                        </td>
                                    </tr>
                                ) : (
                                    outbreaks.map((o) => (
                                        <tr key={o.id} className="group hover:bg-slate-50/80 transition-colors">
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-8 h-8 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-600 font-bold text-xs ring-4 ring-white shadow-sm">
                                                        {o.hospital.name.charAt(0)}
                                                    </div>
                                                    <div>
                                                        <div className="text-slate-900 font-semibold text-sm">{o.hospital.name}</div>
                                                        <div className="text-slate-400 text-xs font-mono">#{o.id.substring(0, 6)}</div>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="text-slate-700 font-medium text-sm">{o.disease_type}</div>
                                                <div className="flex items-center gap-1.5 text-slate-500 text-xs mt-0.5">
                                                    <Clock className="w-3 h-3" />
                                                    {new Date(o.date_reported).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 text-center">
                                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800">
                                                    {o.patient_count} cases
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex justify-center">
                                                    <span className={`px-2.5 py-1 rounded-md text-xs font-semibold uppercase tracking-wide border ${getSeverityStyles(o.severity)}`}>
                                                        {o.severity}
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                {o.verified ? (
                                                    <div className="flex items-center gap-1.5 text-emerald-600 text-sm font-medium">
                                                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
                                                        Verified
                                                    </div>
                                                ) : (
                                                    <div className="flex items-center gap-1.5 text-amber-600 text-sm font-medium">
                                                        <div className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></div>
                                                        Pending
                                                    </div>
                                                )}
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                    <button
                                                        onClick={() => window.open(`/outbreak/${o.id}`, '_blank')}
                                                        className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all"
                                                        title="View Details"
                                                    >
                                                        <Eye className="w-4 h-4" />
                                                    </button>
                                                    {!o.verified && (
                                                        <button
                                                            onClick={() => verifyOutbreak(o.id)}
                                                            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-all"
                                                        >
                                                            Verify
                                                        </button>
                                                    )}
                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                    {/* Pagination or Footer area could go here */}
                    <div className="bg-slate-50 border-t border-slate-200 px-6 py-3 text-xs text-slate-500 text-right">
                        Showing {outbreaks.length} records
                    </div>
                </div>
            </main>

            {/* Premium Modal */}
            {showReportModal && (
                <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200 border border-slate-100">
                        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                            <div>
                                <h2 className="text-lg font-bold text-slate-900">New Outbreak Report</h2>
                                <p className="text-xs text-slate-500">Enter verifying details for the new case</p>
                            </div>
                            <button onClick={() => setShowReportModal(false)} className="p-1 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors">
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <form onSubmit={handleReportSubmit} className="p-6 space-y-5">
                            <div>
                                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">Hospital Name</label>
                                <input
                                    type="text"
                                    required
                                    className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-lg text-slate-900 text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all outline-none"
                                    placeholder="e.g. Memorial City Hospital"
                                    value={newReport.hospitalName}
                                    onChange={e => setNewReport({ ...newReport, hospitalName: e.target.value })}
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">Disease Type</label>
                                    <div className="relative">
                                        <select
                                            className="w-full appearance-none px-4 py-2.5 bg-white border border-slate-200 rounded-lg text-slate-900 text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all outline-none"
                                            value={newReport.diseaseType}
                                            onChange={e => setNewReport({ ...newReport, diseaseType: e.target.value })}
                                        >
                                            <option value="Viral Fever">Viral Fever</option>
                                            <option value="Dengue">Dengue</option>
                                            <option value="Malaria">Malaria</option>
                                            <option value="COVID-19">COVID-19</option>
                                        </select>
                                        <div className="absolute inset-y-0 right-3 flex items-center pointer-events-none text-slate-400">
                                            <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20"><path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" /></svg>
                                        </div>
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">Severity Level</label>
                                    <div className="relative">
                                        <select
                                            className="w-full appearance-none px-4 py-2.5 bg-white border border-slate-200 rounded-lg text-slate-900 text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all outline-none"
                                            value={newReport.severity}
                                            onChange={e => setNewReport({ ...newReport, severity: e.target.value })}
                                        >
                                            <option value="mild">Mild</option>
                                            <option value="moderate">Moderate</option>
                                            <option value="severe">Severe</option>
                                            <option value="critical">Critical</option>
                                        </select>
                                        <div className="absolute inset-y-0 right-3 flex items-center pointer-events-none text-slate-400">
                                            <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20"><path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" /></svg>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">Confirmed Cases</label>
                                <input
                                    type="number"
                                    required min="1"
                                    className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-lg text-slate-900 text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all outline-none"
                                    value={newReport.patientCount}
                                    onChange={e => setNewReport({ ...newReport, patientCount: Number(e.target.value) })}
                                />
                            </div>

                            <div className="flex justify-end gap-3 pt-4 border-t border-slate-100 mt-6">
                                <button type="button" onClick={() => setShowReportModal(false)} className="px-4 py-2 text-slate-600 hover:text-slate-800 font-medium text-sm transition-colors">
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg font-semibold text-sm shadow-md shadow-indigo-600/20 transition-all active:scale-95"
                                >
                                    Submit Report
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminDashboard;
