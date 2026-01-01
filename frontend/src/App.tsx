
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

// Layout
import Layout from '@/components/layout/Layout';

// Pages
import DashboardPage from '@/pages/DashboardPage';
import ChatbotPage from '@/pages/ChatbotPage';
import AdminDashboard from '@/pages/AdminDashboard';
import AnalyticsDashboard from '@/pages/AnalyticsDashboard';
import AlertsDashboard from '@/pages/AlertsDashboard';
import ReportsPage from '@/pages/ReportsPage';
import PredictionDashboard from '@/pages/PredictionDashboard';
import LandingPage from '@/pages/LandingPage';
import DoctorLogin from '@/pages/DoctorLogin';
import DoctorStation from '@/pages/DoctorStation';
import ApprovalRequestsPage from '@/pages/ApprovalRequestsPage';

function App() {
  return (
    <Router>
      <Routes>
        {/* Doctor Station Routes (No Layout) */}
        <Route path="/doctor" element={<DoctorLogin />} />
        <Route path="/doctor/station" element={<DoctorStation />} />

        {/* Admin Approval Route (No Layout for full-page experience) */}
        <Route path="/admin/approvals" element={<ApprovalRequestsPage />} />

        {/* Main App Routes (With Layout) */}
        <Route path="/*" element={
          <Layout>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/chatbot" element={<ChatbotPage />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/analytics" element={<AnalyticsDashboard />} />
              <Route path="/alerts" element={<AlertsDashboard />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/predictions" element={<PredictionDashboard />} />
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
          </Layout>
        } />
      </Routes>
    </Router>
  );
}

export default App;
