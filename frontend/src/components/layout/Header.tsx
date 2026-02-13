import { useState, useEffect } from 'react';
import { Bell, Search, User, Stethoscope } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { API_BASE_URL } from '../../config/api';

const Header = () => {
    const [pendingCount, setPendingCount] = useState(0);
    const navigate = useNavigate();
    const { user } = useAuthStore();

    const userRole = user?.role || 'guest';
    const userName = user?.full_name || user?.email || 'Guest';

    const isDoctor = userRole === 'doctor';
    const isAdmin = userRole === 'admin';
    const showDoctorStation = isDoctor || isAdmin;
    const showNotifications = isDoctor || isAdmin;

    useEffect(() => {
        if (!showNotifications) return;

        const fetchPendingCount = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/outbreaks/pending-count`);
                if (response.ok) {
                    const data = await response.json();
                    setPendingCount(data.pending_count || 0);
                }
            } catch (error) {
                console.error('Error fetching pending count:', error);
            }
        };
        fetchPendingCount();
        const interval = setInterval(fetchPendingCount, 30000);
        return () => clearInterval(interval);
    }, [showNotifications]);

    const handleNotificationClick = () => {
        if (isAdmin) {
            navigate('/admin/approvals');
        } else {
            navigate('/doctor/station');
        }
    };

    const getRoleBadge = () => {
        if (isAdmin) {
            return <span className="px-2 py-0.5 bg-red-500/80 text-white text-[10px] font-bold rounded-full uppercase">Admin</span>;
        } else if (isDoctor) {
            return <span className="px-2 py-0.5 bg-green-500/80 text-white text-[10px] font-bold rounded-full uppercase">Dr</span>;
        }
        return null;
    };

    return (
        <header className="fixed top-0 left-0 right-0 h-16 bg-gradient-to-r from-primary-900 to-primary-800 text-white z-40 shadow-md flex items-center justify-between px-6">
            {/* Left: Branding */}
            <div className="flex items-center w-[240px]">
                <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center mr-3 shadow-lg ring-2 ring-blue-400/30">
                    <span className="font-bold text-white">SM</span>
                </div>
                <div>
                    <h1 className="text-xl font-bold tracking-tight">SymptoMap</h1>
                    <p className="text-[10px] text-blue-200 uppercase tracking-widest font-semibold">Intelligence</p>
                </div>
            </div>

            {/* Center: Search (Doctor/Admin only) */}
            {showDoctorStation && (
                <div className="hidden md:flex items-center flex-1 max-w-xl mx-8">
                    <div className="relative w-full">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <Search className="h-4 w-4 text-primary-300" />
                        </div>
                        <input
                            type="text"
                            placeholder="Search hospitals, diseases, or zones..."
                            className="block w-full pl-10 pr-3 py-2 border border-transparent rounded-lg leading-5 bg-primary-800/50 text-white placeholder-primary-300 focus:outline-none focus:bg-primary-800 focus:ring-1 focus:ring-primary-400 sm:text-sm transition-all"
                        />
                    </div>
                </div>
            )}

            {/* Right: Actions */}
            <div className="flex items-center space-x-4">
                {/* Doctor Station Quick Access — Doctor/Admin only */}
                {showDoctorStation && (
                    <button
                        onClick={() => navigate('/doctor/station')}
                        className="p-2 rounded-lg bg-green-600/80 hover:bg-green-500 transition-colors flex items-center gap-2 text-sm font-medium"
                        title="Doctor Station - Submit Outbreak Data"
                    >
                        <Stethoscope className="w-4 h-4" />
                        <span className="hidden lg:inline">Doctor Station</span>
                    </button>
                )}

                {/* Notification Bell — Doctor/Admin only */}
                {showNotifications && (
                    <button
                        onClick={handleNotificationClick}
                        className="p-2 rounded-full hover:bg-white/10 transition-colors relative"
                        title={pendingCount > 0 ? `${pendingCount} pending approval requests` : 'No pending requests'}
                    >
                        <Bell className="w-5 h-5 text-primary-100" />
                        {pendingCount > 0 && (
                            <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center px-1 animate-pulse">
                                {pendingCount > 99 ? '99+' : pendingCount}
                            </span>
                        )}
                    </button>
                )}

                <div className="h-8 w-px bg-primary-700 mx-2"></div>

                <button className="flex items-center space-x-3 hover:bg-white/10 p-2 rounded-lg transition-colors">
                    <div className="text-right hidden md:block">
                        <p className="text-sm font-medium text-white">{userName}</p>
                        <div className="flex items-center justify-end gap-1">
                            {getRoleBadge()}
                        </div>
                    </div>
                    <div className="w-9 h-9 rounded-full bg-primary-200 flex items-center justify-center text-primary-900 ring-2 ring-white/20 relative">
                        <User className="w-5 h-5" />
                        {isAdmin && (
                            <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-red-500 rounded-full border-2 border-primary-800"></span>
                        )}
                        {isDoctor && (
                            <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 rounded-full border-2 border-primary-800"></span>
                        )}
                    </div>
                </button>
            </div>
        </header>
    );
};

export default Header;
