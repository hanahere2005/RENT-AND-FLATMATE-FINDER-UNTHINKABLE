import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Providers
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './context/ToastContext';
import { AuthProvider } from './context/AuthContext';
import { SocketProvider } from './context/SocketContext';

// Layouts & Components
import MainLayout from './layouts/MainLayout';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import TenantDashboard from './pages/TenantDashboard';
import OwnerDashboard from './pages/OwnerDashboard';
import AdminDashboard from './pages/AdminDashboard';
import ProfilePage from './pages/ProfilePage';
import ListingDetailsPage from './pages/ListingDetailsPage';
import ChatPage from './pages/ChatPage';

function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <AuthProvider>
          <SocketProvider>
            <Router>
              <MainLayout>
                <Routes>
                  {/* Public routes */}
                  <Route path="/" element={<LandingPage />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/signup" element={<SignupPage />} />

                  {/* Generic protected routes (accessible by any logged in user) */}
                  <Route 
                    path="/profile" 
                    element={
                      <ProtectedRoute>
                        <ProfilePage />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/chat" 
                    element={
                      <ProtectedRoute>
                        <ChatPage />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/listings/:id" 
                    element={
                      <ProtectedRoute>
                        <ListingDetailsPage />
                      </ProtectedRoute>
                    } 
                  />

                  {/* Tenant specific routes */}
                  <Route 
                    path="/tenant-dashboard" 
                    element={
                      <ProtectedRoute allowedRoles={['tenant']}>
                        <TenantDashboard />
                      </ProtectedRoute>
                    } 
                  />

                  {/* Owner specific routes */}
                  <Route 
                    path="/owner-dashboard" 
                    element={
                      <ProtectedRoute allowedRoles={['owner']}>
                        <OwnerDashboard />
                      </ProtectedRoute>
                    } 
                  />

                  {/* Admin specific routes */}
                  <Route 
                    path="/admin-dashboard" 
                    element={
                      <ProtectedRoute allowedRoles={['admin']}>
                        <AdminDashboard />
                      </ProtectedRoute>
                    } 
                  />

                  {/* Fallback redirection */}
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </MainLayout>
            </Router>
          </SocketProvider>
        </AuthProvider>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;
