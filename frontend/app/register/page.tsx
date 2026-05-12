"use client";

import React, { useState } from 'react';
import api from '@/lib/api';
import Link from 'next/link';

export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await api.post('/auth/register', { username, email, password });
      window.location.href = '/login?registered=true';
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Try a different email.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-3xl shadow-xl shadow-slate-200/50 p-10 border border-slate-100">
        <div className="text-center mb-10">
          <div className="inline-flex w-16 h-16 bg-indigo-600 rounded-2xl items-center justify-center text-white text-3xl font-black mb-4 shadow-lg shadow-indigo-100">V</div>
          <h1 className="text-3xl font-black text-slate-900 mb-2">Create Account</h1>
          <p className="text-slate-400 font-medium">Join VoiceNotes and start capturing ideas</p>
        </div>

        {error && (
          <div className="bg-red-50 text-red-500 text-sm font-bold p-4 rounded-xl mb-6 border border-red-100">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-slate-700 text-sm font-bold mb-2 ml-1">Username</label>
            <input 
              type="text" 
              required
              className="w-full bg-slate-50 border border-slate-100 rounded-2xl py-3 px-4 text-slate-900 focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              placeholder="johndoe"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-slate-700 text-sm font-bold mb-2 ml-1">Email Address</label>
            <input 
              type="email" 
              required
              className="w-full bg-slate-50 border border-slate-100 rounded-2xl py-3 px-4 text-slate-900 focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-slate-700 text-sm font-bold mb-2 ml-1">Password</label>
            <input 
              type="password" 
              required
              className="w-full bg-slate-50 border border-slate-100 rounded-2xl py-3 px-4 text-slate-900 focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button 
            type="submit" 
            disabled={isLoading}
            className="w-full bg-slate-900 text-white font-black py-4 rounded-2xl shadow-lg shadow-slate-200 hover:bg-black active:scale-95 transition-all disabled:opacity-50 disabled:active:scale-100 mt-4"
          >
            {isLoading ? 'Creating Account...' : 'Get Started'}
          </button>
        </form>

        <p className="mt-8 text-center text-slate-500 font-medium">
          Already have an account? {' '}
          <Link href="/login" className="text-indigo-600 font-bold hover:underline">Log in</Link>
        </p>
      </div>
    </div>
  );
}
