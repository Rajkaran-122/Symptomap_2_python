import { useState, useEffect } from 'react';
import { Activity, CheckCircle, XCircle, AlertTriangle, Bell, Clock } from 'lucide-react';

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
                const response = await fetch('http://localhost:8000/api/v1/analytics/activity-feed');
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
        const interval = setInterval(fetchActivities, 60000); // Refresh every minute
        return () => clearInterval(interval);
    }, [limit]);

    const getIcon = (icon: string, color: string) => {
        const colorClass = {
            green: 'text-green-500 bg-green-50',
            red: 'text-red-500 bg-red-50',
            yellow: 'text-yellow-500 bg-yellow-50',
            blue: 'text-blue-500 bg-blue-50'
        }[color] || 'text-gray-500 bg-gray-50';

        const IconComponent = {
            check: CheckCircle,
            x: XCircle,
            alert: AlertTriangle,
            bell: Bell
        }[icon] || Activity;

        return (
            <div className={`p-2 rounded-full ${colorClass}`}>
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
        const colors = {
            severe: 'bg-red-100 text-red-700',
            critical: 'bg-red-100 text-red-700',
            moderate: 'bg-orange-100 text-orange-700',
            mild: 'bg-green-100 text-green-700'
        };
        return (
            <span className={`px-2 py-0.5 rounded text-xs ${colors[severity as keyof typeof colors] || 'bg-gray-100'}`}>
                {severity}
            </span>
        );
    };

    if (loading) {
        return (
            <div className={`bg-white rounded-xl shadow-sm border p-4 ${className}`}>
                <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <Activity className="w-5 h-5 text-blue-500" />
                    Activity Feed
                </h3>
                <div className="space-y-3">
                    {[1, 2, 3, 4].map(i => (
                        <div key={i} className="animate-pulse flex items-center gap-3">
                            <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
                            <div className="flex-1">
                                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                                <div className="h-3 bg-gray-100 rounded w-1/2"></div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className={`bg-white rounded-xl shadow-sm border p-4 ${className}`}>
            <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5 text-blue-500" />
                Activity Feed
                <span className="ml-auto text-xs text-gray-400 font-normal">Live</span>
            </h3>

            {activities.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                    <Clock className="w-8 h-8 mx-auto mb-2" />
                    <p className="text-sm">No recent activity</p>
                </div>
            ) : (
                <div className="space-y-3">
                    {activities.map((activity) => (
                        <div key={activity.id} className="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors">
                            {getIcon(activity.icon, activity.color)}
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-800 truncate">
                                    {activity.action}
                                </p>
                                <div className="flex items-center gap-2 mt-1">
                                    {activity.disease && (
                                        <span className="text-xs text-gray-600">{activity.disease}</span>
                                    )}
                                    {getSeverityBadge(activity.severity)}
                                </div>
                                {activity.location && (
                                    <p className="text-xs text-gray-400 truncate mt-1">{activity.location}</p>
                                )}
                            </div>
                            <span className="text-xs text-gray-400 whitespace-nowrap">
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
