import React, { useState, useEffect } from 'react';
import { Bell, X, Check, AlertTriangle, Info, AlertCircle, Trash2, Settings } from 'lucide-react';
import { UserPreferencesModal } from './UserPreferencesModal';

interface Notification {
    id: string;
    title: string;
    message: string;
    type: 'info' | 'warning' | 'error' | 'success';
    timestamp: string;
    read: boolean;
    data?: any;
}

interface NotificationCenterProps {
    isOpen: boolean;
    onClose: () => void;
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({ isOpen, onClose }) => {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [loading, setLoading] = useState(false);
    const [isPrefsOpen, setIsPrefsOpen] = useState(false);

    // Fetch real data from API
    useEffect(() => {
        if (isOpen) {
            const fetchNotifications = async () => {
                setLoading(true);
                try {
                    // Try to get token from localStorage if exists
                    const token = localStorage.getItem('symptomap_access_token') ||
                        localStorage.getItem('access_token') ||
                        localStorage.getItem('token');
                    const headers: HeadersInit = {
                        'Content-Type': 'application/json'
                    };
                    if (token) {
                        headers['Authorization'] = `Bearer ${token}`;
                    }

                    // Use relative path or centralized config if possible, but for now let's just ensure it's correct
                    const response = await fetch('/api/v1/broadcasts', {
                        headers
                    });

                    if (response.ok) {
                        const data = await response.json();
                        const mappedData = data.map((b: any) => ({
                            id: b.id,
                            title: b.title,
                            message: b.content,
                            type: b.severity === 'critical' || b.severity === 'emergency' ? 'error' :
                                b.severity === 'warning' ? 'warning' : 'info',
                            timestamp: b.created_at,
                            read: false // State managed locally for now
                        }));
                        setNotifications(mappedData);
                    }
                } catch (error) {
                    console.error('Failed to fetch notifications:', error);
                } finally {
                    setLoading(false);
                }
            };

            fetchNotifications();
        }
    }, [isOpen]);

    const markAsRead = (id: string) => {
        setNotifications(prev =>
            prev.map(n => n.id === id ? { ...n, read: true } : n)
        );
    };

    const deleteNotification = (id: string) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
    };

    const clearAll = () => {
        setNotifications([]);
    };

    const getIcon = (type: string) => {
        switch (type) {
            case 'error': return <AlertTriangle className="w-5 h-5 text-red-500" />;
            case 'warning': return <AlertCircle className="w-5 h-5 text-amber-500" />;
            case 'success': return <Check className="w-5 h-5 text-emerald-500" />;
            default: return <Info className="w-5 h-5 text-indigo-500" />;
        }
    };

    const formatTime = (isoString: string) => {
        const date = new Date(isoString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.round(diffMs / 60000);
        const diffHours = Math.round(diffMs / 3600000);
        const diffDays = Math.round(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays === 1) return 'Yesterday';
        return date.toLocaleDateString();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] overflow-hidden">
            <div className="absolute inset-0 bg-slate-900/10 backdrop-blur-sm transition-opacity" onClick={onClose} />
            <div className="absolute right-0 top-0 bottom-0 w-full max-w-sm bg-white shadow-2xl animate-in slide-in-from-right duration-500 border-l border-slate-100">
                <div className="flex flex-col h-full">
                    {/* Header */}
                    <div className="px-6 py-6 border-b border-slate-100 flex items-center justify-between bg-white">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center">
                                <Bell className="w-5 h-5 text-indigo-600" />
                            </div>
                            <div>
                                <h2 className="font-bold text-slate-900 text-lg tracking-tight">Health Alerts</h2>
                                <p className="text-[10px] uppercase tracking-widest text-slate-400 font-bold">
                                    {notifications.filter(n => !n.read).length} Unread Notifications
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center gap-1">
                            {notifications.length > 0 && (
                                <button
                                    onClick={clearAll}
                                    className="p-2 text-slate-400 hover:text-red-500 rounded-lg hover:bg-red-50 transition-all font-bold text-[10px] uppercase tracking-wider"
                                    title="Clear all"
                                >
                                    Clear
                                </button>
                            )}
                            <button
                                onClick={onClose}
                                className="p-2 text-slate-400 hover:text-slate-900 rounded-lg hover:bg-slate-50 transition-all"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                    {/* Content */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        {loading ? (
                            <div className="space-y-4">
                                {[1, 2, 3, 4].map(i => (
                                    <div key={i} className="animate-pulse flex gap-3 p-4 rounded-xl">
                                        <div className="w-10 h-10 bg-slate-100 rounded-full" />
                                        <div className="flex-1 space-y-3">
                                            <div className="h-4 bg-slate-100 rounded w-3/4" />
                                            <div className="h-3 bg-slate-100 rounded w-full" />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : notifications.length === 0 ? (
                            <div className="flex flex-col items-center justify-center h-full text-slate-300">
                                <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-6">
                                    <Bell className="w-10 h-10 opacity-20" />
                                </div>
                                <p className="text-sm font-bold uppercase tracking-widest">Awaiting Alerts</p>
                                <p className="text-xs mt-1">Systems are currently clear</p>
                            </div>
                        ) : (
                            notifications.map(notification => (
                                <div
                                    key={notification.id}
                                    className={`relative group p-5 rounded-2xl border transition-all duration-300 cursor-pointer ${notification.read
                                        ? 'bg-white border-slate-100 hover:bg-slate-50'
                                        : 'bg-indigo-50/30 border-indigo-100 shadow-sm shadow-indigo-500/5 hover:bg-indigo-50/50'
                                        }`}
                                    onClick={() => markAsRead(notification.id)}
                                >
                                    <div className="flex gap-4">
                                        <div className={`mt-0.5 flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center shadow-sm ${notification.type === 'error' ? 'bg-red-50' :
                                            notification.type === 'warning' ? 'bg-amber-50' :
                                                notification.type === 'success' ? 'bg-emerald-50' : 'bg-indigo-50'
                                            }`}>
                                            {getIcon(notification.type)}
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex justify-between items-start mb-1.5">
                                                <h3 className={`text-sm font-bold tracking-tight truncate ${notification.read ? 'text-slate-700' : 'text-slate-900'
                                                    }`}>
                                                    {notification.title}
                                                </h3>
                                                {!notification.read && (
                                                    <div className="w-2 h-2 bg-indigo-500 rounded-full mt-1.5 flex-shrink-0" />
                                                )}
                                            </div>
                                            <p className={`text-xs leading-relaxed mb-3 ${notification.read ? 'text-slate-400' : 'text-slate-600'
                                                }`}>
                                                {notification.message}
                                            </p>
                                            <div className="flex items-center justify-between">
                                                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                                                    {formatTime(notification.timestamp)}
                                                </span>
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        deleteNotification(notification.id);
                                                    }}
                                                    className="opacity-0 group-hover:opacity-100 p-1.5 text-slate-400 hover:text-red-500 transition-all"
                                                >
                                                    <Trash2 className="w-3.5 h-3.5" />
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>

                    {/* Footer */}
                    <div className="p-6 border-t border-slate-100 bg-white">
                        <button
                            onClick={() => setIsPrefsOpen(true)}
                            className="w-full py-4 text-xs text-indigo-600 hover:text-white font-black uppercase tracking-widest flex items-center justify-center gap-2 hover:bg-indigo-600 border border-indigo-100 hover:border-indigo-600 rounded-2xl transition-all shadow-lg shadow-indigo-100"
                        >
                            <Settings className="w-4 h-4" /> Alert Preferences
                        </button>
                    </div>
                </div>
            </div>

            <UserPreferencesModal
                isOpen={isPrefsOpen}
                onClose={() => setIsPrefsOpen(false)}
            />
        </div>
    );
};
