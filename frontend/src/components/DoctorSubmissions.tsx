import { useEffect, useState } from 'react';
import { MapPin, AlertTriangle, Clock } from 'lucide-react';

const DoctorSubmissions = () => {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            try {
                const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';
                const response = await fetch(`${API_URL}/outbreaks/all`);
                const result = await response.json();
                setData(result);
            } catch (error) {
                console.error('Failed to load doctor submissions:', error);
            } finally {
                setLoading(false);
            }
        };

        loadData();
        const interval = setInterval(loadData, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                <div className="animate-pulse">
                    <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
                    <div className="space-y-3">
                        <div className="h-16 bg-gray-100 rounded"></div>
                        <div className="h-16 bg-gray-100 rounded"></div>
                    </div>
                </div>
            </div>
        );
    }

    if (!data || (data.outbreaks.length === 0 && data.alerts.length === 0)) {
        return null;
    }

    return (
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-900">Recent Doctor Submissions</h3>
                <span className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded-full">
                    Live Updates
                </span>
            </div>

            <div className="space-y-3">
                {/* Outbreaks */}
                {data.outbreaks.slice(0, 3).map((outbreak: any) => (
                    <div key={outbreak.id} className="p-4 bg-gradient-to-r from-red-50 to-orange-50 rounded-xl border border-red-100 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between">
                            <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                    <MapPin className="w-4 h-4 text-red-600" />
                                    <span className="font-semibold text-gray-900">{outbreak.disease}</span>
                                    <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${outbreak.severity === 'severe' ? 'bg-red-100 text-red-700' :
                                            outbreak.severity === 'moderate' ? 'bg-orange-100 text-orange-700' :
                                                'bg-yellow-100 text-yellow-700'
                                        }`}>
                                        {outbreak.severity}
                                    </span>
                                </div>
                                <p className="text-sm text-gray-700">
                                    <strong>{outbreak.cases} cases</strong> reported in {outbreak.location.city}, {outbreak.location.state}
                                </p>
                                <p className="text-xs text-gray-500 mt-1">
                                    📍 {outbreak.location.name}
                                </p>
                                {outbreak.description && (
                                    <p className="text-xs text-gray-600 mt-2 italic">"{outbreak.description}"</p>
                                )}
                            </div>
                            <div className="text-right">
                                <span className="text-xs text-gray-500">Just now</span>
                            </div>
                        </div>
                    </div>
                ))}

                {/* Alerts */}
                {data.alerts.slice(0, 2).map((alert: any) => (
                    <div key={alert.id} className="p-4 bg-gradient-to-r from-amber-50 to-yellow-50 rounded-xl border border-amber-100 hover:shadow-md transition-shadow">
                        <div className="flex items-start gap-3">
                            <AlertTriangle className={`w-5 h-5 flex-shrink-0 mt-0.5 ${alert.type === 'critical' ? 'text-red-600' :
                                    alert.type === 'warning' ? 'text-orange-600' :
                                        'text-blue-600'
                                }`} />
                            <div className="flex-1">
                                <h4 className="font-semibold text-gray-900 mb-1">{alert.title}</h4>
                                <p className="text-sm text-gray-700">{alert.message}</p>
                                <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                                    <Clock className="w-3 h-3" />
                                    <span>Active until {new Date(alert.expiry).toLocaleDateString()}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {data.outbreaks.length + data.alerts.length > 5 && (
                <div className="mt-4 pt-4 border-t border-gray-200 text-center">
                    <p className="text-sm text-gray-500">
                        +{data.outbreaks.length + data.alerts.length - 5} more submissions
                    </p>
                </div>
            )}
        </div>
    );
};

export default DoctorSubmissions;
