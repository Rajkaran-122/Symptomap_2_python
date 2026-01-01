import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, Activity } from 'lucide-react';

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
                const response = await fetch('http://localhost:8000/api/v1/analytics/week-comparison');
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

    const getTrendIcon = (value: number) => {
        if (value > 0) return <TrendingUp className="w-4 h-4 text-red-500" />;
        if (value < 0) return <TrendingDown className="w-4 h-4 text-green-500" />;
        return <Minus className="w-4 h-4 text-gray-400" />;
    };

    const getTrendColor = (value: number) => {
        if (value > 0) return 'text-red-500';
        if (value < 0) return 'text-green-500';
        return 'text-gray-500';
    };

    if (loading) {
        return (
            <div className={`bg-white rounded-xl shadow-sm border p-4 ${className}`}>
                <div className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="h-20 bg-gray-100 rounded"></div>
                        <div className="h-20 bg-gray-100 rounded"></div>
                    </div>
                </div>
            </div>
        );
    }

    if (!data) return null;

    return (
        <div className={`bg-white rounded-xl shadow-sm border p-4 ${className}`}>
            <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5 text-blue-500" />
                Week Comparison
            </h3>

            <div className="grid grid-cols-2 gap-4">
                {/* Outbreaks */}
                <div className="bg-gray-50 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-500">Outbreaks</span>
                        {getTrendIcon(data.change.outbreaks)}
                    </div>
                    <div className="flex items-end gap-2">
                        <span className="text-2xl font-bold text-gray-800">
                            {data.this_week.outbreaks}
                        </span>
                        <span className={`text-sm font-medium ${getTrendColor(data.change.outbreaks)}`}>
                            {data.change.outbreaks > 0 ? '+' : ''}{data.change.outbreaks}
                            <span className="text-xs ml-1">
                                ({data.change.outbreak_percent > 0 ? '+' : ''}{data.change.outbreak_percent}%)
                            </span>
                        </span>
                    </div>
                    <p className="text-xs text-gray-400 mt-1">vs last week: {data.last_week.outbreaks}</p>
                </div>

                {/* Cases */}
                <div className="bg-gray-50 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-500">Cases</span>
                        {getTrendIcon(data.change.cases)}
                    </div>
                    <div className="flex items-end gap-2">
                        <span className="text-2xl font-bold text-gray-800">
                            {data.this_week.cases}
                        </span>
                        <span className={`text-sm font-medium ${getTrendColor(data.change.cases)}`}>
                            {data.change.cases > 0 ? '+' : ''}{data.change.cases}
                        </span>
                    </div>
                    <p className="text-xs text-gray-400 mt-1">vs last week: {data.last_week.cases}</p>
                </div>
            </div>
        </div>
    );
};

export default WeekComparison;
