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
import DoctorRegisterPage from '@/pages/DoctorRegisterPage';
import UserLoginPage from '@/pages/UserLoginPage';
import UserDashboard from '@/pages/UserDashboard';
import PublicMapPage from '@/pages/PublicMapPage';
import AdminBroadcastPanel from '@/components/broadcasts/AdminBroadcastPanel';

function App() {
  const checkAuth = useAuthStore(state => state.checkAuth);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        {/* ═══════════════════════════════════════════
            PUBLIC ROUTES — No auth required
        ═══════════════════════════════════════════ */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/register/doctor" element={<DoctorRegisterPage />} />

        {/* ═══════════════════════════════════════════
            USER (PATIENT) ROUTES — role='user' only
        ═══════════════════════════════════════════ */}
        <Route path="/user/login" element={<UserLoginPage />} />
        <Route path="/user/dashboard" element={<UserDashboard />} />
        <Route path="/user/map" element={<PublicMapPage />} />
        <Route path="/user/chatbot" element={<ChatbotPage />} />

        {/* ═══════════════════════════════════════════
            DOCTOR ROUTES — role='doctor' or 'admin'
        ═══════════════════════════════════════════ */}
        <Route path="/doctor/station" element={
          <ProtectedRoute roles={['doctor', 'admin']}>
            <DoctorStation />
          </ProtectedRoute>
        } />

        {/* Legacy redirect */}
        <Route path="/doctor" element={<Navigate to="/login" replace />} />

        {/* ═══════════════════════════════════════════
            ADMIN ROUTES — role='admin' only
        ═══════════════════════════════════════════ */}
        <Route path="/admin/approvals" element={
          <ProtectedRoute roles={['admin']}>
            <ApprovalRequestsPage />
          </ProtectedRoute>
        } />

        <Route path="/admin/broadcasts" element={
          <ProtectedRoute roles={['admin']}>
            <AdminBroadcastPanel />
          </ProtectedRoute>
        } />

        {/* ═══════════════════════════════════════════
            MAIN APP ROUTES — Doctor / Admin Layout
        ═══════════════════════════════════════════ */}
        <Route path="/*" element={
          <ProtectedRoute roles={['doctor', 'admin']}>
            <Layout>
              <Routes>
                <Route path="/dashboard" element={<DashboardPage />} />
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
