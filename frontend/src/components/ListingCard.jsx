import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { MapPin, DollarSign, Calendar, Sparkles } from 'lucide-react';

const ListingCard = ({ listing, filterQuery }) => {
  const { id, title, rent, location, room_type, furnishing_status, available_from, images, compatibility, is_filled } = listing;

  const [showReason, setShowReason] = useState(false);

  const score = listing.compatibility_score !== undefined && listing.compatibility_score !== null 
    ? listing.compatibility_score 
    : (compatibility?.compatibility_score !== undefined ? compatibility.compatibility_score : compatibility?.score);

  // Determine styling based on match score
  let scoreColorClass = 'bg-slate-100 dark:bg-slate-800 text-slate-500';
  let scoreBorderClass = 'border-slate-200 dark:border-slate-700';
  
  if (score !== undefined && score !== null) {
    if (score >= 80) {
      scoreColorClass = 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400';
      scoreBorderClass = 'border-emerald-500/30';
    } else if (score >= 50) {
      scoreColorClass = 'bg-amber-500/10 border-amber-500/20 text-amber-600 dark:text-amber-400';
      scoreBorderClass = 'border-amber-500/30';
    } else {
      scoreColorClass = 'bg-rose-500/10 border-rose-500/20 text-rose-600 dark:text-rose-400';
      scoreBorderClass = 'border-rose-500/30';
    }
  }

  // Fallback image if none uploaded
  const mainImage = images && images.length > 0 
    ? `http://localhost:5050${images[0].image_url}` 
    : 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=600&q=80';

  return (
    <div className="group bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden flex flex-col justify-between transform hover:-translate-y-1">
      
      {/* Top Image Section */}
      <div className="relative h-48 overflow-hidden bg-slate-100 dark:bg-slate-900">
        <img 
          src={mainImage} 
          alt={title} 
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-900/50 via-transparent to-transparent"></div>
        
        {/* Room type & Furnishing Badges */}
        <div className="absolute top-3 left-3 flex flex-wrap gap-1.5">
          <span className="px-2.5 py-1 rounded-lg bg-white/90 dark:bg-slate-900/90 text-[10px] font-extrabold uppercase tracking-wider text-slate-800 dark:text-slate-200 backdrop-blur-sm border border-white/20">
            {room_type.replace('_', ' ')}
          </span>
          <span className="px-2.5 py-1 rounded-lg bg-white/90 dark:bg-slate-900/90 text-[10px] font-extrabold uppercase tracking-wider text-slate-800 dark:text-slate-200 backdrop-blur-sm border border-white/20">
            {furnishing_status}
          </span>
        </div>

        {/* Booked Badge */}
        {is_filled && (
          <div className="absolute top-3 right-3 bg-rose-600 text-white px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-wider shadow-md z-10">
            Booked
          </div>
        )}

        {/* Compatibility badge */}
        {compatibility !== undefined && compatibility !== null && (
          <div className={`absolute bottom-3 right-3 flex items-center gap-1.5 px-3 py-1.5 rounded-xl border backdrop-blur-md font-bold text-xs shadow-lg
            ${(score === 0 || compatibility.status === 'No preferences selected')
              ? 'bg-slate-100 dark:bg-slate-800 text-slate-500 border-slate-200 dark:border-slate-700' 
              : scoreColorClass}
            ${(score === 0 || compatibility.status === 'No preferences selected')
              ? 'border-slate-200 dark:border-slate-700' 
              : scoreBorderClass}`}
          >
            <Sparkles size={12} className={(score === 0 || compatibility.status === 'No preferences selected') ? 'text-slate-400' : 'animate-pulse'} />
            <span>
              {(score === 0 || compatibility.status === 'No preferences selected')
                ? 'No Preferences Selected'
                : `${score}% Match`}
            </span>
          </div>
        )}
      </div>

      {/* Details Container */}
      <div className="p-5 flex-grow flex flex-col justify-between gap-4">
        
        <div className="space-y-2">
          {/* Rent & Title */}
          <div className="flex justify-between items-start gap-2">
            <h3 className="font-extrabold text-base leading-snug text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors line-clamp-1">
              {title}
            </h3>
          </div>

          {/* Location info */}
          <div className="flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">
            <MapPin size={14} className="text-slate-400" />
            <span>{location}</span>
          </div>

          {/* AI Match Explanation Accordion */}
          {compatibility && score > 0 && compatibility.reason && (
            <div className="text-xs pt-1">
              <button 
                onClick={(e) => {
                  e.preventDefault();
                  setShowReason(!showReason);
                }}
                className="text-[10px] font-extrabold text-blue-600 dark:text-blue-400 flex items-center gap-1 hover:underline"
              >
                <span>{showReason ? 'Hide Analysis' : 'Why this Match?'}</span>
              </button>
              {showReason && (
                <ul className="mt-2 space-y-1 bg-slate-50 dark:bg-slate-900/50 p-2.5 rounded-xl border border-slate-100 dark:border-slate-700/50 text-[10px] text-slate-600 dark:text-slate-400 font-semibold animate-fade-in list-none">
                  {compatibility.reason.map((r, idx) => {
                    const isPass = r.startsWith('✓');
                    return (
                      <li key={idx} className="flex items-start gap-1">
                        <span className={isPass ? 'text-emerald-500 font-bold' : 'text-rose-500 font-bold'}>
                          {isPass ? '✓' : '✗'}
                        </span>
                        <span>{r.replace(/^[✓✗]/, '').trim()}</span>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          )}
        </div>

        <hr className="border-slate-100 dark:border-slate-700/50" />

        {/* Footer */}
        <div className="flex justify-between items-center mt-auto">
          <div className="flex items-baseline">
            <span className="text-xl font-black text-slate-950 dark:text-white">${rent}</span>
            <span className="text-xs font-semibold text-slate-400 ml-1">/mo</span>
          </div>
          <Link
            to={`/listings/${id}${filterQuery ? '?' + filterQuery : ''}`}
            className="px-4 py-2 text-xs font-extrabold text-white bg-gradient-to-r from-blue-600 to-pink-500 hover:from-blue-500 hover:to-pink-400 rounded-xl transition-all"
          >
            View Room
          </Link>
        </div>

      </div>

    </div>
  );
};

export default ListingCard;
