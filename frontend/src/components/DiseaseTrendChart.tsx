import { useState, useEffect } from 'react';
import { TrendingUp, Calendar } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

interface TrendDataPoint {
    date: string;
    outbreaks: number;
    cases: number;
}

interface DiseaseTrendChartProps {
    className?: string;
}

const DiseaseTrendChart = ({ className = '' }: DiseaseTrendChartProps) => {
    const [data, setData] = useState<TrendDataPoint[]>([]);
    const [loading, setLoading] = useState(true);
    const [period, setPeriod] = useState('30d');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/v1/analytics/trend-data');
                if (response.ok) {
                    const result = await response.json();
                    setData(result.trend_data || []);
                }
            } catch (error) {
                console.error('Error fetching trend data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const formatDate = (dateStr: string) => {
        if (!dateStr) return '';
        try {
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        } catch {
            return dateStr;
        }
    };

    if (loading) {
        return (
            <div className={`bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-white/20 p-6 ${className}`}>
                <div className="animate-pulse">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-11 h-11 bg-gradient-to-br from-gray-200 to-gray-300 rounded-xl"></div>
                        <div className="h-5 bg-gray-200 rounded-lg w-40"></div>
                    </div>
                    <div className="h-64 bg-gradient-to-br from-gray-100 to-gray-50 rounded-xl"></div>
                </div>
            </div>
        );
    }

    // Generate sample data if empty
    const chartData = data.length > 0 ? data : [
        { date: '2025-12-25', outbreaks: 2, cases: 45 },
        { date: '2025-12-26', outbreaks: 3, cases: 62 },
        { date: '2025-12-27', outbreaks: 1, cases: 28 },
        { date: '2025-12-28', outbreaks: 4, cases: 95 },
        { date: '2025-12-29', outbreaks: 2, cases: 51 },
        { date: '2025-12-30', outbreaks: 5, cases: 120 },
        { date: '2025-12-31', outbreaks: 3, cases: 78 },
    ];

    return (
        <div className={`bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-white/20 p-6 overflow-hidden relative ${className}`}>
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-48 h-48 bg-gradient-to-bl from-cyan-500/10 to-blue-500/5 rounded-full blur-3xl -z-10"></div>

            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 shadow-lg shadow-cyan-300/50">
                        <TrendingUp className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h3 className="font-bold text-gray-800 text-lg">Disease Trends</h3>
                        <p className="text-xs text-gray-400">Outbreak patterns over time</p>
                    </div>
                </div>

                {/* Period Selector */}
                <div className="flex items-center gap-1 p-1 bg-gray-100 rounded-lg">
                    {['7d', '30d', '90d'].map((p) => (
                        <button
                            key={p}
                            onClick={() => setPeriod(p)}
                            className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${period === p
                                    ? 'bg-white text-gray-800 shadow-sm'
                                    : 'text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            {p}
                        </button>
                    ))}
                </div>
            </div>

            {/* Chart */}
            <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <defs>
                            <linearGradient id="colorOutbreaks" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                            </linearGradient>
                            <linearGradient id="colorCases" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <XAxis
                            dataKey="date"
                            tickFormatter={formatDate}
                            tick={{ fontSize: 11, fill: '#9ca3af' }}
                            axisLine={false}
                            tickLine={false}
                        />
                        <YAxis
                            tick={{ fontSize: 11, fill: '#9ca3af' }}
                            axisLine={false}
                            tickLine={false}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                                borderRadius: '12px',
                                border: 'none',
                                boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
                                padding: '12px 16px'
                            }}
                            labelFormatter={formatDate}
                        />
                        <Area
                            type="monotone"
                            dataKey="cases"
                            stroke="#8b5cf6"
                            strokeWidth={2}
                            fill="url(#colorCases)"
                            dot={false}
                            activeDot={{ r: 6, fill: '#8b5cf6', stroke: '#fff', strokeWidth: 2 }}
                        />
                        <Area
                            type="monotone"
                            dataKey="outbreaks"
                            stroke="#06b6d4"
                            strokeWidth={2.5}
                            fill="url(#colorOutbreaks)"
                            dot={false}
                            activeDot={{ r: 6, fill: '#06b6d4', stroke: '#fff', strokeWidth: 2 }}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>

            {/* Legend */}
            <div className="flex items-center justify-center gap-6 mt-4 pt-4 border-t border-gray-100">
                <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-cyan-500"></div>
                    <span className="text-xs font-medium text-gray-600">Outbreaks</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-violet-500"></div>
                    <span className="text-xs font-medium text-gray-600">Cases</span>
                </div>
            </div>
        </div>
    );
};

export default DiseaseTrendChart;
