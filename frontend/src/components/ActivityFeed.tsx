import { useState, useEffect } from 'react';
import { Activity, CheckCircle, XCircle, AlertTriangle, Bell, Clock, Zap } from 'lucide-react';
import { API_BASE_URL } from '../config/api';

interface ActivityItem {
    id: string;
    type: string;
    action: string;
    disease?: string;
    location?: string;
    severity?: string;
    status: string;
    icon: string;
    color: string;
    time: string;
}

interface ActivityFeedProps {
    limit?: number;
    className?: string;
}

const ActivityFeed = ({ limit = 10, className = '' }: ActivityFeedProps) => {
    const [activities, setActivities] = useState<ActivityItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchActivities = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/analytics/activity-feed`);
                if (response.ok) {
                    const data = await response.json();
                    setActivities(data.activities.slice(0, limit));
                }
            } catch (error) {
                console.error('Error fetching activities:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchActivities();
        const interval = setInterval(fetchActivities, 60000);
        return () => clearInterval(interval);
    }, [limit]);

    const getIcon = (icon: string, color: string) => {
        const colorStyles = {
            green: 'text-emerald-600 bg-gradient-to-br from-emerald-100 to-green-100 shadow-emerald-200/50',
            red: 'text-red-600 bg-gradient-to-br from-red-100 to-rose-100 shadow-red-200/50',
            yellow: 'text-amber-600 bg-gradient-to-br from-amber-100 to-yellow-100 shadow-amber-200/50',
            blue: 'text-blue-600 bg-gradient-to-br from-blue-100 to-indigo-100 shadow-blue-200/50'
        }[color] || 'text-gray-600 bg-gradient-to-br from-gray-100 to-slate-100';

        const IconComponent = {
            check: CheckCircle,
            x: XCircle,
            alert: AlertTriangle,
            bell: Bell
        }[icon] || Activity;

        return (
            <div className={`p-2.5 rounded-xl shadow-lg ${colorStyles} transition-transform duration-300 group-hover:scale-110`}>
                <IconComponent className="w-4 h-4" />
            </div>
        );
    };

    const formatTime = (timeStr: string) => {
        if (!timeStr) return '';
        try {
            const date = new Date(timeStr);
            const now = new Date();
            const diffMs = now.getTime() - date.getTime();
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMins / 60);
            const diffDays = Math.floor(diffHours / 24);

            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins}m ago`;
            if (diffHours < 24) return `${diffHours}h ago`;
            if (diffDays < 7) return `${diffDays}d ago`;
            return date.toLocaleDateString();
        } catch {
            return timeStr;
        }
    };

    const getSeverityBadge = (severity?: string) => {
        if (!severity) return null;
        const styles = {
            severe: 'bg-gradient-to-r from-red-500 to-rose-500 text-white shadow-red-200',
            critical: 'bg-gradient-to-r from-red-600 to-red-500 text-white shadow-red-200',
            moderate: 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-amber-200',
            mild: 'bg-gradient-to-r from-emerald-500 to-green-500 text-white shadow-emerald-200'
        };
        return (
            <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider shadow-sm ${styles[severity as keyof typeof styles] || 'bg-gray-200'}`}>
                {severity}
            </span>
        );
    };

    if (loading) {
        return (
            <div className={`bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-white/20 p-6 ${className}`}>
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg shadow-blue-200">
                        <Activity className="w-5 h-5 text-white" />
                    </div>
                    <h3 className="font-bold text-gray-800 text-lg">Activity Feed</h3>
                </div>
                <div className="space-y-4">
                    {[1, 2, 3, 4].map(i => (
                        <div key={i} className="animate-pulse flex items-center gap-4">
                            <div className="w-11 h-11 bg-gradient-to-br from-gray-200 to-gray-300 rounded-xl"></div>
                            <div className="flex-1">
                                <div className="h-4 bg-gradient-to-r from-gray-200 to-gray-100 rounded-lg w-3/4 mb-2"></div>
                                <div className="h-3 bg-gray-100 rounded-lg w-1/2"></div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className={`bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-white/20 p-6 overflow-hidden relative ${className}`}>
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-br from-blue-500/10 to-indigo-500/5 rounded-full blur-3xl -z-10"></div>

            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg shadow-blue-300/50">
                        <Activity className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h3 className="font-bold text-gray-800 text-lg">Activity Feed</h3>
                        <p className="text-xs text-gray-400">Real-time updates</p>
                    </div>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-emerald-50 to-green-50 rounded-full border border-emerald-200">
                    <div className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </div>
                    <span className="text-xs font-semibold text-emerald-700">Live</span>
                </div>
            </div>

            {activities.length === 0 ? (
                <div className="text-center py-12">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                        <Clock className="w-8 h-8 text-gray-400" />
                    </div>
                    <p className="text-gray-500 font-medium">No recent activity</p>
                    <p className="text-xs text-gray-400 mt-1">Activities will appear here</p>
                </div>
            ) : (
                <div className="space-y-2">
                    {activities.map((activity, idx) => (
                        <div
                            key={activity.id}
                            className="group flex items-start gap-4 p-3 rounded-xl hover:bg-gradient-to-r hover:from-gray-50 hover:to-white transition-all duration-300 cursor-pointer border border-transparent hover:border-gray-100 hover:shadow-sm"
                            style={{ animationDelay: `${idx * 50}ms` }}
                        >
                            {getIcon(activity.icon, activity.color)}
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-semibold text-gray-800 truncate group-hover:text-blue-600 transition-colors">
                                    {activity.action}
                                </p>
                                <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                                    {activity.disease && (
                                        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-md">
                                            {activity.disease}
                                        </span>
                                    )}
                                    {getSeverityBadge(activity.severity)}
                                </div>
                                {activity.location && (
                                    <p className="text-xs text-gray-400 truncate mt-1 flex items-center gap-1">
                                        <Zap className="w-3 h-3" />
                                        {activity.location}
                                    </p>
                                )}
                            </div>
                            <span className="text-xs text-gray-400 whitespace-nowrap bg-gray-50 px-2 py-1 rounded-md font-medium">
                                {formatTime(activity.time)}
                            </span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default ActivityFeed;

