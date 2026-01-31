import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useEffect } from 'react';
import { useAuthStore } from './store/authStore';

// Layout
import Layout from '@/components/layout/Layout';
import ProtectedRoute from '@/components/layout/ProtectedRoute';

// Pages
import DashboardPage from '@/pages/DashboardPage';
import ChatbotPage from '@/pages/ChatbotPage';
import AdminDashboard from '@/pages/AdminDashboard';
import AnalyticsDashboard from '@/pages/AnalyticsDashboard';
import AlertsDashboard from '@/pages/AlertsDashboard';
import ReportsPage from '@/pages/ReportsPage';
import PredictionDashboard from '@/pages/PredictionDashboard';
import LandingPage from '@/pages/LandingPage';
import DoctorStation from '@/pages/DoctorStation';
import ApprovalRequestsPage from '@/pages/ApprovalRequestsPage';
import LoginPage from '@/pages/LoginPage';
import RegisterPage from '@/pages/RegisterPage';

function App() {
  const checkAuth = useAuthStore(state => state.checkAuth);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Legacy redirect */}
        <Route path="/doctor" element={<Navigate to="/login" replace />} />

        {/* Doctor Routes */}
        <Route path="/doctor/station" element={
          <ProtectedRoute roles={['doctor', 'admin']}>
            <DoctorStation />
          </ProtectedRoute>
        } />

        {/* Admin Routes */}
        <Route path="/admin/approvals" element={
          <ProtectedRoute roles={['admin']}>
            <ApprovalRequestsPage />
          </ProtectedRoute>
        } />

        {/* Main App Routes (Authenticated) */}
        <Route path="/*" element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/chatbot" element={<ChatbotPage />} />
                <Route path="/admin" element={
                  <ProtectedRoute roles={['admin']}>
                    <AdminDashboard />
                  </ProtectedRoute>
                } />
                <Route path="/analytics" element={<AnalyticsDashboard />} />
                <Route path="/alerts" element={<AlertsDashboard />} />
                <Route path="/reports" element={<ReportsPage />} />
                <Route path="/predictions" element={<PredictionDashboard />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        } />
      </Routes>

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#1e293b',
            color: '#fff',
            fontSize: '14px',
            borderRadius: '8px',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </Router>
  );
}

export default App;
