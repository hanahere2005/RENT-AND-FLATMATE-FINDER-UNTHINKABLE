import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const API_URL = 'http://localhost:5000';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [loading, setLoading] = useState(true);

  // Configure global axios default authorization header
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      localStorage.setItem('token', token);
    } else {
      delete axios.defaults.headers.common['Authorization'];
      localStorage.removeItem('token');
    }
  }, [token]);

  // Load current user profile details if token is present
  useEffect(() => {
    const fetchUser = async () => {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const res = await axios.get(`${API_URL}/auth/me`);
        setUser(res.data.user);
        setProfile(res.data.profile);
      } catch (err) {
        console.error("Failed to load user profile", err);
        // If auth fails, try to refresh once or clear
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          try {
            const refreshRes = await axios.post(`${API_URL}/auth/refresh`, {}, {
              headers: { Authorization: `Bearer ${refreshToken}` }
            });
            const newAccess = refreshRes.data.access_token;
            setToken(newAccess);
            // Retry fetching profile
            const retryRes = await axios.get(`${API_URL}/auth/me`, {
              headers: { Authorization: `Bearer ${newAccess}` }
            });
            setUser(retryRes.data.user);
            setProfile(retryRes.data.profile);
          } catch (refreshErr) {
            logout();
          }
        } else {
          logout();
        }
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [token]);

  const login = async (email, password) => {
    try {
      const res = await axios.post(`${API_URL}/auth/login`, { email, password });
      setToken(res.data.access_token);
      localStorage.setItem('refresh_token', res.data.refresh_token);
      setUser(res.data.user);
      setProfile(res.data.profile);
      return { success: true };
    } catch (err) {
      const message = err.response?.data?.error || 'Login failed';
      return { success: false, error: message };
    }
  };

  const registerUser = async (registrationData) => {
    try {
      await axios.post(`${API_URL}/auth/register`, registrationData);
      return { success: true };
    } catch (err) {
      const message = err.response?.data?.error || 'Registration failed';
      return { success: false, error: message };
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    setProfile(null);
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
  };

  const updateProfileInState = (updatedProfile) => {
    setProfile(updatedProfile);
  };

  return (
    <AuthContext.Provider value={{
      user,
      profile,
      token,
      loading,
      login,
      logout,
      registerUser,
      updateProfileInState,
      isAuthenticated: !!user,
      isAdmin: user?.role === 'admin',
      isOwner: user?.role === 'owner',
      isTenant: user?.role === 'tenant'
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
