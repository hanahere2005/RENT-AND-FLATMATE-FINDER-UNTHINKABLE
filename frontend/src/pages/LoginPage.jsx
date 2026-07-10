import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { Mail, Lock, Loader2, LogIn } from 'lucide-react';

const LoginPage = () => {
  const { login } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      email: '',
      password: ''
    }
  });

  const onSubmit = async (data) => {
    setSubmitting(true);
    const result = await login(data.email, data.password);
    setSubmitting(false);

    if (result.success) {
      showToast("Signed in successfully!", "success");
      // Check auth profile details and redirect accordingly
      const userRes = await login(data.email, data.password); 
      
      const userToken = localStorage.getItem('token');
      if (userToken) {
        try {
          const payload = JSON.parse(atob(userToken.split('.')[1]));
          const role = payload.role;
          if (role === 'admin') navigate('/admin-dashboard');
          else if (role === 'owner') navigate('/owner-dashboard');
          else navigate('/tenant-dashboard');
        } catch (e) {
          navigate('/');
        }
      }
    } else {
      showToast(result.error || "Invalid credentials", "error");
    }
  };

  return (
    <div className="min-h-[80vh] flex flex-col justify-center items-center py-12 px-4 sm:px-6 lg:px-8">
      
      <div className="max-w-md w-full bg-white dark:bg-slate-800 p-8 rounded-3xl border border-slate-100 dark:border-slate-700/50 shadow-2xl space-y-6">
        
        {/* Header */}
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-black text-slate-900 dark:text-white">Welcome Back</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Log in to search properties and connect with users.</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          
          {/* Email field */}
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-650 dark:text-slate-350 block">Email Address</label>
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
            <label className="text-xs font-bold text-slate-650 dark:text-slate-350 block">Password</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400 dark:text-slate-500 pointer-events-none">
                <Lock size={16} />
              </span>
              <input
                type="password"
                placeholder="••••••••"
                className={`w-full pl-10 pr-4 py-2.5 rounded-xl border bg-slate-50 dark:bg-slate-900/50 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all
                  ${errors.password ? 'border-rose-500 focus:ring-rose-500/20' : 'border-slate-200 dark:border-slate-700'}`}
                {...register('password', { required: 'Password is required' })}
              />
            </div>
            {errors.password && <span className="text-[10px] text-rose-500 font-bold">{errors.password.message}</span>}
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={submitting}
            className="w-full mt-2 py-3 px-4 rounded-xl bg-gradient-to-r from-blue-600 to-pink-500 hover:from-blue-500 hover:to-pink-400 font-extrabold text-sm text-white transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {submitting ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Signing In...
              </>
            ) : (
              <>
                <LogIn size={16} />
                Sign In
              </>
            )}
          </button>
        </form>

        <hr className="border-slate-100 dark:border-slate-700" />

        {/* Footer Link */}
        <div className="text-center text-xs text-slate-500 dark:text-slate-400 font-medium">
          Don't have an account?{' '}
          <Link to="/signup" className="font-extrabold text-pink-600 dark:text-pink-450 hover:underline">
            Sign Up
          </Link>
        </div>

      </div>

    </div>
  );
};

export default LoginPage;
