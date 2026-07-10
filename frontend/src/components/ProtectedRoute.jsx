import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import LoadingSkeleton from './LoadingSkeleton';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { token, user, loading } = useAuth();

  if (loading) {
    // Show a premium loading screen/skeleton while we parse current session
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex flex-col justify-center items-center">
        <LoadingSkeleton type="profile" />
        <p className="mt-4 text-slate-500 dark:text-slate-400 font-medium animate-pulse">Loading secure session...</p>
      </div>
    );
  }

  // Redirect to login if user is not authenticated
  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }

  // Check if role is authorized
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    // Redirect unauthorized user to their proper dashboard or landing page
    if (user.role === 'owner') return <Navigate to="/owner-dashboard" replace />;
    if (user.role === 'tenant') return <Navigate to="/tenant-dashboard" replace />;
    if (user.role === 'admin') return <Navigate to="/admin-dashboard" replace />;
    return <Navigate to="/" replace />;
  }

  return children;
};

export default ProtectedRoute;
