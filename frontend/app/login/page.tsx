"use client";

import React, { useState } from 'react';
import api from '@/lib/api';
import Link from 'next/link';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const res = await api.post('/auth/login', { email, password });
      localStorage.setItem('access_token', res.data.access_token);
      localStorage.setItem('username', res.data.username);
      localStorage.setItem('user_id', res.data.user_id);
      window.location.href = '/dashboard';
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-3xl shadow-xl shadow-slate-200/50 p-10 border border-slate-100">
        <div className="text-center mb-10">
          <div className="inline-flex w-16 h-16 bg-indigo-600 rounded-2xl items-center justify-center text-white text-3xl font-black mb-4 shadow-lg shadow-indigo-100">V</div>
          <h1 className="text-3xl font-black text-slate-900 mb-2">Welcome Back</h1>
          <p className="text-slate-400 font-medium">Log in to access your intelligent notes</p>
        </div>

        {error && (
          <div className="bg-red-50 text-red-500 text-sm font-bold p-4 rounded-xl mb-6 border border-red-100">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
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
            className="w-full bg-indigo-600 text-white font-black py-4 rounded-2xl shadow-lg shadow-indigo-200 hover:bg-indigo-700 hover:shadow-indigo-300 active:scale-95 transition-all disabled:opacity-50 disabled:active:scale-100"
          >
            {isLoading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        <p className="mt-8 text-center text-slate-500 font-medium">
          Don't have an account? {' '}
          <Link href="/register" className="text-indigo-600 font-bold hover:underline">Create one</Link>
        </p>
      </div>
    </div>
  );
}
