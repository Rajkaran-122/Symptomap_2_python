import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Loader2 } from 'lucide-react';

interface ProtectedRouteProps {
    children: React.ReactNode;
    roles?: string[];
}

const ProtectedRoute = ({ children, roles }: ProtectedRouteProps) => {
    const { isAuthenticated, user, isLoading } = useAuthStore();
    const location = useLocation();

    if (isLoading) {
        return (
            <div className="min-h-screen bg-slate-900 flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
            </div>
        );
    }

    if (!isAuthenticated) {
        // Role-aware login redirect: user paths → /user/login, others → /login
        const isUserPath = location.pathname.startsWith('/user');
        const loginPath = isUserPath ? '/user/login' : '/login';
        return <Navigate to={loginPath} state={{ from: location }} replace />;
    }

    if (roles && user && !roles.includes(user.role)) {
        // If a 'user' tries to access doctor/admin pages, send them to their dashboard
        if (user.role === 'user') {
            return <Navigate to="/user/dashboard" replace />;
        }
        // If a doctor/admin tries to access user pages, send them to main dashboard
        return <Navigate to="/dashboard" replace />;
    }

    return <>{children}</>;
};

export default ProtectedRoute;
