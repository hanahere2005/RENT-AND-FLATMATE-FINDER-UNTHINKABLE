import React from 'react';

const LoadingSkeleton = ({ type = 'card', count = 1 }) => {
  const cards = Array.from({ length: count });

  if (type === 'card') {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 w-full">
        {cards.map((_, i) => (
          <div key={i} className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm p-5 space-y-4 animate-pulse">
            {/* Image placeholder */}
            <div className="h-48 bg-slate-200 dark:bg-slate-700 rounded-xl w-full"></div>
            {/* Title / Badges */}
            <div className="flex gap-2">
              <div className="h-5 bg-slate-200 dark:bg-slate-700 rounded w-16"></div>
              <div className="h-5 bg-slate-200 dark:bg-slate-700 rounded w-24"></div>
            </div>
            {/* Main title lines */}
            <div className="space-y-2">
              <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded w-3/4"></div>
              <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-1/2"></div>
            </div>
            <hr className="border-slate-100 dark:border-slate-700" />
            {/* Rent & details footer */}
            <div className="flex justify-between items-center">
              <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded w-20"></div>
              <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded-full w-24"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (type === 'listing-detail') {
    return (
      <div className="w-full space-y-8 animate-pulse">
        {/* Banner image */}
        <div className="h-96 bg-slate-200 dark:bg-slate-700 rounded-2xl w-full"></div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main content */}
          <div className="lg:col-span-2 space-y-6">
            <div className="space-y-3">
              <div className="h-10 bg-slate-200 dark:bg-slate-700 rounded w-2/3"></div>
              <div className="h-5 bg-slate-200 dark:bg-slate-700 rounded w-1/3"></div>
            </div>
            <div className="h-24 bg-slate-200 dark:bg-slate-700 rounded-xl w-full"></div>
            <div className="space-y-2">
              <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded w-32"></div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                <div className="h-12 bg-slate-200 dark:bg-slate-700 rounded-lg"></div>
                <div className="h-12 bg-slate-200 dark:bg-slate-700 rounded-lg"></div>
                <div className="h-12 bg-slate-200 dark:bg-slate-700 rounded-lg"></div>
              </div>
            </div>
          </div>
          {/* Sidebar */}
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow space-y-4">
              <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded w-1/2"></div>
              <div className="h-12 bg-slate-200 dark:bg-slate-700 rounded-xl w-full"></div>
              <div className="h-12 bg-slate-200 dark:bg-slate-700 rounded-xl w-full"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (type === 'chat') {
    return (
      <div className="flex gap-4 w-full h-[600px] border border-slate-100 dark:border-slate-700 rounded-2xl p-4 animate-pulse">
        {/* Sidebar */}
        <div className="w-80 border-r border-slate-100 dark:border-slate-700 pr-4 space-y-4">
          <div className="h-10 bg-slate-200 dark:bg-slate-700 rounded-lg w-full"></div>
          {Array.from({ length: 5 }).map((_, idx) => (
            <div key={idx} className="flex items-center gap-3">
              <div className="w-12 h-12 bg-slate-200 dark:bg-slate-700 rounded-full"></div>
              <div className="flex-grow space-y-2">
                <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-2/3"></div>
                <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
        {/* Main Conversation */}
        <div className="flex-grow flex flex-col justify-between p-2">
          <div className="flex items-center gap-3 border-b border-slate-100 dark:border-slate-700 pb-3">
            <div className="w-10 h-10 bg-slate-200 dark:bg-slate-700 rounded-full"></div>
            <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-32"></div>
          </div>
          <div className="flex-grow flex flex-col justify-end space-y-4 my-4">
            <div className="h-12 bg-slate-200 dark:bg-slate-700 rounded-xl w-1/3 align-self-start"></div>
            <div className="h-12 bg-slate-200 dark:bg-slate-700 rounded-xl w-1/3 self-end"></div>
            <div className="h-12 bg-slate-200 dark:bg-slate-700 rounded-xl w-1/2 align-self-start"></div>
          </div>
          <div className="h-12 bg-slate-200 dark:bg-slate-700 rounded-xl w-full"></div>
        </div>
      </div>
    );
  }

  if (type === 'profile') {
    return (
      <div className="max-w-2xl w-full bg-white dark:bg-slate-800 p-8 rounded-2xl shadow border border-slate-100 dark:border-slate-700/50 space-y-6 animate-pulse">
        <div className="flex justify-center">
          <div className="w-24 h-24 bg-slate-200 dark:bg-slate-700 rounded-full"></div>
        </div>
        <div className="space-y-4">
          <div className="h-10 bg-slate-200 dark:bg-slate-700 rounded-lg w-full"></div>
          <div className="grid grid-cols-2 gap-4">
            <div className="h-10 bg-slate-200 dark:bg-slate-700 rounded-lg"></div>
            <div className="h-10 bg-slate-200 dark:bg-slate-700 rounded-lg"></div>
          </div>
          <div className="h-24 bg-slate-200 dark:bg-slate-700 rounded-lg w-full"></div>
          <div className="h-12 bg-slate-200 dark:bg-slate-700 rounded-lg w-1/3 mx-auto"></div>
        </div>
      </div>
    );
  }

  return null;
};

export default LoadingSkeleton;
