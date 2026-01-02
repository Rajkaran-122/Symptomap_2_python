import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, BarChart3, AlertTriangle, Users } from 'lucide-react';
import { API_BASE_URL } from '../config/api';

interface WeekData {
    this_week: { outbreaks: number; cases: number };
    last_week: { outbreaks: number; cases: number };
    change: {
        outbreaks: number;
        cases: number;
        outbreak_percent: number;
        case_percent: number;
    };
}

const WeekComparison = ({ className = '' }: { className?: string }) => {
    const [data, setData] = useState<WeekData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/analytics/week-comparison`);
                if (response.ok) {
                    const result = await response.json();
                    if (!result.error) {
                        setData(result);
                    }
                }
            } catch (error) {
                console.error('Error fetching week comparison:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const getTrendIcon = (value: number, size = 'w-5 h-5') => {
        if (value > 0) return <TrendingUp className={`${size} text-red-500`} />;
        if (value < 0) return <TrendingDown className={`${size} text-emerald-500`} />;
        return <Minus className={`${size} text-gray-400`} />;
    };

    const getTrendBg = (value: number) => {
        if (value > 0) return 'from-red-500/10 to-rose-500/5 border-red-200';
        if (value < 0) return 'from-emerald-500/10 to-green-500/5 border-emerald-200';
        return 'from-gray-100 to-gray-50 border-gray-200';
    };

    const getTrendText = (value: number) => {
        if (value > 0) return 'text-red-600';
        if (value < 0) return 'text-emerald-600';
        return 'text-gray-600';
    };

    if (loading) {
        return (
            <div className={`bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-white/20 p-6 ${className}`}>
                <div className="animate-pulse">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-11 h-11 bg-gradient-to-br from-gray-200 to-gray-300 rounded-xl"></div>
                        <div className="h-5 bg-gray-200 rounded-lg w-32"></div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="h-28 bg-gradient-to-br from-gray-100 to-gray-50 rounded-xl"></div>
                        <div className="h-28 bg-gradient-to-br from-gray-100 to-gray-50 rounded-xl"></div>
                    </div>
                </div>
            </div>
        );
    }

    if (!data) return null;

    return (
        <div className={`bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-white/20 p-6 overflow-hidden relative ${className}`}>
            {/* Background decoration */}
            <div className="absolute bottom-0 left-0 w-32 h-32 bg-gradient-to-tr from-purple-500/10 to-indigo-500/5 rounded-full blur-3xl -z-10"></div>

            {/* Header */}
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 rounded-xl bg-gradient-to-br from-purple-500 to-indigo-600 shadow-lg shadow-purple-300/50">
                    <BarChart3 className="w-5 h-5 text-white" />
                </div>
                <div>
                    <h3 className="font-bold text-gray-800 text-lg">Week Comparison</h3>
                    <p className="text-xs text-gray-400">This week vs last week</p>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
                {/* Outbreaks Card */}
                <div className={`rounded-xl p-4 bg-gradient-to-br ${getTrendBg(data.change.outbreaks)} border transition-all duration-300 hover:shadow-lg cursor-pointer group`}>
                    <div className="flex items-center justify-between mb-3">
                        <div className="p-2 rounded-lg bg-white shadow-sm">
                            <AlertTriangle className="w-4 h-4 text-amber-600" />
                        </div>
                        <div className={`p-1.5 rounded-full ${data.change.outbreaks > 0 ? 'bg-red-100' : data.change.outbreaks < 0 ? 'bg-emerald-100' : 'bg-gray-100'}`}>
                            {getTrendIcon(data.change.outbreaks, 'w-4 h-4')}
                        </div>
                    </div>
                    <p className="text-xs text-gray-500 font-medium uppercase tracking-wider mb-1">Outbreaks</p>
                    <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-bold text-gray-900">
                            {data.this_week.outbreaks}
                        </span>
                        <span className={`text-sm font-bold ${getTrendText(data.change.outbreaks)}`}>
                            {data.change.outbreaks > 0 ? '+' : ''}{data.change.outbreaks}
                        </span>
                    </div>
                    <div className="mt-2 flex items-center gap-1">
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${data.change.outbreaks > 0 ? 'bg-red-100 text-red-700' : data.change.outbreaks < 0 ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-600'}`}>
                            {data.change.outbreak_percent > 0 ? '+' : ''}{data.change.outbreak_percent}%
                        </span>
                        <span className="text-xs text-gray-400">vs {data.last_week.outbreaks}</span>
                    </div>
                </div>

                {/* Cases Card */}
                <div className={`rounded-xl p-4 bg-gradient-to-br ${getTrendBg(data.change.cases)} border transition-all duration-300 hover:shadow-lg cursor-pointer group`}>
                    <div className="flex items-center justify-between mb-3">
                        <div className="p-2 rounded-lg bg-white shadow-sm">
                            <Users className="w-4 h-4 text-blue-600" />
                        </div>
                        <div className={`p-1.5 rounded-full ${data.change.cases > 0 ? 'bg-red-100' : data.change.cases < 0 ? 'bg-emerald-100' : 'bg-gray-100'}`}>
                            {getTrendIcon(data.change.cases, 'w-4 h-4')}
                        </div>
                    </div>
                    <p className="text-xs text-gray-500 font-medium uppercase tracking-wider mb-1">Cases</p>
                    <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-bold text-gray-900">
                            {data.this_week.cases}
                        </span>
                        <span className={`text-sm font-bold ${getTrendText(data.change.cases)}`}>
                            {data.change.cases > 0 ? '+' : ''}{data.change.cases}
                        </span>
                    </div>
                    <div className="mt-2 flex items-center gap-1">
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${data.change.cases > 0 ? 'bg-red-100 text-red-700' : data.change.cases < 0 ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-600'}`}>
                            {data.change.case_percent > 0 ? '+' : ''}{data.change.case_percent}%
                        </span>
                        <span className="text-xs text-gray-400">vs {data.last_week.cases}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default WeekComparison;

