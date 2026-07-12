import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowRight, Sparkles, Home, Shield, Users, MessageCircle } from 'lucide-react';
import api from '../services/api';
import ListingCard from '../components/ListingCard';

const LandingPage = () => {
  const { user } = useAuth();
  const [featuredListings, setFeaturedListings] = useState([]);

  useEffect(() => {
    const fetchListings = async () => {
      try {
        const res = await api.get('/listings?limit=3');
        setFeaturedListings(res.data.listings || []);
      } catch (err) {
        console.error("Failed to load featured rooms", err);
      }
    };
    fetchListings();
  }, []);

  return (
    <div className="space-y-20 py-8">
      
      {/* Hero Section */}
      <section className="relative rounded-3xl overflow-hidden bg-slate-900 text-white p-8 sm:p-12 md:p-16 lg:p-20 shadow-2xl">
        {/* Background Gradients */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl -translate-y-12 translate-x-12"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl translate-y-12 -translate-x-12"></div>
        
        <div className="relative max-w-3xl space-y-6">
          <div className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-pink-500/10 border border-pink-500/30 text-xs font-bold text-pink-400">
            <Sparkles size={14} className="animate-pulse" />
            <span>AI-Powered Roommate &amp; Flat Finder</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-tight">
            Find the Right Home.<br/>
            Meet the Right <span className="bg-gradient-to-r from-blue-400 to-pink-400 bg-clip-text text-transparent">People</span>.
          </h1>

          <p className="text-slate-400 text-base sm:text-lg max-w-2xl font-medium leading-relaxed">
            Stop guessing compatibility. Our matching engine compares budget, locations, move-in dates, and lifestyles to compute scoring alerts before you message.
          </p>

          <div className="flex flex-wrap gap-4 pt-4">
            {user ? (
              <Link
                to={user.role === 'owner' ? '/owner-dashboard' : '/tenant-dashboard'}
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-pink-500 hover:from-blue-500 hover:to-pink-400 font-extrabold text-sm text-white shadow-lg hover:shadow-pink-500/25 transition-all flex items-center gap-2 group"
              >
                Go to Dashboard
                <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
              </Link>
            ) : (
              <>
                <Link
                  to="/signup"
                  className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-pink-500 hover:from-blue-500 hover:to-pink-400 font-extrabold text-sm text-white shadow-lg hover:shadow-pink-500/25 transition-all flex items-center gap-2 group"
                >
                  Get Started
                  <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                </Link>
                <Link
                  to="/login"
                  className="px-6 py-3 rounded-xl border border-slate-700 hover:border-slate-600 hover:bg-slate-800/50 font-bold text-sm text-slate-300 transition-all"
                >
                  Sign In
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="space-y-12">
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-black tracking-tight text-slate-900 dark:text-white">Why use Staylio?</h2>
          <p className="text-slate-500 dark:text-slate-400 max-w-xl mx-auto font-medium">Built with cutting-edge tools to secure bookings, matches, and real-time chat operations.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          
          <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm space-y-4">
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 dark:bg-blue-500/5 flex items-center justify-center text-blue-600 dark:text-blue-400">
              <Sparkles size={24} />
            </div>
            <h3 className="font-extrabold text-lg text-slate-950 dark:text-white">AI Matchmaking</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-medium">
              We weigh budget, furnishing, move-in dates, and locations to cache compatibility scores in our system.
            </p>
          </div>

          <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm space-y-4">
            <div className="w-12 h-12 rounded-xl bg-pink-500/10 dark:bg-pink-500/5 flex items-center justify-center text-pink-600 dark:text-pink-400">
              <MessageCircle size={24} />
            </div>
            <h3 className="font-extrabold text-lg text-slate-950 dark:text-white">WebSocket Chat</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-medium">
              Message owners instantly once interest is accepted. Features online status, read receipts, and typing prompts.
            </p>
          </div>

          <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm space-y-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 dark:bg-emerald-500/5 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
              <Shield size={24} />
            </div>
            <h3 className="font-extrabold text-lg text-slate-950 dark:text-white">Role Access</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-medium">
              Separate modules for owners (listings management), tenants (profiles &amp; filtering), and admins (analytics).
            </p>
          </div>

          <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm space-y-4">
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 dark:bg-blue-500/5 flex items-center justify-center text-blue-600 dark:text-blue-400">
              <Home size={24} />
            </div>
            <h3 className="font-extrabold text-lg text-slate-950 dark:text-white">Property Management</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-medium">
              Upload listing photos, configure exact location guidelines, mark filled listings, and review incoming requests.
            </p>
          </div>

        </div>
      </section>

      {/* Featured Rooms */}
      {featuredListings.length > 0 && (
        <section className="space-y-12">
          <div className="flex justify-between items-end">
            <div className="space-y-2">
              <h2 className="text-3xl font-black tracking-tight text-slate-900 dark:text-white">Explore Available Rooms</h2>
              <p className="text-slate-500 dark:text-slate-400 font-medium">Take a look at active rooms currently seeking flatmates.</p>
            </div>
            <Link
              to="/signup"
              className="text-sm font-extrabold text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1 group"
            >
              See all listings
              <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {featuredListings.map((listing) => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </div>
        </section>
      )}

    </div>
  );
};

export default LandingPage;
