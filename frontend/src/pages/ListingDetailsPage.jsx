import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { 
  Home, MapPin, DollarSign, Calendar, Sparkles, Check, 
  Phone, User, ArrowLeft, Loader2, Heart, ShieldCheck 
} from 'lucide-react';
import api from '../services/api';
import LoadingSkeleton from '../components/LoadingSkeleton';

const ListingDetailsPage = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const { showToast } = useToast();

  const [listing, setListing] = useState(null);
  const [compatScore, setCompatScore] = useState(null);
  const [interestStatus, setInterestStatus] = useState(null); // 'none', 'pending', 'accepted', 'rejected'
  
  const [loading, setLoading] = useState(true);
  const [submittingInterest, setSubmittingInterest] = useState(false);

  const fetchDetails = async () => {
    setLoading(true);
    try {
      // Get property info
      const res = await api.get(`/listings/${id}`);
      setListing(res.data);

      // If user is a tenant, check interest status and compatibility
      if (user && user.role === 'tenant') {
        const compatRes = await api.get(`/tenant/compatibility/${id}`);
        setCompatScore(compatRes.data.compatibility);
        setInterestStatus(compatRes.data.interest_status || 'none');
      }
    } catch (err) {
      console.error(err);
      showToast("Failed to load listing details", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, [id, user]);

  // Express interest request submit
  const handleExpressInterest = async () => {
    if (!user) {
      showToast("Please sign in as a tenant to express interest", "warning");
      return;
    }
    
    setSubmittingInterest(true);
    try {
      await api.post(`/tenant/interest/${id}`);
      showToast("Interest request submitted successfully!", "success");
      setInterestStatus('pending');
    } catch (err) {
      console.error(err);
      showToast(err.response?.data?.error || "Failed to submit request", "error");
    } finally {
      setSubmittingInterest(false);
    }
  };

  if (loading) {
    return <LoadingSkeleton type="details" />;
  }

  if (!listing) {
    return (
      <div className="text-center py-20 space-y-4">
        <Home className="mx-auto text-slate-350" size={40} />
        <h3 className="font-extrabold text-base">Listing Not Found</h3>
        <p className="text-xs text-slate-400 font-medium">The listing you are trying to view does not exist or has been removed.</p>
        <Link to="/" className="inline-block text-xs font-black text-blue-600 hover:underline">Go Home</Link>
      </div>
    );
  }

  // Get image URL helper
  const getImageUrl = (imagePath) => {
    if (!imagePath) return null;
    return `http://127.0.0.1:5000/uploads/${imagePath.split('/').pop()}`;
  };

  return (
    <div className="space-y-8 py-2 max-w-5xl mx-auto animate-fade-in">
      
      {/* Back button */}
      <div>
        <Link 
          to={user?.role === 'owner' ? '/owner-dashboard' : '/tenant-dashboard'} 
          className="inline-flex items-center gap-1.5 text-xs font-extrabold text-slate-500 hover:text-slate-900 dark:hover:text-white"
        >
          <ArrowLeft size={16} />
          Back to Dashboard
        </Link>
      </div>

      {/* Main Grid content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Photos & Details */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Photo carousel/gallery */}
          <div className="bg-slate-900 rounded-3xl overflow-hidden aspect-video relative group shadow-lg">
            {listing.images && listing.images.length > 0 ? (
              <img 
                src={getImageUrl(listing.images[0].image_url)} 
                alt="Room" 
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center text-slate-500 space-y-2">
                <Home size={48} />
                <span className="text-xs font-bold">No Photos Provided</span>
              </div>
            )}
            
            {/* Rent badge */}
            <div className="absolute bottom-4 left-4 bg-white/95 dark:bg-slate-900/95 backdrop-blur px-4 py-2 rounded-2xl border border-slate-100 dark:border-slate-800/80 font-black text-sm text-slate-900 dark:text-white shadow">
              ${listing.rent_amount} <span className="text-[10px] text-slate-450 dark:text-slate-400 font-bold uppercase">/ month</span>
            </div>
          </div>

          {/* Core Info */}
          <div className="bg-white dark:bg-slate-800 p-6 sm:p-8 rounded-3xl border border-slate-100 dark:border-slate-700/50 shadow-sm space-y-4">
            
            <div className="space-y-1">
              <h1 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white truncate">
                {listing.address}
              </h1>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-bold uppercase">
                {listing.city}, {listing.state}
              </p>
            </div>

            {/* Price/Availability info tags */}
            <div className="grid grid-cols-2 gap-4 border-t border-b border-slate-50 dark:border-slate-700/50 py-4 text-xs font-bold text-slate-650 dark:text-slate-400">
              <div className="flex items-center gap-2">
                <DollarSign size={18} className="text-blue-550 dark:text-blue-400" />
                <div>
                  <span className="block text-[10px] text-slate-400 uppercase font-black">Monthly Rent</span>
                  <span>${listing.rent_amount}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Calendar size={18} className="text-pink-550 dark:text-pink-400" />
                <div>
                  <span className="block text-[10px] text-slate-400 uppercase font-black">Available From</span>
                  <span>{new Date(listing.available_from).toLocaleDateString([], { month: 'long', day: 'numeric', year: 'numeric' })}</span>
                </div>
              </div>
            </div>

            {/* Description */}
            {listing.description && (
              <div className="space-y-1">
                <h3 className="font-extrabold text-xs text-slate-900 dark:text-white uppercase tracking-wider">Description</h3>
                <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 leading-relaxed">
                  {listing.description}
                </p>
              </div>
            )}

            {/* Amenities badges */}
            {listing.amenities && listing.amenities.length > 0 && (
              <div className="space-y-2 pt-2">
                <h3 className="font-extrabold text-xs text-slate-900 dark:text-white uppercase tracking-wider">Amenities</h3>
                <div className="flex flex-wrap gap-2">
                  {listing.amenities.map((amenity) => (
                    <span 
                      key={amenity} 
                      className="px-3 py-1.5 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-700/80 text-[10px] font-extrabold text-slate-600 dark:text-slate-350"
                    >
                      {amenity}
                    </span>
                  ))}
                </div>
              </div>
            )}

          </div>

        </div>

        {/* Right Column: Compatibility & Actions */}
        <div className="space-y-6">
          
          {/* Tenant view: Compatibility analysis card */}
          {user?.role === 'tenant' && compatScore && (
            <div className="bg-white dark:bg-slate-800 p-6 rounded-3xl border border-slate-100 dark:border-slate-700/50 shadow-sm space-y-4">
              <h2 className="font-extrabold text-sm text-slate-900 dark:text-white border-b border-slate-50 dark:border-slate-700 pb-2">Compatibility Report</h2>
              
              {/* Score ring */}
              <div className="flex items-center gap-4">
                <div className={`w-14 h-14 rounded-full flex items-center justify-center font-black text-sm border-4 shadow-sm
                  ${compatScore.score >= 80 
                    ? 'bg-emerald-50 text-emerald-700 border-emerald-500/20 dark:bg-emerald-950/20 dark:text-emerald-400' 
                    : compatScore.score >= 60 
                      ? 'bg-amber-50 text-amber-700 border-amber-500/20 dark:bg-amber-950/20 dark:text-amber-450' 
                      : 'bg-rose-50 text-rose-700 border-rose-500/20 dark:bg-rose-950/20 dark:text-rose-450'}`}>
                  {compatScore.score}%
                </div>
                <div>
                  <span className="text-[10px] font-black uppercase text-slate-400 block tracking-wide">Overall Match Rating</span>
                  <span className="text-xs font-extrabold text-slate-700 dark:text-slate-205 leading-none">
                    {compatScore.score >= 80 ? 'Highly Compatible' : compatScore.score >= 60 ? 'Moderate Match' : 'Low Compatibility'}
                  </span>
                </div>
              </div>

              {/* Matching factors */}
              <div className="space-y-2 pt-2 text-[11px] font-bold text-slate-500 dark:text-slate-400 border-t border-slate-50 dark:border-slate-700">
                <div className="flex justify-between items-center">
                  <span>Budget Compatibility:</span>
                  <span className={compatScore.match_breakdown?.budget_match ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}>
                    {compatScore.match_breakdown?.budget_match ? 'Yes' : 'Over Budget'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Location Preference:</span>
                  <span className={compatScore.match_breakdown?.location_match ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400 dark:text-slate-500'}>
                    {compatScore.match_breakdown?.location_match ? 'Matched' : 'Unmatched'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Move-In Schedule:</span>
                  <span className={compatScore.match_breakdown?.date_match ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400 dark:text-slate-500'}>
                    {compatScore.match_breakdown?.date_match ? 'Aligned' : 'Different'}
                  </span>
                </div>
              </div>

              {/* AI scoring reasoning */}
              {compatScore.reasoning && (
                <div className="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-2xl border border-slate-100 dark:border-slate-700/80 space-y-1.5">
                  <div className="flex items-center gap-1.5 font-extrabold text-xs text-blue-600 dark:text-blue-400">
                    <Sparkles size={14} className="animate-pulse" />
                    <span>AI Matching Analysis</span>
                  </div>
                  <p className="text-[10px] font-semibold text-slate-505 dark:text-slate-400 leading-relaxed">
                    {compatScore.reasoning}
                  </p>
                </div>
              )}

            </div>
          )}

          {/* Action box: Express Interest / Chat access */}
          <div className="bg-white dark:bg-slate-800 p-6 rounded-3xl border border-slate-100 dark:border-slate-700/50 shadow-sm space-y-4">
            
            <h2 className="font-extrabold text-sm text-slate-900 dark:text-white border-b border-slate-50 dark:border-slate-700 pb-2">Express Interest</h2>
            
            {/* Show request button based on user.role */}
            {user?.role === 'tenant' ? (
              <div className="space-y-3">
                {interestStatus === 'none' && (
                  <button
                    onClick={handleExpressInterest}
                    disabled={submittingInterest}
                    className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-600 to-pink-500 hover:from-blue-500 hover:to-pink-400 font-black text-xs text-white transition-all flex items-center justify-center gap-1.5 shadow shadow-pink-500/10"
                  >
                    {submittingInterest ? <Loader2 size={16} className="animate-spin" /> : <Heart size={16} />}
                    Submit Interest Request
                  </button>
                )}

                {interestStatus === 'pending' && (
                  <div className="p-3 bg-blue-50/50 dark:bg-slate-900/50 border border-blue-150 rounded-xl text-center text-xs font-bold text-blue-700 dark:text-blue-400">
                    Interest Pending Owner Approval
                  </div>
                )}

                {interestStatus === 'accepted' && (
                  <div className="space-y-3">
                    <div className="p-3 bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-150 rounded-xl text-center text-xs font-bold text-emerald-700 dark:text-emerald-400 flex items-center justify-center gap-1.5">
                      <ShieldCheck size={16} />
                      Request Accepted!
                    </div>
                    <Link
                      to="/chat"
                      className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 font-black text-xs text-white transition-all flex items-center justify-center gap-1.5 shadow shadow-blue-500/10"
                    >
                      Go to Live Chat
                    </Link>
                  </div>
                )}

                {interestStatus === 'rejected' && (
                  <div className="p-3 bg-rose-50/50 dark:bg-rose-950/20 border border-rose-150 rounded-xl text-center text-xs font-bold text-rose-700 dark:text-rose-400">
                    Request Declined by Owner
                  </div>
                )}
              </div>
            ) : user?.role === 'owner' ? (
              <div className="p-4 bg-slate-50 dark:bg-slate-900/50 rounded-2xl border border-slate-100 dark:border-slate-700/80 text-center text-xs font-bold text-slate-500">
                You listed this property. Manage interest requests on your dashboard.
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-[11px] font-bold text-slate-400 text-center">You must be logged in as a tenant to express interest.</p>
                <Link
                  to="/login"
                  className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-600 to-pink-500 hover:from-blue-500 hover:to-pink-400 font-black text-xs text-white transition-all flex items-center justify-center gap-1.5 shadow shadow-pink-500/10"
                >
                  Sign In
                </Link>
              </div>
            )}

          </div>

        </div>

      </div>

    </div>
  );
};

export default ListingDetailsPage;
