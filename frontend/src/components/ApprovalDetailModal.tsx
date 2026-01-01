import { X, MapPin, Users, AlertTriangle, CheckCircle, XCircle, Clock, Stethoscope } from 'lucide-react';

interface OutbreakData {
    id: number;
    disease_type: string;
    patient_count: number;
    severity: string;
    location_name: string;
    city: string;
    state: string;
    description: string;
    date_reported: string;
    status: string;
    doctor_name?: string;
}

interface ApprovalDetailModalProps {
    outbreak: OutbreakData | null;
    isOpen: boolean;
    onClose: () => void;
    onApprove: (id: number) => void;
    onReject: (id: number) => void;
    loading?: boolean;
}

const ApprovalDetailModal = ({
    outbreak,
    isOpen,
    onClose,
    onApprove,
    onReject,
    loading = false
}: ApprovalDetailModalProps) => {
    if (!isOpen || !outbreak) return null;

    const getSeverityColor = (severity: string) => {
        switch (severity?.toLowerCase()) {
            case 'severe': return 'from-red-500 to-rose-600 text-white';
            case 'moderate': return 'from-amber-500 to-orange-500 text-white';
            case 'mild': return 'from-emerald-500 to-green-500 text-white';
            default: return 'from-gray-500 to-gray-600 text-white';
        }
    };

    const formatDate = (dateStr: string) => {
        try {
            return new Date(dateStr).toLocaleDateString('en-IN', {
                day: 'numeric',
                month: 'long',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch {
            return dateStr;
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/50 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl mx-4 overflow-hidden animate-in fade-in zoom-in duration-200">
                {/* Header */}
                <div className="bg-gradient-to-r from-primary-600 to-indigo-600 p-6 text-white">
                    <button
                        onClick={onClose}
                        className="absolute top-4 right-4 p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>

                    <div className="flex items-start gap-4">
                        <div className="p-3 bg-white/10 rounded-xl">
                            <AlertTriangle className="w-8 h-8" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold mb-1">{outbreak.disease_type} Outbreak</h2>
                            <p className="text-primary-100 text-sm flex items-center gap-2">
                                <MapPin className="w-4 h-4" />
                                {outbreak.location_name}, {outbreak.city}, {outbreak.state}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6">
                    {/* Stats Grid */}
                    <div className="grid grid-cols-3 gap-4 mb-6">
                        <div className="bg-gray-50 rounded-xl p-4 text-center">
                            <Users className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                            <div className="text-2xl font-bold text-gray-900">{outbreak.patient_count}</div>
                            <div className="text-xs text-gray-500">Patients Affected</div>
                        </div>

                        <div className="bg-gray-50 rounded-xl p-4 text-center">
                            <div className={`inline-block px-3 py-1 rounded-full bg-gradient-to-r ${getSeverityColor(outbreak.severity)} text-sm font-bold mb-2`}>
                                {outbreak.severity?.toUpperCase()}
                            </div>
                            <div className="text-xs text-gray-500">Severity Level</div>
                        </div>

                        <div className="bg-gray-50 rounded-xl p-4 text-center">
                            <Clock className="w-6 h-6 text-purple-600 mx-auto mb-2" />
                            <div className="text-sm font-semibold text-gray-900">{formatDate(outbreak.date_reported)}</div>
                            <div className="text-xs text-gray-500">Date Reported</div>
                        </div>
                    </div>

                    {/* Description */}
                    <div className="mb-6">
                        <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                            <Stethoscope className="w-4 h-4" />
                            Clinical Description
                        </h4>
                        <p className="text-gray-600 bg-gray-50 p-4 rounded-xl text-sm leading-relaxed">
                            {outbreak.description || 'No additional description provided.'}
                        </p>
                    </div>

                    {/* Doctor Info */}
                    {outbreak.doctor_name && (
                        <div className="mb-6 flex items-center gap-3 p-4 bg-blue-50 rounded-xl">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold">
                                {outbreak.doctor_name.charAt(0)}
                            </div>
                            <div>
                                <div className="font-semibold text-gray-800">{outbreak.doctor_name}</div>
                                <div className="text-xs text-gray-500">Reporting Doctor</div>
                            </div>
                        </div>
                    )}

                    {/* Status */}
                    <div className="flex items-center gap-2 mb-6 p-3 bg-amber-50 rounded-xl">
                        <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
                        <span className="text-sm font-medium text-amber-700">
                            Status: {outbreak.status?.toUpperCase() || 'PENDING'}
                        </span>
                    </div>

                    {/* Actions */}
                    {outbreak.status === 'pending' && (
                        <div className="flex gap-3">
                            <button
                                onClick={() => onApprove(outbreak.id)}
                                disabled={loading}
                                className="flex-1 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white font-semibold flex items-center justify-center gap-2 transition-all disabled:opacity-50 shadow-lg"
                            >
                                <CheckCircle className="w-5 h-5" />
                                Approve Outbreak
                            </button>
                            <button
                                onClick={() => onReject(outbreak.id)}
                                disabled={loading}
                                className="flex-1 py-3 rounded-xl bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 text-white font-semibold flex items-center justify-center gap-2 transition-all disabled:opacity-50 shadow-lg"
                            >
                                <XCircle className="w-5 h-5" />
                                Reject Report
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ApprovalDetailModal;
