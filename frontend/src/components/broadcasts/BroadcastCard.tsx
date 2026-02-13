import React from 'react';
import { AlertTriangle, Info, AlertCircle, Clock, MapPin, ChevronDown, Zap, Shield } from 'lucide-react';

export interface Broadcast {
    id: string;
    title: string;
    content: string;
    severity: 'info' | 'warning' | 'critical' | 'emergency';
    region: string | null;
    channels: string[];
    created_at: string;
    expires_at: string | null;
    is_automated: boolean;
}

interface BroadcastCardProps {
    broadcast: Broadcast;
    isExpanded: boolean;
    onToggle: () => void;
}

const BroadcastCard: React.FC<BroadcastCardProps> = ({ broadcast, isExpanded, onToggle }) => {
    const getSeverityConfig = (severity: Broadcast['severity']) => {
        const configs = {
            info: {
                icon: Info,
                bg: 'bg-blue-50/50',
                hover: 'hover:bg-blue-50',
                border: 'border-blue-100',
                text: 'text-blue-600',
                iconBg: 'bg-white'
            },
            warning: {
                icon: AlertCircle,
                bg: 'bg-amber-50/50',
                hover: 'hover:bg-amber-50',
                border: 'border-amber-100',
                text: 'text-amber-600',
                iconBg: 'bg-white'
            },
            critical: {
                icon: AlertTriangle,
                bg: 'bg-red-50/50',
                hover: 'hover:bg-red-50',
                border: 'border-red-100',
                text: 'text-red-600',
                iconBg: 'bg-white'
            },
            emergency: {
                icon: Zap,
                bg: 'bg-rose-50/50',
                hover: 'hover:bg-rose-50',
                border: 'border-rose-100',
                text: 'text-rose-600',
                iconBg: 'bg-white'
            }
        };
        return configs[severity] || configs.info;
    };

    const formatTimeAgo = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now.getTime() - date.getTime();

        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        return `${days}d ago`;
    };

    const config = getSeverityConfig(broadcast.severity);
    const Icon = config.icon;

    return (
        <div
            className={`group relative ${config.bg} ${config.hover} border ${config.border} rounded-3xl overflow-hidden transition-all duration-300 shadow-sm hover:shadow-md`}
        >
            <button
                onClick={onToggle}
                className="w-full p-8 text-left"
            >
                <div className="flex items-start gap-6">
                    <div className={`w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0 ${config.iconBg} border border-slate-100 shadow-sm transition-transform group-hover:scale-110`}>
                        <Icon className={`w-7 h-7 ${config.text}`} />
                    </div>

                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-3">
                            <span className={`text-[10px] font-black uppercase tracking-widest px-2.5 py-1 rounded-full border ${config.border} ${config.text}`}>
                                {broadcast.severity}
                            </span>
                            {broadcast.is_automated && (
                                <span className="text-[10px] font-black uppercase tracking-widest bg-indigo-50 text-indigo-600 px-2.5 py-1 rounded-full border border-indigo-100 flex items-center gap-1">
                                    <Shield className="w-2.5 h-2.5" /> AI Verified
                                </span>
                            )}
                        </div>

                        <h3 className="text-xl font-black text-slate-900 mb-2 tracking-tight group-hover:text-indigo-600 transition-colors">
                            {broadcast.title}
                        </h3>

                        <p className={`text-slate-500 leading-relaxed text-sm ${isExpanded ? '' : 'line-clamp-2'}`}>
                            {broadcast.content}
                        </p>

                        <div className="flex items-center gap-6 mt-6 text-[11px] font-bold text-slate-400 uppercase tracking-widest">
                            <span className="flex items-center gap-2">
                                <Clock className="w-3.5 h-3.5 text-indigo-400" />
                                {formatTimeAgo(broadcast.created_at)}
                            </span>
                            {broadcast.region && (
                                <span className="flex items-center gap-2">
                                    <MapPin className="w-3.5 h-3.5 text-indigo-400" />
                                    {broadcast.region}
                                </span>
                            )}
                        </div>
                    </div>

                    <div className={`p-2 rounded-full border border-slate-100 bg-white transition-transform duration-300 ${isExpanded ? 'rotate-180 bg-slate-50' : ''}`}>
                        <ChevronDown className="w-5 h-5 text-slate-400" />
                    </div>
                </div>
            </button>
        </div>
    );
};

export default BroadcastCard;
