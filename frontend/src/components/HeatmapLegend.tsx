import { MapPin } from 'lucide-react';

interface HeatmapLegendProps {
    className?: string;
    orientation?: 'horizontal' | 'vertical';
}

const HeatmapLegend = ({ className = '', orientation = 'vertical' }: HeatmapLegendProps) => {
    const legendItems = [
        { label: 'Critical', cases: '500+', color: '#DC2626', bgColor: 'from-red-600 to-red-500' },
        { label: 'High', cases: '200-499', color: '#F59E0B', bgColor: 'from-amber-500 to-orange-500' },
        { label: 'Moderate', cases: '50-199', color: '#3B82F6', bgColor: 'from-blue-500 to-indigo-500' },
        { label: 'Low', cases: '10-49', color: '#10B981', bgColor: 'from-emerald-500 to-green-500' },
        { label: 'Minimal', cases: '1-9', color: '#6B7280', bgColor: 'from-gray-500 to-gray-400' },
    ];

    const isHorizontal = orientation === 'horizontal';

    return (
        <div className={`bg-white/90 backdrop-blur-xl rounded-xl shadow-lg border border-white/20 p-4 ${className}`}>
            {/* Header */}
            <div className="flex items-center gap-2 mb-3 pb-2 border-b border-gray-100">
                <div className="p-1.5 rounded-lg bg-gradient-to-br from-rose-500 to-red-600">
                    <MapPin className="w-3.5 h-3.5 text-white" />
                </div>
                <span className="text-sm font-bold text-gray-800">Risk Levels</span>
            </div>

            {/* Legend Items */}
            <div className={`${isHorizontal ? 'flex flex-wrap gap-3' : 'space-y-2'}`}>
                {legendItems.map((item) => (
                    <div
                        key={item.label}
                        className={`flex items-center gap-2 ${isHorizontal ? '' : 'hover:bg-gray-50 rounded-lg px-2 py-1.5 -mx-2 transition-colors cursor-default'}`}
                    >
                        {/* Color indicator */}
                        <div
                            className={`w-4 h-4 rounded-md bg-gradient-to-br ${item.bgColor} shadow-sm ring-1 ring-black/5`}
                        />

                        {/* Label and cases */}
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between gap-2">
                                <span className="text-xs font-semibold text-gray-700">{item.label}</span>
                                <span className="text-[10px] text-gray-400 font-medium">{item.cases}</span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Footer */}
            <div className="mt-3 pt-2 border-t border-gray-100">
                <p className="text-[10px] text-gray-400 text-center">Cases per outbreak area</p>
            </div>
        </div>
    );
};

export default HeatmapLegend;
