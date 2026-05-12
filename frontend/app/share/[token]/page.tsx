import React from 'react';
import { notFound } from 'next/navigation';

interface SharePageProps {
  params: { token: string };
}

async function getNote(token: string) {
  // Use absolute URL for server-side fetch if needed, 
  // but assuming relative works with proxy or internal DNS
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/share/${token}`, {
    cache: 'no-store'
  });
  
  if (!res.ok) return null;
  return res.json();
}

export default async function SharePage({ params }: SharePageProps) {
  const note = await getNote(params.token);

  if (!note) {
    notFound();
  }

  const formattedDate = new Date(note.created_at).toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  });

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center py-20 px-4">
      <div className="max-w-2xl w-full bg-white rounded-3xl shadow-xl p-10 border border-slate-100">
        <div className="flex justify-between items-start mb-8">
          <span className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider bg-indigo-50 text-indigo-600 border border-indigo-100`}>
            {note.category}
          </span>
          <span className="text-slate-400 text-sm font-medium">{formattedDate}</span>
        </div>

        <h1 className="text-4xl font-extrabold text-slate-900 mb-6 leading-tight">
          {note.title || "Shared Voice Note"}
        </h1>

        <div className="prose prose-slate max-w-none mb-10">
          <p className="text-slate-700 text-lg leading-relaxed whitespace-pre-wrap">
            {note.content}
          </p>
        </div>

        {note.keywords && note.keywords.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-12">
            {note.keywords.map((kw: string) => (
              <span key={kw} className="px-3 py-1 bg-slate-100 text-slate-600 rounded-md text-sm font-semibold">
                #{kw}
              </span>
            ))}
          </div>
        )}

        {note.audio_url && (
          <div className="bg-indigo-50 rounded-2xl p-6 mb-10">
            <p className="text-indigo-900 font-semibold mb-4 flex items-center gap-2">
               Play Audio Recording
            </p>
            <audio controls className="w-full">
              <source src={note.audio_url} type="audio/mpeg" />
              Your browser does not support the audio element.
            </audio>
          </div>
        )}

        <footer className="mt-12 pt-8 border-t border-slate-100 text-center">
          <p className="text-slate-400 text-sm mb-4">
            Made with <span className="text-indigo-500 font-bold">VoiceNotes</span>
          </p>
          <a 
            href="/register" 
            className="inline-block px-8 py-3 bg-indigo-600 text-white rounded-full font-bold hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-200"
          >
            Create Your Own Voice Notes
          </a>
        </footer>
      </div>
    </div>
  );
}
