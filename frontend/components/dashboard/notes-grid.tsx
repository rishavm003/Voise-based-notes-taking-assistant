"use client";

import React from 'react';
import { NoteCard } from './note-card';
import { Mic, SearchX, Plus } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

interface NotesGridProps {
  notes: any[];
  isLoading: boolean;
  searchQuery: string;
  onDelete: (id: string) => void;
  onKeywordClick: (keyword: string) => void;
  onShare: (note: any) => void;
  onClearFilters: () => void;
  onStartRecording: () => void;
}

export const NotesGrid: React.FC<NotesGridProps> = ({
  notes,
  isLoading,
  searchQuery,
  onDelete,
  onKeywordClick,
  onShare,
  onClearFilters,
  onStartRecording
}) => {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-white rounded-2xl p-6 border border-slate-200 h-64 flex flex-col gap-4">
             <Skeleton className="h-6 w-24 rounded-full" />
             <Skeleton className="h-8 w-3/4 rounded-md" />
             <Skeleton className="h-20 w-full rounded-md" />
             <div className="mt-auto flex justify-between">
                <Skeleton className="h-4 w-20 rounded-md" />
                <Skeleton className="h-8 w-24 rounded-full" />
             </div>
          </div>
        ))}
      </div>
    );
  }

  if (notes.length === 0) {
    if (searchQuery) {
      return (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <div className="bg-slate-100 p-6 rounded-full mb-6">
            <SearchX size={48} className="text-slate-400" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-2">No notes found</h3>
          <p className="text-slate-500 mb-8 max-w-xs">
            Try a different search term or category to find what you're looking for.
          </p>
          <button
            onClick={onClearFilters}
            className="px-6 py-2 bg-white border border-slate-200 text-slate-600 font-bold rounded-full hover:bg-slate-50 transition-colors"
          >
            Clear all filters
          </button>
        </div>
      );
    }

    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <div className="bg-indigo-50 p-6 rounded-full mb-6 animate-bounce">
          <Mic size={48} className="text-indigo-500" />
        </div>
        <h3 className="text-2xl font-bold text-slate-900 mb-2">No notes yet</h3>
        <p className="text-slate-500 mb-8 max-w-sm">
          Your thoughts deserve to be captured. Tap the record button above to create your first intelligent voice note.
        </p>
        <button
          onClick={onStartRecording}
          className="flex items-center gap-2 px-8 py-3 bg-indigo-600 text-white font-bold rounded-full hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-200 active:scale-95"
        >
          <Plus size={20} /> Start Recording
        </button>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {notes.map(note => (
        <NoteCard
          key={note.id}
          note={note}
          onDelete={onDelete}
          onKeywordClick={onKeywordClick}
          onShare={onShare}
        />
      ))}
    </div>
  );
};
