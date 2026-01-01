import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    CheckCircle, XCircle, Clock, AlertTriangle,
    RefreshCw, MapPin, Users, Activity, Eye
} from 'lucide-react';
import ApprovalDetailModal from '../components/ApprovalDetailModal';

interface PendingRequest {
    id: number;
    disease_type: string;
    patient_count: number;
    severity: string;
    latitude: number;
    longitude: number;
    location_name: string;
    city: string;
    state: string;
    description: string;
    date_reported: string;
    submitted_by: string;
    created_at: string;
    status: string;
}

const ApprovalRequestsPage = () => {
    const navigate = useNavigate();
    const [requests, setRequests] = useState<PendingRequest[]>([]);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState<number | null>(null);
    const [filter, setFilter] = useState<'all' | 'pending' | 'approved' | 'rejected'>('pending');
    const [successMessage, setSuccessMessage] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [selectedRequest, setSelectedRequest] = useState<PendingRequest | null>(null);

    // Check authentication
    useEffect(() => {
        const token = localStorage.getItem('doctor_token');
        if (!token) {
            navigate('/doctor');
        }
    }, [navigate]);

    const getAuthHeaders = () => {
        const token = localStorage.getItem('doctor_token');
        return {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    };

    const fetchRequests = async () => {
        setLoading(true);
        try {
            const endpoint = filter === 'pending'
                ? 'http://localhost:8000/api/v1/admin/pending'
                : 'http://localhost:8000/api/v1/admin/all-requests';

            const response = await fetch(endpoint, {
                headers: getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error('Failed to fetch requests');
            }

            const data = await response.json();

            if (filter === 'pending') {
                setRequests(data);
            } else {
                const filtered = filter === 'all'
                    ? data.requests
                    : data.requests.filter((r: PendingRequest) => r.status === filter);
                setRequests(filtered);
            }
        } catch (error) {
            console.error('Error fetching requests:', error);
            setErrorMessage('Failed to load requests');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRequests();
    }, [filter]);

    const handleApprove = async (id: number) => {
        setActionLoading(id);
        setErrorMessage('');

        try {
            const response = await fetch(`http://localhost:8000/api/v1/admin/approve/${id}`, {
                method: 'POST',
                headers: getAuthHeaders()
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to approve');
            }

            setSuccessMessage('Request approved and added to official dashboard!');
            fetchRequests();

            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (error: any) {
            setErrorMessage(error.message || 'Failed to approve request');
        } finally {
            setActionLoading(null);
        }
    };

    const handleReject = async (id: number) => {
        if (!confirm('Are you sure you want to reject this request?')) return;

        setActionLoading(id);
        setErrorMessage('');

        try {
            const response = await fetch(`http://localhost:8000/api/v1/admin/reject/${id}`, {
                method: 'POST',
                headers: getAuthHeaders()
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to reject');
            }

            setSuccessMessage('Request rejected');
            fetchRequests();

            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (error: any) {
            setErrorMessage(error.message || 'Failed to reject request');
        } finally {
            setActionLoading(null);
        }
    };

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'severe': return 'bg-red-100 text-red-700 border-red-200';
            case 'moderate': return 'bg-orange-100 text-orange-700 border-orange-200';
            case 'mild': return 'bg-green-100 text-green-700 border-green-200';
            default: return 'bg-gray-100 text-gray-700 border-gray-200';
        }
    };

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'approved':
                return <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs flex items-center gap-1">
                    <CheckCircle className="w-3 h-3" /> Approved
                </span>;
            case 'rejected':
                return <span className="px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs flex items-center gap-1">
                    <XCircle className="w-3 h-3" /> Rejected
                </span>;
            default:
                return <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs flex items-center gap-1">
                    <Clock className="w-3 h-3" /> Pending
                </span>;
        }
    };

    const formatDate = (dateStr: string) => {
        if (!dateStr) return 'N/A';
        try {
            return new Date(dateStr).toLocaleDateString('en-IN', {
                day: '2-digit',
                month: 'short',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch {
            return dateStr;
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-900 via-blue-800 to-blue-900 text-white py-8 px-6">
                <div className="max-w-7xl mx-auto">
                    <h1 className="text-3xl font-bold mb-2">Approval Requests</h1>
                    <p className="text-blue-200">Review and approve doctor submissions</p>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Success/Error Messages */}
                {successMessage && (
                    <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2 text-green-700">
                        <CheckCircle className="w-5 h-5" />
                        {successMessage}
                    </div>
                )}
                {errorMessage && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
                        <AlertTriangle className="w-5 h-5" />
                        {errorMessage}
                    </div>
                )}

                {/* Controls */}
                <div className="flex flex-wrap gap-4 mb-6 items-center justify-between">
                    <div className="flex gap-2">
                        {(['pending', 'approved', 'rejected', 'all'] as const).map((f) => (
                            <button
                                key={f}
                                onClick={() => setFilter(f)}
                                className={`px-4 py-2 rounded-lg font-medium transition-all ${filter === f
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-white text-gray-600 hover:bg-gray-100 border'
                                    }`}
                            >
                                {f.charAt(0).toUpperCase() + f.slice(1)}
                            </button>
                        ))}
                    </div>
                    <button
                        onClick={fetchRequests}
                        className="flex items-center gap-2 px-4 py-2 bg-white border rounded-lg hover:bg-gray-50 transition-all"
                    >
                        <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                        Refresh
                    </button>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-white rounded-xl p-4 shadow-sm border">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-yellow-100 rounded-lg">
                                <Clock className="w-5 h-5 text-yellow-600" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Pending</p>
                                <p className="text-xl font-bold">{requests.filter(r => r.status === 'pending' || !r.status).length}</p>
                            </div>
                        </div>
                    </div>
                    <div className="bg-white rounded-xl p-4 shadow-sm border">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-green-100 rounded-lg">
                                <CheckCircle className="w-5 h-5 text-green-600" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Approved</p>
                                <p className="text-xl font-bold">{requests.filter(r => r.status === 'approved').length}</p>
                            </div>
                        </div>
                    </div>
                    <div className="bg-white rounded-xl p-4 shadow-sm border">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-red-100 rounded-lg">
                                <XCircle className="w-5 h-5 text-red-600" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Rejected</p>
                                <p className="text-xl font-bold">{requests.filter(r => r.status === 'rejected').length}</p>
                            </div>
                        </div>
                    </div>
                    <div className="bg-white rounded-xl p-4 shadow-sm border">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-blue-100 rounded-lg">
                                <Activity className="w-5 h-5 text-blue-600" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Total</p>
                                <p className="text-xl font-bold">{requests.length}</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Table */}
                <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
                    {loading ? (
                        <div className="p-12 text-center text-gray-500">
                            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
                            Loading requests...
                        </div>
                    ) : requests.length === 0 ? (
                        <div className="p-12 text-center text-gray-500">
                            <Clock className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                            <p className="text-lg font-medium">No {filter} requests</p>
                            <p className="text-sm">Check back later for new submissions</p>
                        </div>
                    ) : (
                        <table className="w-full">
                            <thead className="bg-gray-50 border-b">
                                <tr>
                                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Disease</th>
                                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Location</th>
                                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Cases</th>
                                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Severity</th>
                                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Status</th>
                                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Submitted</th>
                                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y">
                                {requests.map((request) => (
                                    <tr key={request.id} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-4 py-4">
                                            <span className="font-medium text-gray-800">{request.disease_type}</span>
                                        </td>
                                        <td className="px-4 py-4">
                                            <div className="flex items-center gap-2">
                                                <MapPin className="w-4 h-4 text-gray-400" />
                                                <div>
                                                    <p className="text-sm font-medium text-gray-700">{request.location_name}</p>
                                                    <p className="text-xs text-gray-500">{request.city}, {request.state}</p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-4 py-4">
                                            <div className="flex items-center gap-1">
                                                <Users className="w-4 h-4 text-gray-400" />
                                                <span className="font-medium">{request.patient_count}</span>
                                            </div>
                                        </td>
                                        <td className="px-4 py-4">
                                            <span className={`px-2 py-1 rounded-full text-xs border ${getSeverityColor(request.severity)}`}>
                                                {request.severity}
                                            </span>
                                        </td>
                                        <td className="px-4 py-4">
                                            {getStatusBadge(request.status)}
                                        </td>
                                        <td className="px-4 py-4 text-sm text-gray-500">
                                            {formatDate(request.created_at)}
                                        </td>
                                        <td className="px-4 py-4">
                                            {(request.status === 'pending' || !request.status) && (
                                                <div className="flex gap-2">
                                                    <button
                                                        onClick={() => handleApprove(request.id)}
                                                        disabled={actionLoading === request.id}
                                                        className="flex items-center gap-1 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 text-sm"
                                                    >
                                                        {actionLoading === request.id ? (
                                                            <RefreshCw className="w-3 h-3 animate-spin" />
                                                        ) : (
                                                            <CheckCircle className="w-3 h-3" />
                                                        )}
                                                        Approve
                                                    </button>
                                                    <button
                                                        onClick={() => handleReject(request.id)}
                                                        disabled={actionLoading === request.id}
                                                        className="flex items-center gap-1 px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 text-sm"
                                                    >
                                                        <XCircle className="w-3 h-3" />
                                                        Reject
                                                    </button>
                                                </div>
                                            )}
                                            {request.status === 'approved' && (
                                                <span className="text-green-600 text-sm">✓ On Dashboard</span>
                                            )}
                                            {request.status === 'rejected' && (
                                                <span className="text-red-600 text-sm">Rejected</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>

                {/* Navigation */}
                <div className="mt-6 flex gap-4">
                    <button
                        onClick={() => navigate('/admin')}
                        className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                    >
                        ← Back to Admin
                    </button>
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        View Dashboard
                    </button>
                </div>
            </div>

            {/* Detail Modal */}
            <ApprovalDetailModal
                outbreak={selectedRequest}
                isOpen={!!selectedRequest}
                onClose={() => setSelectedRequest(null)}
                onApprove={(id) => {
                    handleApprove(id);
                    setSelectedRequest(null);
                }}
                onReject={(id) => {
                    handleReject(id);
                    setSelectedRequest(null);
                }}
                loading={actionLoading !== null}
            />
        </div>
    );
};

export default ApprovalRequestsPage;
