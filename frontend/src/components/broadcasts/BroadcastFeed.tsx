/**
 * Broadcast Feed - Premium Light Theme
 * Displays health announcements with sophisticated styling
 */

import React, { useState, useEffect } from 'react';
import { AlertTriangle, Radio, Filter } from 'lucide-react';
import BroadcastCard, { Broadcast } from './BroadcastCard';
import { API_BASE_URL } from '../../config/api';

interface BroadcastFeedProps {
    region?: string;
    limit?: number;
}

const BroadcastFeed: React.FC<BroadcastFeedProps> = ({ region, limit = 10 }) => {
    const [broadcasts, setBroadcasts] = useState<Broadcast[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [expandedId, setExpandedId] = useState<string | null>(null);
    const [filter, setFilter] = useState<string>('all');

    useEffect(() => {
        const fetchBroadcasts = async () => {
            try {
                const token = localStorage.getItem('symptomap_access_token') || localStorage.getItem('access_token');
                const params = new URLSearchParams({
                    active_only: 'true',
                    limit: limit.toString(),
                });
                if (region) params.append('region', region);

                const response = await fetch(`${API_BASE_URL}/broadcasts?${params}`, {
                    headers: token ? { 'Authorization': `Bearer ${token}` } : {}
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch broadcasts');
                }

                const data = await response.json();
                setBroadcasts(Array.isArray(data) ? data : []);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load broadcasts');
            } finally {
                setLoading(false);
            }
        };

        fetchBroadcasts();
    }, [region, limit]);

    const filteredBroadcasts = filter === 'all'
        ? broadcasts
        : broadcasts.filter(b => b.severity === filter);

    if (loading) {
        return (
            <div className="space-y-6">
                {[1, 2, 3].map(i => (
                    <div key={i} className="bg-white border border-slate-200 rounded-3xl p-8 animate-pulse shadow-sm">
                        <div className="flex items-start gap-5">
                            <div className="w-14 h-14 bg-slate-100 rounded-2xl"></div>
                            <div className="flex-1 space-y-4">
                                <div className="h-4 bg-slate-100 rounded-full w-1/4"></div>
                                <div className="h-6 bg-slate-100 rounded-full w-3/4"></div>
                                <div className="h-4 bg-slate-100 rounded-full w-full"></div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-100 rounded-[2rem] p-12 text-center shadow-sm">
                <div className="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                    <AlertTriangle className="w-8 h-8 text-red-600" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">Systems Failure</h3>
                <p className="text-red-600/80 max-w-xs mx-auto text-sm font-medium">{error}</p>
            </div>
        );
    }

    if (broadcasts.length === 0) {
        return (
            <div className="bg-white border border-slate-200 rounded-[2rem] p-16 text-center shadow-sm">
                <div className="w-20 h-20 bg-indigo-50 rounded-[2rem] flex items-center justify-center mx-auto mb-6">
                    <Radio className="w-10 h-10 text-indigo-600" />
                </div>
                <h3 className="text-2xl font-black text-slate-900 mb-2">Airwaves Silent</h3>
                <p className="text-slate-500 max-w-sm mx-auto">No health broadcasts are currently active in your region. Monitoring continues.</p>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Advanced Filters */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 overflow-x-auto scrollbar-hide pb-2">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-indigo-50 rounded-lg">
                        <Filter className="w-4 h-4 text-indigo-600" />
                    </div>
                    <div className="flex gap-2">
                        {['all', 'emergency', 'critical', 'warning', 'info'].map(level => (
                            <button
                                key={level}
                                onClick={() => setFilter(level)}
                                className={`px-5 py-2.5 rounded-xl text-xs font-black uppercase tracking-widest transition-all whitespace-nowrap border
                                    ${filter === level
                                        ? 'bg-indigo-600 border-indigo-600 text-white shadow-lg shadow-indigo-100 scale-105'
                                        : 'bg-white border-slate-200 text-slate-500 hover:text-indigo-600 hover:bg-slate-50'
                                    }`}
                            >
                                {level}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="hidden lg:flex items-center gap-2 text-xs font-bold text-slate-400">
                    <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                    SECURED TELEMETRY ACTIVE
                </div>
            </div>

            {/* Optimized Broadcast Grid */}
            <div className="grid grid-cols-1 gap-6">
                {filteredBroadcasts.map((broadcast, i) => (
                    <div key={broadcast.id} className="animate-in fade-in slide-in-from-bottom-4 duration-700" style={{ animationDelay: `${i * 100}ms` }}>
                        <BroadcastCard
                            broadcast={broadcast}
                            isExpanded={expandedId === broadcast.id}
                            onToggle={() => setExpandedId(expandedId === broadcast.id ? null : broadcast.id)}
                        />
                    </div>
                ))}
            </div>

            {filteredBroadcasts.length === 0 && filter !== 'all' && (
                <div className="bg-white border border-slate-200 rounded-[2rem] p-12 text-center shadow-sm">
                    <p className="text-slate-400 font-bold uppercase tracking-widest text-xs">No matching {filter} announcements</p>
                </div>
            )}
        </div>
    );
};

export default BroadcastFeed;
