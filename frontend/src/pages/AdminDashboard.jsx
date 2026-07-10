import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { 
  ShieldAlert, Users, Home, Activity, CheckSquare, 
  Trash2, Mail, Loader2, BarChart3, AlertTriangle 
} from 'lucide-react';
import api from '../services/api';

const AdminDashboard = () => {
  const { showToast } = useToast();
  
  const [activeTab, setActiveTab] = useState('analytics'); // 'analytics', 'users', 'listings'
  const [analytics, setAnalytics] = useState(null);
  const [usersList, setUsersList] = useState([]);
  const [listingsList, setListingsList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState(null);

  const loadAdminData = async () => {
    setLoading(true);
    try {
      const anaRes = await api.get('/admin/analytics');
      setAnalytics(anaRes.data);
      
      const usersRes = await api.get('/admin/users');
      setUsersList(usersRes.data || []);
      
      const listRes = await api.get('/admin/listings');
      setListingsList(listRes.data || []);
    } catch (err) {
      console.error(err);
      showToast("Error loading administration details", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAdminData();
  }, []);

  const handleDeleteUser = async (userId) => {
    if (!window.confirm("Are you sure you want to delete this user profile? All associated listings and requests will be deleted.")) return;
    setDeletingId(userId);
    try {
      await api.delete(`/admin/users/${userId}`);
      showToast("User profile deleted successfully", "success");
      loadAdminData();
    } catch (err) {
      console.error(err);
      showToast("Failed to delete user", "error");
    } finally {
      setDeletingId(null);
    }
  };

  const handleDeleteListing = async (listingId) => {
    if (!window.confirm("Are you sure you want to delete this listing?")) return;
    setDeletingId(listingId);
    try {
      await api.delete(`/admin/listings/${listingId}`);
      showToast("Listing deleted successfully", "success");
      loadAdminData();
    } catch (err) {
      console.error(err);
      showToast("Failed to delete listing", "error");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-8 py-4 animate-fade-in">
      
      {/* Banner */}
      <div className="bg-slate-900 text-white p-6 sm:p-8 rounded-3xl relative overflow-hidden shadow-xl">
        <div className="absolute top-0 right-0 w-64 h-64 bg-pink-500/10 rounded-full blur-2xl"></div>
        <div className="relative flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-pink-500/20 flex items-center justify-center text-pink-500">
            <ShieldAlert size={20} />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-black">Administration Control Panel</h1>
            <p className="text-slate-400 text-xs sm:text-sm font-medium">Verify system parameters, monitor active user logs, and manage listings.</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 dark:border-slate-800">
        <button
          onClick={() => setActiveTab('analytics')}
          className={`px-6 py-3 font-extrabold text-sm border-b-2 transition-all flex items-center gap-2
            ${activeTab === 'analytics' 
              ? 'border-pink-600 text-pink-600 dark:text-pink-450' 
              : 'border-transparent text-slate-500 hover:text-slate-950 dark:hover:text-white'}`}
        >
          <BarChart3 size={16} />
          Analytics
        </button>
        <button
          onClick={() => setActiveTab('users')}
          className={`px-6 py-3 font-extrabold text-sm border-b-2 transition-all flex items-center gap-2
            ${activeTab === 'users' 
              ? 'border-pink-600 text-pink-600 dark:text-pink-450' 
              : 'border-transparent text-slate-500 hover:text-slate-950 dark:hover:text-white'}`}
        >
          <Users size={16} />
          Manage Users
          <span className="ml-1 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-350 px-2 py-0.5 rounded-full text-[10px] font-bold">
            {usersList.length}
          </span>
        </button>
        <button
          onClick={() => setActiveTab('listings')}
          className={`px-6 py-3 font-extrabold text-sm border-b-2 transition-all flex items-center gap-2
            ${activeTab === 'listings' 
              ? 'border-pink-600 text-pink-600 dark:text-pink-450' 
              : 'border-transparent text-slate-500 hover:text-slate-950 dark:hover:text-white'}`}
        >
          <Home size={16} />
          Manage Listings
          <span className="ml-1 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-350 px-2 py-0.5 rounded-full text-[10px] font-bold">
            {listingsList.length}
          </span>
        </button>
      </div>

      {/* SECTION 1: ANALYTICS OVERVIEW */}
      {activeTab === 'analytics' && (
        <div className="space-y-6">
          {loading || !analytics ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-pulse">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="h-32 bg-slate-100 dark:bg-slate-850 rounded-2xl"></div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              
              {/* Users Stat */}
              <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-500">
                  <Users size={24} />
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-bold block uppercase">Total Accounts</span>
                  <span className="text-xl font-black text-slate-900 dark:text-white">{analytics.users.total}</span>
                  <div className="text-[9px] text-slate-500 font-semibold mt-0.5">
                    {analytics.users.tenants} Tenants / {analytics.users.owners} Owners
                  </div>
                </div>
              </div>

              {/* Listings Stat */}
              <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-pink-500/10 flex items-center justify-center text-pink-500">
                  <Home size={24} />
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-bold block uppercase">Total Rooms</span>
                  <span className="text-xl font-black text-slate-900 dark:text-white">{analytics.listings.total}</span>
                  <div className="text-[9px] text-slate-500 font-semibold mt-0.5">
                    {analytics.listings.active} Active / {analytics.listings.filled} Filled
                  </div>
                </div>
              </div>

              {/* Requests Stat */}
              <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-500">
                  <Activity size={24} />
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-bold block uppercase">Interest Requests</span>
                  <span className="text-xl font-black text-slate-900 dark:text-white">{analytics.requests.total}</span>
                  <div className="text-[9px] text-slate-500 font-semibold mt-0.5">
                    {analytics.requests.accepted} Accepted / {analytics.requests.pending} Pending
                  </div>
                </div>
              </div>

              {/* Chats Stat */}
              <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-rose-500/10 flex items-center justify-center text-rose-500">
                  <CheckSquare size={24} />
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 font-bold block uppercase">Unlocked Chats</span>
                  <span className="text-xl font-black text-slate-900 dark:text-white">{analytics.chats.total}</span>
                  <div className="text-[9px] text-slate-500 font-semibold mt-0.5">Active roommate conversations</div>
                </div>
              </div>

            </div>
          )}
        </div>
      )}

      {/* SECTION 2: USERS DIRECTORY */}
      {activeTab === 'users' && (
        <div className="bg-white dark:bg-slate-800 rounded-3xl border border-slate-100 dark:border-slate-700/50 shadow-sm overflow-hidden">
          <div className="p-5 border-b border-slate-100 dark:border-slate-700">
            <h2 className="font-extrabold text-lg text-slate-900 dark:text-white">Platform Users</h2>
            <p className="text-xs text-slate-400 font-medium">List of all tenant and owner profiles registered on the platform.</p>
          </div>

          <div className="overflow-x-auto">
            {usersList.length === 0 ? (
              <div className="text-center py-12 p-6 text-slate-400">No users found.</div>
            ) : (
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50 dark:bg-slate-900 text-slate-400 font-bold border-b border-slate-100 dark:border-slate-700">
                    <th className="px-6 py-4">User Email</th>
                    <th className="px-6 py-4">Role</th>
                    <th className="px-6 py-4">Date Joined</th>
                    <th className="px-6 py-4 text-right">Delete Profile</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-700 font-medium">
                  {usersList.map((usr) => (
                    <tr key={usr.id} className="hover:bg-slate-50 dark:hover:bg-slate-750/30 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <Mail size={14} className="text-slate-400" />
                          <span className="font-bold text-slate-900 dark:text-white">{usr.email}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-extrabold uppercase
                          ${usr.role === 'admin' 
                            ? 'bg-rose-500/10 text-rose-600' 
                            : usr.role === 'owner' 
                              ? 'bg-pink-500/10 text-pink-600' 
                              : 'bg-blue-500/10 text-blue-600'}`}>
                          {usr.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-500 dark:text-slate-450">
                        {new Date(usr.created_at).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}
                      </td>
                      <td className="px-6 py-4 text-right">
                        {usr.role !== 'admin' ? (
                          <button
                            onClick={() => handleDeleteUser(usr.id)}
                            disabled={deletingId !== null}
                            className="p-2 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/20 rounded-xl transition-all disabled:opacity-50"
                            title="Delete User Account"
                          >
                            <Trash2 size={14} />
                          </button>
                        ) : (
                          <span className="text-[10px] text-slate-400 italic">Protected</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* SECTION 3: LISTINGS LOG */}
      {activeTab === 'listings' && (
        <div className="bg-white dark:bg-slate-800 rounded-3xl border border-slate-100 dark:border-slate-700/50 shadow-sm overflow-hidden">
          <div className="p-5 border-b border-slate-100 dark:border-slate-700">
            <h2 className="font-extrabold text-lg text-slate-900 dark:text-white">Active &amp; Closed Listings</h2>
            <p className="text-xs text-slate-400 font-medium">Monitor active rooms, verify addresses, and remove fake listings.</p>
          </div>

          <div className="overflow-x-auto">
            {listingsList.length === 0 ? (
              <div className="text-center py-12 p-6 text-slate-400">No rooms listed.</div>
            ) : (
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50 dark:bg-slate-900 text-slate-400 font-bold border-b border-slate-100 dark:border-slate-700">
                    <th className="px-6 py-4">Title</th>
                    <th className="px-6 py-4">Rent</th>
                    <th className="px-6 py-4">Location</th>
                    <th className="px-6 py-4">Owner Email</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4 text-right">Delete Room</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-700 font-medium">
                  {listingsList.map((lst) => (
                    <tr key={lst.id} className="hover:bg-slate-50 dark:hover:bg-slate-750/30 transition-colors">
                      <td className="px-6 py-4 font-bold text-slate-900 dark:text-white">
                        {lst.title}
                      </td>
                      <td className="px-6 py-4 font-extrabold">${lst.rent}</td>
                      <td className="px-6 py-4 text-slate-500 dark:text-slate-450">{lst.location}</td>
                      <td className="px-6 py-4 text-slate-550 dark:text-slate-400">{lst.owner_email}</td>
                      <td className="px-6 py-4">
                        <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase
                          ${lst.is_filled 
                            ? 'bg-slate-200 text-slate-700' 
                            : 'bg-emerald-500/10 text-emerald-600'}`}>
                          {lst.is_filled ? 'Filled' : 'Active'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => handleDeleteListing(lst.id)}
                          disabled={deletingId !== null}
                          className="p-2 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/20 rounded-xl transition-all disabled:opacity-50"
                          title="Delete Listing"
                        >
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

    </div>
  );
};

export default AdminDashboard;
