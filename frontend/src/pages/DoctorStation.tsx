import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, MapPin, AlertTriangle, FileText, LogOut, CheckCircle } from 'lucide-react';
import OutbreakForm from '../components/doctor/OutbreakForm';
import AlertForm from '../components/doctor/AlertForm';
import { API_BASE_URL } from '../config/api';

type Tab = 'outbreak' | 'alert' | 'submissions';

const DoctorStation = () => {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState<Tab>('outbreak');
    const [stats, setStats] = useState({ total_submissions: 0, outbreak_reports: 0, active_alerts: 0 });
    const [submissions, setSubmissions] = useState<any>(null);

    useEffect(() => {
        // Check authentication
        const token = localStorage.getItem('doctor_token');
        const expiry = localStorage.getItem('doctor_token_expiry');

        if (!token || !expiry || Date.now() > parseInt(expiry)) {
            navigate('/doctor');
            return;
        }

        // Load stats
        loadStats();
        if (activeTab === 'submissions') {
            loadSubmissions();
        }
    }, [activeTab, navigate]);

    const getAuthHeaders = () => {
        const token = localStorage.getItem('doctor_token');
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    };

    const loadStats = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/doctor/stats`, {
                headers: getAuthHeaders()
            });
            const data = await response.json();
            setStats(data);
        } catch (err) {
            console.error('Failed to load stats:', err);
        }
    };

    const loadSubmissions = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/doctor/submissions`, {
                headers: getAuthHeaders()
            });
            const data = await response.json();
            setSubmissions(data);
        } catch (err) {
            console.error('Failed to load submissions:', err);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('doctor_token');
        localStorage.removeItem('doctor_token_expiry');
        navigate('/doctor');
    };

    const handleSubmissionSuccess = () => {
        loadStats();
        if (activeTab === 'submissions') {
            loadSubmissions();
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                                <Activity className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-xl font-bold text-gray-900">Doctor Station</h1>
                                <p className="text-sm text-gray-500">Submit outbreak reports & alerts</p>
                            </div>
                        </div>

                        <button
                            onClick={handleLogout}
                            className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                            <LogOut className="w-4 h-4" />
                            <span className="text-sm font-medium">Logout</span>
                        </button>
                    </div>
                </div>
            </header>

            {/* Stats Cards */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="bg-white rounded-lg p-6 border border-gray-200">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Total Submissions</p>
                                <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total_submissions}</p>
                            </div>
                            <FileText className="w-8 h-8 text-blue-500" />
                        </div>
                    </div>

                    <div className="bg-white rounded-lg p-6 border border-gray-200">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Outbreak Reports</p>
                                <p className="text-2xl font-bold text-gray-900 mt-1">{stats.outbreak_reports}</p>
                            </div>
                            <MapPin className="w-8 h-8 text-green-500" />
                        </div>
                    </div>

                    <div className="bg-white rounded-lg p-6 border border-gray-200">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Active Alerts</p>
                                <p className="text-2xl font-bold text-gray-900 mt-1">{stats.active_alerts}</p>
                            </div>
                            <AlertTriangle className="w-8 h-8 text-orange-500" />
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <div className="bg-white rounded-lg border border-gray-200">
                    <div className="border-b border-gray-200">
                        <nav className="flex -mb-px">
                            <button
                                onClick={() => setActiveTab('outbreak')}
                                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${activeTab === 'outbreak'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                <div className="flex items-center gap-2">
                                    <MapPin className="w-4 h-4" />
                                    Submit Outbreak
                                </div>
                            </button>

                            <button
                                onClick={() => setActiveTab('alert')}
                                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${activeTab === 'alert'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                <div className="flex items-center gap-2">
                                    <AlertTriangle className="w-4 h-4" />
                                    Create Alert
                                </div>
                            </button>

                            <button
                                onClick={() => setActiveTab('submissions')}
                                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${activeTab === 'submissions'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                <div className="flex items-center gap-2">
                                    <FileText className="w-4 h-4" />
                                    My Submissions
                                </div>
                            </button>
                        </nav>
                    </div>

                    {/* Tab Content */}
                    <div className="p-6">
                        {activeTab === 'outbreak' && <OutbreakForm onSuccess={handleSubmissionSuccess} />}
                        {activeTab === 'alert' && <AlertForm onSuccess={handleSubmissionSuccess} />}
                        {activeTab === 'submissions' && (
                            <div className="space-y-4">
                                {!submissions ? (
                                    <p className="text-gray-500 text-center py-8">Loading...</p>
                                ) : (
                                    <>
                                        <h3 className="text-lg font-semibold text-gray-900">Recent Outbreaks</h3>
                                        {submissions.outbreaks.length === 0 ? (
                                            <p className="text-gray-500 py-4">No outbreaks submitted yet.</p>
                                        ) : (
                                            <div className="space-y-2">
                                                {submissions.outbreaks.map((outbreak: any) => (
                                                    <div key={outbreak.id} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                                                        <div className="flex items-start justify-between">
                                                            <div>
                                                                <h4 className="font-medium text-gray-900">{outbreak.disease_type}</h4>
                                                                <p className="text-sm text-gray-600 mt-1">
                                                                    {outbreak.location_name} - {outbreak.patient_count} cases ({outbreak.severity})
                                                                </p>
                                                                <p className="text-xs text-gray-500 mt-1">
                                                                    {new Date(outbreak.created_at).toLocaleString()}
                                                                </p>
                                                            </div>
                                                            <CheckCircle className="w-5 h-5 text-green-500" />
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        )}

                                        <h3 className="text-lg font-semibold text-gray-900 mt-6">Active Alerts</h3>
                                        {submissions.alerts.length === 0 ? (
                                            <p className="text-gray-500 py-4">No alerts created yet.</p>
                                        ) : (
                                            <div className="space-y-2">
                                                {submissions.alerts.map((alert: any) => (
                                                    <div key={alert.id} className="p-4 bg-orange-50 rounded-lg border border-orange-200">
                                                        <div className="flex items-start justify-between">
                                                            <div>
                                                                <h4 className="font-medium text-gray-900">{alert.title}</h4>
                                                                <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                                                                <p className="text-xs text-gray-500 mt-1">
                                                                    {new Date(alert.created_at).toLocaleString()}
                                                                </p>
                                                            </div>
                                                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${alert.alert_type === 'critical' ? 'bg-red-100 text-red-700' :
                                                                alert.alert_type === 'warning' ? 'bg-orange-100 text-orange-700' :
                                                                    'bg-blue-100 text-blue-700'
                                                                }`}>
                                                                {alert.alert_type}
                                                            </span>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DoctorStation;
