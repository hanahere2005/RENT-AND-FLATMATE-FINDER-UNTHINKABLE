import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { 
  Home, Plus, User, Sparkles, Check, X, Phone, Calendar, 
  MapPin, Loader2, List, EyeOff, LayoutDashboard, CheckSquare 
} from 'lucide-react';
import api from '../services/api';
import ListingCard from '../components/ListingCard';

const OwnerDashboard = () => {
  const { user } = useAuth();
  const { showToast } = useToast();
  
  const [activeSection, setActiveSection] = useState('listings'); // 'listings', 'create', 'requests'
  const [listings, setListings] = useState([]);
  const [requests, setRequests] = useState([]);
  
  const [loadingListings, setLoadingListings] = useState(true);
  const [loadingRequests, setLoadingRequests] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  // New room listing form fields
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [address, setAddress] = useState('');
  const [rentAmount, setRentAmount] = useState('');
  const [availableFrom, setAvailableFrom] = useState('');
  const [roomType, setRoomType] = useState('single');
  const [furnishingStatus, setFurnishingStatus] = useState('fully-furnished');
  const [contactInfo, setContactInfo] = useState('');
  const [amenities, setAmenities] = useState('');
  const [selectedFiles, setSelectedFiles] = useState([]);

  // Fetch owner's listing properties
  const fetchListings = async () => {
    setLoadingListings(true);
    try {
      const res = await api.get('/owner/listings');
      setListings(res.data || []);
    } catch (err) {
      console.error(err);
      showToast("Failed to load your listings", "error");
    } fill: {
      setLoadingListings(false);
    }
  };

  // Fetch incoming tenant interest requests
  const fetchRequests = async () => {
    setLoadingRequests(true);
    try {
      const res = await api.get('/owner/requests');
      setRequests(res.data || []);
    } catch (err) {
      console.error(err);
      showToast("Failed to load tenant requests", "error");
    } fill: {
      setLoadingRequests(false);
    }
  };

  useEffect(() => {
    fetchListings();
    fetchRequests();
  }, []);

  const handleFileChange = (e) => {
    setSelectedFiles(Array.from(e.target.files));
  };

  // Handle post listing submit
  const handleCreateListing = async (e) => {
    e.preventDefault();
    if (!title || !address || !city || !state || !rentAmount || !availableFrom || !contactInfo) {
      showToast("Please fill in all required fields", "warning");
      return;
    }

    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('title', title);
      formData.append('description', description);
      formData.append('location', `${city}, ${state}`);
      formData.append('address', address);
      formData.append('rent', rentAmount);
      formData.append('available_from', availableFrom);
      formData.append('room_type', roomType);
      formData.append('furnishing_status', furnishingStatus);
      formData.append('contact_info', contactInfo);
      
      const amenitiesArr = amenities.split(',').map(item => item.trim()).filter(Boolean);
      formData.append('amenities', JSON.stringify(amenitiesArr));

      // Append multi-files
      selectedFiles.forEach((file) => {
        formData.append('images', file);
      });

      await api.post('/listings', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      showToast("Room listing posted successfully!", "success");
      
      // Reset form fields
      setTitle('');
      setDescription('');
      setCity('');
      setState('');
      setAddress('');
      setRentAmount('');
      setAvailableFrom('');
      setRoomType('single');
      setFurnishingStatus('fully-furnished');
      setContactInfo('');
      setAmenities('');
      setSelectedFiles([]);
      
      fetchListings();
      setActiveSection('listings');
    } catch (err) {
      console.error(err);
      showToast(err.response?.data?.error || "Failed to create listing", "error");
    } finally {
      setSubmitting(false);
    }
  };

  // Accept/Reject interest requests
  const handleRequestAction = async (requestId, status) => {
    try {
      await api.put(`/owner/requests/${requestId}`, { status });
      showToast(`Request successfully ${status}!`, "success");
      fetchRequests();
    } catch (err) {
      console.error(err);
      showToast("Failed to update request status", "error");
    }
  };

  // Deactivate filled property listings
  const handleToggleListingStatus = async (listingId, currentStatus) => {
    try {
      await api.put(`/listings/${listingId}`, { is_active: !currentStatus });
      showToast(`Property status updated successfully!`, "success");
      fetchListings();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8 py-2 animate-fade-in">
      
      {/* Welcome Banner */}
      <section className="bg-slate-900 rounded-3xl p-6 sm:p-8 text-white relative overflow-hidden shadow-lg">
        <div className="absolute top-0 right-0 w-64 h-64 bg-pink-500/10 rounded-full blur-3xl -translate-y-12 translate-x-12"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-500/15 rounded-full blur-3xl translate-y-12 -translate-x-12"></div>
        
        <div className="relative flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="space-y-2">
            <h1 className="text-2xl sm:text-3xl font-black">Owner Control Center</h1>
            <p className="text-xs text-slate-300 font-semibold max-w-md leading-relaxed">
              Post listings, upload photos, and review compatibility scores for incoming tenant interest requests.
            </p>
          </div>
          
          <button
            onClick={() => setActiveSection(activeSection === 'create' ? 'listings' : 'create')}
            className="flex-shrink-0 flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-pink-500 hover:from-blue-500 hover:to-pink-400 text-white font-extrabold text-xs shadow-lg shadow-pink-500/15 transition-all transform hover:-translate-y-0.5"
          >
            {activeSection === 'create' ? (
              <>
                <List size={16} />
                Show Listings
              </>
            ) : (
              <>
                <Plus size={16} />
                Post Room
              </>
            )}
          </button>
        </div>
      </section>

      {/* Navigation tabs */}
      <section className="flex border-b border-slate-100 dark:border-slate-800">
        <button
          onClick={() => setActiveSection('listings')}
          className={`px-4 py-2.5 font-bold text-xs border-b-2 transition-all
            ${activeSection === 'listings' 
              ? 'border-blue-500 text-blue-600 dark:text-blue-400' 
              : 'border-transparent text-slate-400 hover:text-slate-900 dark:hover:text-white'}`}
        >
          My Listings ({listings.length})
        </button>
        <button
          onClick={() => setActiveSection('requests')}
          className={`px-4 py-2.5 font-bold text-xs border-b-2 transition-all relative
            ${activeSection === 'requests' 
              ? 'border-blue-500 text-blue-600 dark:text-blue-400' 
              : 'border-transparent text-slate-400 hover:text-slate-900 dark:hover:text-white'}`}
        >
          Incoming Interests ({requests.filter(r => r.status === 'pending').length})
          {requests.filter(r => r.status === 'pending').length > 0 && (
            <span className="absolute top-1.5 right-0.5 w-2 h-2 rounded-full bg-pink-650"></span>
          )}
        </button>
      </section>

      {/* Main Switch sections */}
      <section>
        
        {/* Listings Grid */}
        {activeSection === 'listings' && (
          loadingListings ? (
            <div className="flex justify-center py-12">
              <Loader2 className="animate-spin text-blue-600" size={28} />
            </div>
          ) : listings.length === 0 ? (
            <div className="text-center py-20 bg-white dark:bg-slate-800 rounded-3xl border border-slate-100 dark:border-slate-700/50 space-y-3 shadow-sm">
              <Home size={40} className="mx-auto text-slate-300 dark:text-slate-655" />
              <h3 className="font-extrabold text-base text-slate-905 dark:text-white">No Listings Yet</h3>
              <p className="text-xs text-slate-450 dark:text-slate-400 max-w-xs mx-auto font-medium leading-relaxed">
                Click "Post Room" above to list your properties and find roommate matches.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {listings.map((listing) => (
                <div key={listing.id} className="relative group">
                  <ListingCard listing={listing} />
                  
                  {/* Status Toggle overlay banner */}
                  <div className="absolute top-3 right-3 z-10">
                    <button
                      onClick={() => handleToggleListingStatus(listing.id, listing.is_active)}
                      className={`px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-wider transition-all shadow-md
                        ${listing.is_active 
                          ? 'bg-white hover:bg-slate-50 text-slate-700 border border-slate-100' 
                          : 'bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-100'}`}
                    >
                      {listing.is_active ? 'Active (Click to Close)' : 'Closed (Click to Open)'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )
        )}

        {/* Requests List */}
        {activeSection === 'requests' && (
          loadingRequests ? (
            <div className="flex justify-center py-12">
              <Loader2 className="animate-spin text-blue-600" size={28} />
            </div>
          ) : requests.length === 0 ? (
            <div className="text-center py-20 bg-white dark:bg-slate-800 rounded-3xl border border-slate-100 dark:border-slate-700/50 space-y-3 shadow-sm">
              <CheckSquare size={40} className="mx-auto text-slate-300 dark:text-slate-655" />
              <h3 className="font-extrabold text-base text-slate-905 dark:text-white">No Incoming Requests</h3>
              <p className="text-xs text-slate-450 dark:text-slate-400 max-w-xs mx-auto font-medium leading-relaxed">
                Tenant requests and high compatibility alerts will pop up here once they express interest.
              </p>
            </div>
          ) : (
            <div className="space-y-4 max-w-4xl">
              {requests.map((req) => {
                const compat = req.compatibility;
                
                return (
                  <div 
                    key={req.id} 
                    className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm flex flex-col md:flex-row justify-between gap-6 transition-all hover:shadow-md"
                  >
                    {/* Tenant preference breakdown */}
                    <div className="space-y-3 flex-grow">
                      
                      {/* Badge header */}
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-extrabold text-sm text-slate-900 dark:text-white truncate max-w-[200px]">
                          {req.tenant_email}
                        </span>
                        <span className="text-[10px] font-bold text-slate-400">expressed interest in</span>
                        <span className="text-xs font-black text-blue-600 dark:text-blue-400 underline">
                          {req.listing_address}
                        </span>
                      </div>

                      {/* Bio */}
                      {req.tenant_profile?.bio && (
                        <p className="text-xs font-semibold text-slate-505 dark:text-slate-400 bg-slate-50/50 dark:bg-slate-900/20 p-3 rounded-xl border border-slate-100/50 dark:border-slate-700/30 italic">
                          "{req.tenant_profile.bio}"
                        </p>
                      )}

                      {/* Details row */}
                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-[11px] font-bold text-slate-450 dark:text-slate-400">
                        <div className="flex items-center gap-1.5">
                          <Calendar size={14} className="text-slate-400" />
                          <span>Move-in: {req.tenant_profile?.move_in_date || 'Flexible'}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <Plus size={14} className="text-slate-400" />
                          <span>Budget: ${req.tenant_profile?.budget_min}-${req.tenant_profile?.budget_max}/mo</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <User size={14} className="text-slate-400" />
                          <span>Habits: {req.tenant_profile?.lifestyle_habits?.join(', ') || 'N/A'}</span>
                        </div>
                      </div>

                    </div>

                    {/* Compatibility Score & Actions */}
                    <div className="flex flex-col sm:flex-row md:flex-col items-center justify-center gap-4 border-t sm:border-t-0 md:border-t-0 md:border-l border-slate-100 dark:border-slate-700/50 pt-4 sm:pt-0 md:pt-4 md:pl-6 md:w-48 flex-shrink-0">
                      
                      {/* Score Indicator */}
                      <div className="text-center">
                        <span className="text-[10px] font-black uppercase text-slate-400 block tracking-wider mb-1">Compatibility</span>
                        <div className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-xl font-black text-xs shadow-sm
                          ${compat?.score >= 80 
                            ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/20 dark:text-emerald-400' 
                            : compat?.score >= 60 
                              ? 'bg-amber-50 text-amber-700 dark:bg-amber-950/20 dark:text-amber-450' 
                              : 'bg-rose-50 text-rose-700 dark:bg-rose-950/20 dark:text-rose-400'}`}>
                          <Sparkles size={14} className="animate-pulse" />
                          <span>{compat?.score}% Match</span>
                        </div>
                      </div>

                      {/* Action buttons */}
                      <div className="flex gap-2 w-full justify-center">
                        {req.status === 'pending' ? (
                          <>
                            <button
                              onClick={() => handleRequestAction(req.id, 'accepted')}
                              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 font-bold text-xs text-white transition-all flex items-center gap-1 shadow shadow-emerald-500/10"
                            >
                              <Check size={14} />
                              Accept
                            </button>
                            <button
                              onClick={() => handleRequestAction(req.id, 'rejected')}
                              className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 font-bold text-xs text-white transition-all flex items-center gap-1 shadow shadow-rose-500/10"
                            >
                              <X size={14} />
                              Decline
                            </button>
                          </>
                        ) : (
                          <span className={`text-xs font-black uppercase tracking-wider
                            ${req.status === 'accepted' ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-450'}`}>
                            {req.status}
                          </span>
                        )}
                      </div>

                    </div>

                  </div>
                );
              })}
            </div>
          )
        )}

        {/* Create Listing Form */}
        {activeSection === 'create' && (
          <div className="bg-white dark:bg-slate-800 p-6 sm:p-8 rounded-3xl border border-slate-100 dark:border-slate-700/50 shadow-sm max-w-3xl">
            <form onSubmit={handleCreateListing} className="space-y-6">
              <h2 className="font-extrabold text-base text-slate-900 dark:text-white border-b border-slate-50 dark:border-slate-700 pb-3">Post Property Details</h2>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                
                {/* Title */}
                <div className="sm:col-span-3 space-y-1">
                  <label className="text-xs font-bold text-slate-650 dark:text-slate-350 block">Listing Title *</label>
                  <input
                    type="text"
                    placeholder="e.g. Spacious Room in Cozy Shared Apartment"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full px-4 py-2 rounded-xl border border-slate-205 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                    required
                  />
                </div>

                {/* Street address */}
                <div className="sm:col-span-3 space-y-1">
                  <label className="text-xs font-bold text-slate-650 dark:text-slate-350 block">Street Address *</label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400 pointer-events-none">
                      <MapPin size={16} />
                    </span>
                    <input
                      type="text"
                      placeholder="e.g. 123 Main St, Apt 4B"
                      value={address}
                      onChange={(e) => setAddress(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                      required
                    />
                  </div>
                </div>

                {/* City */}
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-650 dark:text-slate-350 block">City *</label>
                  <input
                    type="text"
                    placeholder="e.g. San Francisco"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    className="w-full px-4 py-2 rounded-xl border border-slate-202 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                    required
                  />
                </div>

                {/* State */}
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-655 dark:text-slate-350 block">State *</label>
                  <input
                    type="text"
                    placeholder="e.g. CA"
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                    className="w-full px-4 py-2 rounded-xl border border-slate-202 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                    required
                  />
                </div>

                {/* Rent amount */}
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-650 dark:text-slate-350 block">Monthly Rent ($) *</label>
                  <input
                    type="number"
                    placeholder="e.g. 1200"
                    value={rentAmount}
                    onChange={(e) => setRentAmount(e.target.value)}
                    className="w-full px-4 py-2 rounded-xl border border-slate-202 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                    required
                  />
                </div>

                {/* Available from */}
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-650 dark:text-slate-355 block">Available From *</label>
                  <input
                    type="date"
                    value={availableFrom}
                    onChange={(e) => setAvailableFrom(e.target.value)}
                    className="w-full px-4 py-2 rounded-xl border border-slate-202 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                    required
                  />
                </div>

                {/* Room Type */}
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-650 dark:text-slate-350 block">Room Type *</label>
                  <select
                    value={roomType}
                    onChange={(e) => setRoomType(e.target.value)}
                    className="w-full px-4 py-2 rounded-xl border border-slate-202 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                    required
                  >
                    <option value="single">Single Room</option>
                    <option value="shared">Shared Room</option>
                    <option value="entire_flat">Entire Flat</option>
                  </select>
                </div>

                {/* Furnishing Status */}
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-655 dark:text-slate-350 block">Furnishing *</label>
                  <select
                    value={furnishingStatus}
                    onChange={(e) => setFurnishingStatus(e.target.value)}
                    className="w-full px-4 py-2 rounded-xl border border-slate-202 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                    required
                  >
                    <option value="unfurnished">Unfurnished</option>
                    <option value="semi-furnished">Semi-Furnished</option>
                    <option value="fully-furnished">Fully Furnished</option>
                  </select>
                </div>

                {/* Contact Info */}
                <div className="sm:col-span-2 space-y-1">
                  <label className="text-xs font-bold text-slate-650 dark:text-slate-350 block">Contact Phone / Info *</label>
                  <input
                    type="text"
                    placeholder="e.g. +1 (555) 019-2834 or owner@email.com"
                    value={contactInfo}
                    onChange={(e) => setContactInfo(e.target.value)}
                    className="w-full px-4 py-2 rounded-xl border border-slate-202 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                    required
                  />
                </div>

                {/* Amenities */}
                <div className="sm:col-span-2 space-y-1">
                  <label className="text-xs font-bold text-slate-655 dark:text-slate-350 block">Amenities (comma-separated)</label>
                  <input
                    type="text"
                    placeholder="e.g. Private Bath, WiFi, Gym, AC"
                    value={amenities}
                    onChange={(e) => setAmenities(e.target.value)}
                    className="w-full px-4 py-2 rounded-xl border border-slate-202 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                </div>

                {/* Description */}
                <div className="sm:col-span-3 space-y-1">
                  <label className="text-xs font-bold text-slate-655 dark:text-slate-350 block">Property Description</label>
                  <textarea
                    rows={4}
                    placeholder="Provide details about the room size, roommates, apartment rules..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-202 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                </div>

                {/* Photos */}
                <div className="sm:col-span-3 space-y-1">
                  <label className="text-xs font-bold text-slate-655 dark:text-slate-355 block">Upload Property Photos</label>
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleFileChange}
                    className="w-full text-xs font-bold text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-extrabold file:bg-blue-50 file:text-blue-700 dark:file:bg-slate-900 dark:file:text-blue-400 file:cursor-pointer"
                  />
                </div>

              </div>

              {/* Submit */}
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-pink-500 hover:from-blue-500 hover:to-pink-400 font-extrabold text-xs text-white transition-all flex items-center gap-2 disabled:opacity-50"
                >
                  {submitting ? (
                    <>
                      <Loader2 size={14} className="animate-spin" />
                      Posting Listing...
                    </>
                  ) : (
                    <>
                      <Plus size={14} />
                      Post Listing
                    </>
                  )}
                </button>
              </div>

            </form>
          </div>
        )}

      </section>

    </div>
  );
};

export default OwnerDashboard;
