import React, { createContext, useContext, useState, useCallback } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

const ToastContext = createContext();

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((message, type = 'info', duration = 4000) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { id, message, type, duration }]);
    
    setTimeout(() => {
      removeToast(id);
    }, duration);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {/* Toast Portal/Wrapper */}
      <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-3 max-w-sm w-full pointer-events-none">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`pointer-events-auto flex items-start gap-3 p-4 rounded-xl shadow-2xl border backdrop-blur-md transform transition-all duration-300 translate-y-0 opacity-100 animate-slide-in
              ${
                toast.type === 'success'
                  ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-800 dark:text-emerald-300'
                  : toast.type === 'error'
                  ? 'bg-rose-500/10 border-rose-500/20 text-rose-800 dark:text-rose-300'
                  : toast.type === 'warning'
                  ? 'bg-amber-500/10 border-amber-500/20 text-amber-800 dark:text-amber-300'
                  : 'bg-blue-500/10 border-blue-500/20 text-blue-800 dark:text-blue-300'
              }`}
          >
            <div className="flex-shrink-0 mt-0.5">
              {toast.type === 'success' && <CheckCircle size={20} className="text-emerald-500" />}
              {toast.type === 'error' && <AlertCircle size={20} className="text-rose-500" />}
              {toast.type === 'warning' && <AlertTriangle size={20} className="text-amber-500" />}
              {toast.type === 'info' && <Info size={20} className="text-blue-500" />}
            </div>
            <div className="flex-grow text-sm font-medium">{toast.message}</div>
            <button
              onClick={() => removeToast(toast.id)}
              className="flex-shrink-0 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
            >
              <X size={16} />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};
