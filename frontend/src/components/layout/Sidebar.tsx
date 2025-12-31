
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
    LayoutDashboard,
    MessageSquare,
    Stethoscope,
    BarChart2,
    FileText,
    AlertTriangle,
    TrendingUp,
    MapPin
} from 'lucide-react';

const Sidebar = () => {
    const location = useLocation();

    const menuItems = [
        { label: 'Home', icon: LayoutDashboard, path: '/' },
        { label: 'Dashboard', icon: MapPin, path: '/dashboard' },
        { label: 'AI Predictions', icon: TrendingUp, path: '/predictions' },
        { label: 'Alerts', icon: AlertTriangle, path: '/alerts' },
        { label: 'Reports', icon: FileText, path: '/reports' },
        { label: 'Analytics', icon: BarChart2, path: '/analytics' },
        { label: 'AI Assistant', icon: MessageSquare, path: '/chatbot' },
        { label: 'Doctor Station', icon: Stethoscope, path: '/admin' },
    ];

    return (
        <aside className="w-[240px] bg-white border-r border-gray-200 flex flex-col h-screen fixed left-0 top-16 z-30">
            <div className="flex-1 py-6 space-y-1">
                {menuItems.map((item) => {
                    const isActive = location.pathname === item.path;
                    const Icon = item.icon;
                    return (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`flex items-center px-6 py-3 text-sm font-medium transition-colors relative
                                ${isActive
                                    ? 'bg-primary-50 text-primary-900'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                }`}
                        >
                            {isActive && (
                                <div className="absolute left-0 top-0 bottom-0 w-[3px] bg-primary-500" />
                            )}
                            <Icon className={`w-5 h-5 mr-3 ${isActive ? 'text-primary-700' : 'text-gray-400'}`} />
                            {item.label}
                        </Link>
                    );
                })}
            </div>

            {/* User Profile Snippet at bottom */}
            <div className="p-4 border-t border-gray-200">
                <div className="flex items-center">
                    <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-bold text-xs">
                        DR
                    </div>
                    <div className="ml-3">
                        <p className="text-sm font-medium text-gray-900">Dr. User</p>
                        <p className="text-xs text-gray-500">Medical Officer</p>
                    </div>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
