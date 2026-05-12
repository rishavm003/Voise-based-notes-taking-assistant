"use client";

import React, { useState, useRef } from 'react';
import { Play, Pause, Trash2, Link as LinkIcon, Calendar, Clock } from 'lucide-react';

interface NoteCardProps {
  note: any;
  onDelete: (id: string) => void;
  onKeywordClick: (keyword: string) => void;
  onShare: (note: any) => void;
}

export const NoteCard: React.FC<NoteCardProps> = ({ 
  note, 
  onDelete, 
  onKeywordClick,
  onShare 
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const togglePlay = () => {
    if (!note.audio_url) return;

    if (!audioRef.current) {
      audioRef.current = new Audio(note.audio_url);
      audioRef.current.onended = () => setIsPlaying(false);
    }

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const getCategoryColor = (cat: string) => {
    const colors: Record<string, string> = {
      work: 'bg-blue-50 text-blue-600 border-blue-100',
      personal: 'bg-green-50 text-green-600 border-green-100',
      idea: 'bg-purple-50 text-purple-600 border-purple-100',
      reminder: 'bg-amber-50 text-amber-600 border-amber-100'
    };
    return colors[cat.toLowerCase()] || 'bg-slate-50 text-slate-600 border-slate-100';
  };

  const formattedDate = new Date(note.created_at).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  });

  return (
    <div className="group bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300 relative overflow-hidden">
      {/* Decorative top bar */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 to-purple-500 opacity-0 group-hover:opacity-100 transition-opacity" />

      <div className="flex justify-between items-start mb-4">
        <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border ${getCategoryColor(note.category)}`}>
          {note.category}
        </span>
        <div className="flex gap-2">
          <button 
            onClick={() => onShare(note)}
            className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
            title="Share note"
          >
            <LinkIcon size={16} />
          </button>
          <button 
            onClick={() => onDelete(note.id)}
            className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            title="Delete note"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      <h3 className="text-lg font-bold text-slate-900 mb-2 line-clamp-1 pr-4">
        {note.title || "Untitled Note"}
      </h3>
      
      <p className="text-slate-600 text-sm mb-6 line-clamp-3 leading-relaxed">
        {note.content}
      </p>

      {note.keywords && note.keywords.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-6">
          {note.keywords.map((kw: string) => (
            <button
              key={kw}
              onClick={() => onKeywordClick(kw)}
              className="text-[11px] font-semibold text-slate-500 hover:text-indigo-600 bg-slate-100 hover:bg-indigo-50 px-2 py-1 rounded transition-colors"
            >
              #{kw}
            </button>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between pt-4 border-t border-slate-50">
        <div className="flex items-center gap-3 text-slate-400">
          <div className="flex items-center gap-1 text-[11px] font-medium">
            <Calendar size={12} />
            {formattedDate}
          </div>
        </div>

        {note.audio_url && (
          <button 
            onClick={togglePlay}
            className={`flex items-center gap-2 px-4 py-2 rounded-full font-bold text-xs transition-all ${
              isPlaying 
              ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200' 
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {isPlaying ? (
              <><Pause size={14} fill="currentColor" /> Pause</>
            ) : (
              <><Play size={14} fill="currentColor" /> Play</>
            )}
          </button>
        )}
      </div>
    </div>
  );
};
