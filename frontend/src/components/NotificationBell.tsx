import { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config/api';

interface NotificationBellProps {
    className?: string;
}

const NotificationBell = ({ className = '' }: NotificationBellProps) => {
    const [pendingCount, setPendingCount] = useState(0);
    const [showDropdown, setShowDropdown] = useState(false);
    const navigate = useNavigate();

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

    useEffect(() => {
        fetchPendingCount();
        // Refresh every 30 seconds
        const interval = setInterval(fetchPendingCount, 30000);
        return () => clearInterval(interval);
    }, []);

    const handleClick = () => {
        const token = localStorage.getItem('doctor_token');
        if (token) {
            navigate('/admin/approvals');
        } else {
            setShowDropdown(!showDropdown);
        }
    };

    return (
        <div className={`relative ${className}`}>
            <button
                onClick={handleClick}
                className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-full transition-colors"
                title={pendingCount > 0 ? `${pendingCount} pending requests` : 'No pending requests'}
            >
                <Bell className="w-5 h-5" />
                {pendingCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1">
                        {pendingCount > 99 ? '99+' : pendingCount}
                    </span>
                )}
            </button>

            {showDropdown && (
                <div className="absolute right-0 mt-2 w-72 bg-white rounded-lg shadow-lg border z-50">
                    <div className="p-4">
                        <h3 className="font-semibold text-gray-800 mb-2">Pending Requests</h3>
                        {pendingCount > 0 ? (
                            <>
                                <p className="text-sm text-gray-600 mb-3">
                                    {pendingCount} outbreak report{pendingCount !== 1 ? 's' : ''} awaiting approval
                                </p>
                                <a
                                    href="/doctor"
                                    className="block text-center bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors text-sm"
                                >
                                    Login to Review
                                </a>
                            </>
                        ) : (
                            <p className="text-sm text-gray-500">No pending requests</p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default NotificationBell;
