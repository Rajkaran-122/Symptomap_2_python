
import { Link, useLocation } from 'react-router-dom';
import { Link, useLocation } from 'react-router-dom';
import {
    LayoutDashboard,
    MessageSquare,
    Stethoscope,
    BarChart2,
    FileText,
    AlertTriangle,
    TrendingUp,
    MapPin,
    Shield,
    LogOut
} from 'lucide-react';

const Sidebar = () => {
    const location = useLocation();

    const menuItems = [
        { label: 'Home', icon: LayoutDashboard, path: '/', color: 'from-blue-500 to-indigo-600' },
        { label: 'Dashboard', icon: MapPin, path: '/dashboard', color: 'from-emerald-500 to-teal-600' },
        { label: 'AI Predictions', icon: TrendingUp, path: '/predictions', color: 'from-violet-500 to-purple-600' },
        { label: 'Alerts', icon: AlertTriangle, path: '/alerts', color: 'from-amber-500 to-orange-600' },
        { label: 'Reports', icon: FileText, path: '/reports', color: 'from-cyan-500 to-blue-600' },
        { label: 'Analytics', icon: BarChart2, path: '/analytics', color: 'from-pink-500 to-rose-600' },
        { label: 'AI Assistant', icon: MessageSquare, path: '/chatbot', color: 'from-green-500 to-emerald-600' },
        { label: 'Doctor Station', icon: Stethoscope, path: '/admin', color: 'from-red-500 to-rose-600' },
    ];

    return (
        <aside className="w-[260px] bg-white/80 backdrop-blur-xl border-r border-gray-100 flex flex-col h-screen fixed left-0 top-16 z-30 shadow-xl">
            {/* Logo Area */}
            <div className="px-6 py-4 border-b border-gray-100">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Navigation</p>
            </div>

            <div className="flex-1 py-4 space-y-1 px-3 overflow-y-auto">
                {menuItems.map((item) => {
                    const isActive = location.pathname === item.path;
                    const Icon = item.icon;
                    return (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`flex items-center px-4 py-3 text-sm font-medium transition-all duration-300 rounded-xl relative group
                                ${isActive
                                    ? 'bg-gradient-to-r from-primary-50 to-primary-100/50 text-primary-900 shadow-sm'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                }`}
                        >
                            {/* Active indicator */}
                            {isActive && (
                                <div className={`absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-gradient-to-b ${item.color} rounded-full`} />
                            )}

                            {/* Icon with gradient background when active */}
                            <div className={`p-2 rounded-lg mr-3 transition-all duration-300 ${isActive
                                ? `bg-gradient-to-br ${item.color} shadow-lg`
                                : 'bg-gray-100 group-hover:bg-gray-200'
                                }`}>
                                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-gray-500 group-hover:text-gray-700'}`} />
                            </div>

                            <span className="flex-1">{item.label}</span>

                            {/* Hover indicator */}
                            {!isActive && (
                                <div className="w-0 h-0.5 bg-gray-300 rounded-full transition-all duration-300 group-hover:w-4"></div>
                            )}
                        </Link>
                    );
                })}
            </div>

            {/* Admin Quick Access */}
            <div className="px-3 py-3 border-t border-gray-100">
                <Link
                    to="/admin/approvals"
                    className="flex items-center px-4 py-3 text-sm font-medium text-gray-600 hover:bg-amber-50 hover:text-amber-700 rounded-xl transition-all duration-300 group"
                >
                    <div className="p-2 rounded-lg bg-amber-100 mr-3 group-hover:bg-amber-200 transition-colors">
                        <Shield className="w-4 h-4 text-amber-600" />
                    </div>
                    <span className="flex-1">Approvals</span>
                    <span className="px-2 py-0.5 text-xs font-bold bg-amber-500 text-white rounded-full">New</span>
                </Link>
            </div>

            {/* User Profile Snippet at bottom */}
            <div className="p-4 border-t border-gray-100 bg-gradient-to-r from-gray-50 to-white">
                <div className="flex items-center">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-primary-200">
                        DR
                    </div>
                    <div className="ml-3 flex-1">
                        <p className="text-sm font-semibold text-gray-900">Dr. User</p>
                        <p className="text-xs text-gray-500">Medical Officer</p>
                    </div>
                    <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors" title="Logout">
                        <LogOut className="w-4 h-4 text-gray-400" />
                    </button>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;

