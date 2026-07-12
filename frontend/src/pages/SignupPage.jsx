import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { Mail, Lock, Phone, Building, Loader2, UserPlus } from 'lucide-react';

const SignupPage = () => {
  const { registerUser } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  
  const [submitting, setSubmitting] = useState(false);
  const [selectedRole, setSelectedRole] = useState('tenant');

  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      email: '',
      password: '',
      role: 'tenant',
      company_name: '',
      contact_phone: ''
    }
  });

  const onSubmit = async (data) => {
    setSubmitting(true);
    const payload = {
      email: data.email,
      password: data.password,
      role: data.role
    };

    if (data.role === 'owner') {
      payload.company_name = data.company_name;
      payload.contact_phone = data.contact_phone;
    }

    const result = await registerUser(payload);
    setSubmitting(false);

    if (result.success) {
      showToast("Account created successfully! Please log in.", "success");
      navigate('/login');
    } else {
      showToast(result.error || "Registration failed", "error");
    }
  };

  return (
    <div className="min-h-[80vh] flex flex-col justify-center items-center py-12 px-4 sm:px-6 lg:px-8">
      
      <div className="max-w-md w-full bg-white dark:bg-slate-800 p-8 rounded-3xl border border-slate-100 dark:border-slate-700/50 shadow-2xl space-y-6">
        
        {/* Header */}
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-black text-slate-900 dark:text-white">Create Account</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Join our community to find rooms and roommate matches.</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          
          {/* Email field */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-600 dark:text-slate-300 block">Email Address</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400 dark:text-slate-500 pointer-events-none">
                <Mail size={16} />
              </span>
              <input
                type="email"
                placeholder="you@example.com"
                className={`w-full pl-10 pr-4 py-2.5 rounded-xl border bg-slate-50 dark:bg-slate-900/50 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all
                  ${errors.email ? 'border-rose-500 focus:ring-rose-500/20 focus:border-rose-500' : 'border-slate-200 dark:border-slate-700'}`}
                {...register('email', { 
                  required: 'Email is required',
                  pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: 'Invalid email address' }
                })}
              />
            </div>
            {errors.email && <span className="text-[10px] text-rose-500 font-bold">{errors.email.message}</span>}
          </div>

          {/* Password field */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-600 dark:text-slate-300 block">Password</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400 dark:text-slate-500 pointer-events-none">
                <Lock size={16} />
              </span>
              <input
                type="password"
                placeholder="••••••••"
                className={`w-full pl-10 pr-4 py-2.5 rounded-xl border bg-slate-50 dark:bg-slate-900/50 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all
                  ${errors.password ? 'border-rose-500 focus:ring-rose-500/20' : 'border-slate-200 dark:border-slate-700'}`}
                {...register('password', { 
                  required: 'Password is required',
                  minLength: { value: 6, message: 'Password must be at least 6 characters' }
                })}
              />
            </div>
            {errors.password && <span className="text-[10px] text-rose-500 font-bold">{errors.password.message}</span>}
          </div>

          {/* Role selection */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-600 dark:text-slate-300 block">I am a...</label>
            <div className="grid grid-cols-2 gap-3">
              <label 
                className={`flex justify-center items-center py-2.5 rounded-xl border font-bold text-sm cursor-pointer transition-all
                  ${selectedRole === 'tenant' 
                    ? 'bg-blue-50 border-blue-500 text-blue-700 dark:bg-slate-800 dark:text-blue-400' 
                    : 'border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'}`}
              >
                <input
                  type="radio"
                  value="tenant"
                  className="sr-only"
                  {...register('role', { 
                    onChange: (e) => setSelectedRole(e.target.value) 
                  })}
                />
                Tenant
              </label>

              <label 
                className={`flex justify-center items-center py-2.5 rounded-xl border font-bold text-sm cursor-pointer transition-all
                  ${selectedRole === 'owner' 
                    ? 'bg-blue-50 border-blue-500 text-blue-700 dark:bg-slate-800 dark:text-blue-400' 
                    : 'border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'}`}
              >
                <input
                  type="radio"
                  value="owner"
                  className="sr-only"
                  {...register('role', { 
                    onChange: (e) => setSelectedRole(e.target.value) 
                  })}
                />
                Property Owner
              </label>
            </div>
          </div>

          {/* Conditional Owner fields */}
          {selectedRole === 'owner' && (
            <div className="space-y-4 pt-2 border-t border-slate-100 dark:border-slate-700/50 animate-fade-in">
              
              {/* Contact phone */}
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-600 dark:text-slate-300 block">Contact Phone Number</label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400 dark:text-slate-500 pointer-events-none">
                    <Phone size={16} />
                  </span>
                  <input
                    type="text"
                    placeholder="+1 (234) 567-890"
                    className={`w-full pl-10 pr-4 py-2.5 rounded-xl border bg-slate-50 dark:bg-slate-900/50 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20
                      ${errors.contact_phone ? 'border-rose-500 focus:ring-rose-500/20' : 'border-slate-200 dark:border-slate-700'}`}
                    {...register('contact_phone', { required: 'Phone number is required for property owners' })}
                  />
                </div>
                {errors.contact_phone && <span className="text-[10px] text-rose-500 font-bold">{errors.contact_phone.message}</span>}
              </div>

              {/* Company name */}
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-600 dark:text-slate-300 block">Company Name (Optional)</label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400 dark:text-slate-500 pointer-events-none">
                    <Building size={16} />
                  </span>
                  <input
                    type="text"
                    placeholder="e.g. Dream Homes LLC"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                    {...register('company_name')}
                  />
                </div>
              </div>

            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={submitting}
            className="w-full mt-4 py-3 px-4 rounded-xl bg-gradient-to-r from-blue-600 to-pink-500 hover:from-blue-500 hover:to-pink-400 font-extrabold text-sm text-white transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {submitting ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Creating Account...
              </>
            ) : (
              <>
                <UserPlus size={16} />
                Sign Up
              </>
            )}
          </button>
        </form>

        <hr className="border-slate-100 dark:border-slate-700" />

        {/* Footer Link */}
        <div className="text-center text-xs text-slate-500 dark:text-slate-400 font-medium">
          Already have an account?{' '}
          <Link to="/login" className="font-extrabold text-pink-600 dark:text-pink-400 hover:underline">
            Sign In
          </Link>
        </div>

      </div>

    </div>
  );
};

export default SignupPage;
