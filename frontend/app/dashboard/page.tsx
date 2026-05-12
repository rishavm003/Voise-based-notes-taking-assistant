"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { NotesGrid } from '@/components/dashboard/notes-grid';
import api from '@/lib/api';
import { exportNotesPDF } from '@/lib/export-pdf';
import { Search, LogOut, FileDown, PlusCircle } from 'lucide-react';

export default function Dashboard() {
  const [notes, setNotes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');
  const [username, setUsername] = useState('');

  const fetchNotes = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await api.get('/notes');
      setNotes(res.data);
    } catch (error) {
      console.error('Failed to fetch notes', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotes();
    const storedUser = localStorage.getItem('username');
    if (storedUser) setUsername(storedUser);
  }, [fetchNotes]);

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this note?')) return;
    try {
      await api.delete(`/notes/${id}`);
      setNotes(notes.filter((n: any) => n.id !== id));
    } catch (error) {
      alert('Failed to delete note');
    }
  };

  const handleKeywordClick = (keyword: string) => {
    setSearchQuery(keyword);
  };

  const handleShare = async (note: any) => {
    try {
      const res = await api.post(`/notes/${note.id}/share`);
      const fullUrl = `${window.location.origin}/share/${res.data.token}`;
      await navigator.clipboard.writeText(fullUrl);
      alert('Share link copied to clipboard!');
    } catch (error) {
      alert('Failed to generate share link');
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = '/login';
  };

  const filteredNotes = notes.filter((note: any) => {
    const matchesSearch = (note.title || '').toLowerCase().includes(searchQuery.toLowerCase()) || 
                          (note.content || '').toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = activeCategory === 'all' || note.category.toLowerCase() === activeCategory.toLowerCase();
    return matchesSearch && matchesCategory;
  });

  const handleExport = () => {
    exportNotesPDF(filteredNotes, username || 'User');
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navbar */}
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white font-black text-xl shadow-lg shadow-indigo-100">V</div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-600">VoiceNotes</h1>
          </div>
          
          <div className="flex-1 max-w-xl mx-8 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input 
              type="text" 
              placeholder="Search your notes, keywords, or categories..."
              className="w-full bg-slate-100 border-none rounded-full py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-indigo-500 transition-all"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="flex items-center gap-4">
            <button 
              onClick={handleExport}
              className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-slate-600 hover:bg-slate-50 rounded-lg transition-colors"
            >
              <FileDown size={18} /> Export PDF
            </button>
            <div className="h-6 w-px bg-slate-200" />
            <button onClick={handleLogout} className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
              <LogOut size={20} />
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Categories Bar */}
        <div className="flex items-center gap-2 mb-8 overflow-x-auto pb-2 scrollbar-hide">
          {['all', 'work', 'personal', 'idea', 'reminder'].map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-6 py-2 rounded-full text-sm font-bold capitalize transition-all whitespace-nowrap ${
                activeCategory === cat 
                ? 'bg-slate-900 text-white shadow-lg' 
                : 'bg-white text-slate-500 border border-slate-200 hover:border-slate-300'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Stats Summary (Mini) */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-10">
            <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
                <p className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-1">Total Notes</p>
                <p className="text-3xl font-black text-slate-900">{notes.length}</p>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
                <p className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-1">Filtered</p>
                <p className="text-3xl font-black text-indigo-600">{filteredNotes.length}</p>
            </div>
        </div>

        {/* Notes Grid */}
        <NotesGrid 
          notes={filteredNotes} 
          isLoading={isLoading} 
          searchQuery={searchQuery}
          onDelete={handleDelete}
          onKeywordClick={handleKeywordClick}
          onShare={handleShare}
          onClearFilters={() => { setSearchQuery(''); setActiveCategory('all'); }}
          onStartRecording={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        />
      </main>

      {/* Floating Action Button for Recorder (Placeholder) */}
      <button 
        className="fixed bottom-8 right-8 w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center text-white shadow-2xl shadow-indigo-200 hover:scale-110 active:scale-95 transition-all z-20 group"
      >
        <PlusCircle size={32} />
        <span className="absolute right-full mr-4 bg-slate-900 text-white text-xs font-bold py-2 px-4 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
            New Voice Note
        </span>
      </button>
    </div>
  );
}
