import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { User, Mail, Shield, Phone, Building, Calendar, DollarSign, MapPin, Loader2, Save } from 'lucide-react';
import api from '../services/api';
import LoadingSkeleton from '../components/LoadingSkeleton';

const ProfilePage = () => {
  const { user, profile, updateProfileState } = useAuth();
  const { showToast } = useToast();
  
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const { register, handleSubmit, reset, formState: { errors } } = useForm();

  useEffect(() => {
    if (user) {
      // Setup default form fields based on whether tenant or owner profile details exist
      const defaults = {
        email: user.email,
        role: user.role
      };

      if (user.role === 'tenant' && profile) {
        defaults.preferred_locations = profile.preferred_locations?.join(', ') || '';
        defaults.budget_min = profile.budget_min || '';
        defaults.budget_max = profile.budget_max || '';
        defaults.move_in_date = profile.move_in_date || '';
        defaults.lifestyle_habits = profile.lifestyle_habits?.join(', ') || '';
        defaults.bio = profile.bio || '';
      } else if (user.role === 'owner' && profile) {
        defaults.contact_phone = profile.contact_phone || '';
        defaults.company_name = profile.company_name || '';
      }
      
      reset(defaults);
      setLoading(false);
    }
  }, [user, profile, reset]);

  const onSubmit = async (data) => {
    setSubmitting(true);
    try {
      let res;
      if (user.role === 'tenant') {
        const payload = {
          preferred_locations: data.preferred_locations.split(',').map(s => s.trim()).filter(Boolean),
          budget_min: Number(data.budget_min),
          budget_max: Number(data.budget_max),
          move_in_date: data.move_in_date,
          lifestyle_habits: data.lifestyle_habits.split(',').map(s => s.trim()).filter(Boolean),
          bio: data.bio
        };
        res = await api.put('/tenant/profile', payload);
      } else if (user.role === 'owner') {
        const payload = {
          contact_phone: data.contact_phone,
          company_name: data.company_name
        };
        res = await api.put('/owner/profile', payload);
      }

      if (res && res.data) {
        updateProfileState(res.data.profile);
        showToast("Profile updated successfully!", "success");
      }
    } catch (err) {
      console.error(err);
      showToast("Failed to update profile", "error");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <LoadingSkeleton type="profile" />;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-4 animate-fade-in">
      
      {/* Decorative Header Block */}
      <div className="relative rounded-3xl h-36 bg-gradient-to-r from-blue-600 to-pink-500 overflow-hidden shadow-md">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-2xl -translate-y-8 translate-x-8"></div>
        <div className="absolute bottom-6 left-8 flex items-center gap-4 text-white">
          <div className="w-16 h-16 rounded-2xl bg-white/20 backdrop-blur-md flex items-center justify-center font-black text-2xl border border-white/20">
            {user.email.substring(0, 1).toUpperCase()}
          </div>
          <div>
            <h1 className="font-extrabold text-lg leading-none">{user.email}</h1>
            <span className="text-[10px] font-black uppercase text-pink-200 mt-1 block tracking-wider">
              {user.role} Account
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Core details column */}
        <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm h-fit space-y-4">
          <h2 className="font-extrabold text-sm text-slate-900 dark:text-white border-b border-slate-50 dark:border-slate-700 pb-2">Account Meta</h2>
          
          <div className="space-y-3 text-xs font-semibold text-slate-600 dark:text-slate-400">
            <div className="flex items-center gap-2">
              <Mail size={16} className="text-slate-400" />
              <span className="truncate">{user.email}</span>
            </div>
            <div className="flex items-center gap-2">
              <Shield size={16} className="text-slate-400" />
              <span className="capitalize">{user.role} role access</span>
            </div>
          </div>
        </div>

        {/* Profile form column */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-800 p-6 sm:p-8 rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <h2 className="font-extrabold text-base text-slate-900 dark:text-white border-b border-slate-50 dark:border-slate-700 pb-3">
              Configure {user.role === 'tenant' ? 'Roommate Preferences' : 'Contact Details'}
            </h2>

            {user.role === 'tenant' ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                
                {/* Preferred locations */}
                <div className="sm:col-span-2 space-y-1">
                  <label className="text-xs font-bold text-slate-600 dark:text-slate-300 block">Preferred Cities / Neighborhoods</label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400 dark:text-slate-500 pointer-events-none">
                      <MapPin size={16} />
                    </span>
                    <input
                      type="text"
                      placeholder="e.g. San Francisco, Oakland, Berkeley"
                      className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                      {...register('preferred_locations')}
                    />
                  </div>
                  <span className="text-[10px] text-slate-400 font-bold block">Comma-separated values</span>
                </div>

                {/* Min budget */}
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-600 dark:text-slate-300 block">Min Monthly Budget ($)</label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400 dark:text-slate-500 pointer-events-none">
                      <DollarSign size={16} />
                    </span>
                    <input
                      type="number"
                      placeholder="e.g. 500"
                      className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                      {...register('budget_min')}
                    />
                  </div>
                </div>

                {/* Max budget */}
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-600 dark:text-slate-300 block">Max Monthly Budget ($)</label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400 dark:text-slate-500 pointer-events-none">
                      <DollarSign size={16} />
                    </span>
                    <input
                      type="number"
                      placeholder="e.g. 1500"
                      className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                      {...register('budget_max')}
                    />
                  </div>
                </div>

                {/* Move-in date */}
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-600 dark:text-slate-300 block">Target Move-in Date</label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400 dark:text-slate-500 pointer-events-none">
                      <Calendar size={16} />
                    </span>
                    <input
                      type="date"
                      className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                      {...register('move_in_date')}
                    />
                  </div>
                </div>

                {/* Lifestyle Habits */}
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-600 dark:text-slate-300 block">Lifestyle Habits</label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400 dark:text-slate-500 pointer-events-none">
                      <User size={16} />
                    </span>
                    <input
                      type="text"
                      placeholder="e.g. non-smoker, clean, quiet"
                      className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                      {...register('lifestyle_habits')}
                    />
                  </div>
                  <span className="text-[10px] text-slate-400 font-bold block">Comma-separated habits</span>
                </div>

                {/* Bio bio */}
                <div className="sm:col-span-2 space-y-1">
                  <label className="text-xs font-bold text-slate-600 dark:text-slate-300 block">Introduce Yourself (Bio)</label>
                  <textarea
                    rows={4}
                    placeholder="Tell potential room owners who you are, what you do, and what type of shared flat you want..."
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                    {...register('bio')}
                  />
                </div>

              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                
                {/* Phone */}
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-600 dark:text-slate-300 block">Contact Phone Number</label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400 dark:text-slate-500 pointer-events-none">
                      <Phone size={16} />
                    </span>
                    <input
                      type="text"
                      placeholder="+1 (234) 567-890"
                      className={`w-full pl-10 pr-4 py-2 rounded-xl border bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500
                        ${errors.contact_phone ? 'border-rose-500 focus:ring-rose-500/20' : 'border-slate-200 dark:border-slate-700'}`}
                      {...register('contact_phone', { required: 'Phone number is required' })}
                    />
                  </div>
                  {errors.contact_phone && <span className="text-[10px] text-rose-500 font-bold">{errors.contact_phone.message}</span>}
                </div>

                {/* Company name */}
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-600 dark:text-slate-300 block">Company / Agency Name (Optional)</label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400 dark:text-slate-500 pointer-events-none">
                      <Building size={16} />
                    </span>
                    <input
                      type="text"
                      placeholder="e.g. Apex Properties LLC"
                      className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                      {...register('company_name')}
                    />
                  </div>
                </div>

              </div>
            )}

            {/* Save trigger */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={submitting}
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-pink-500 hover:from-blue-500 hover:to-pink-400 font-extrabold text-xs text-white transition-all flex items-center gap-2 disabled:opacity-50 shadow-md shadow-pink-500/10"
              >
                {submitting ? (
                  <>
                    <Loader2 size={14} className="animate-spin" />
                    Saving Changes...
                  </>
                ) : (
                  <>
                    <Save size={14} />
                    Save Settings
                  </>
                )}
              </button>
            </div>

          </form>
        </div>

      </div>

    </div>
  );
};

export default ProfilePage;
