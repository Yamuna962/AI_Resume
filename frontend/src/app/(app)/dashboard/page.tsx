'use client';

import { useAuthStore } from '@/stores/auth.store';
import Link from 'next/link';
import { UploadCloud, FileText, Target, Award, Clock, ArrowRight, TrendingUp } from 'lucide-react';
import api from '@/lib/axios';
import { useEffect, useState } from 'react';

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState({ total_analyses: 0, avg_ats_score: 0 });

  useEffect(() => {
    api.get('/profile').then(res => setStats({
      total_analyses: res.data.total_analyses || 0,
      avg_ats_score: res.data.avg_ats_score || 0,
    })).catch(() => {});
  }, []);

  const firstName = user?.full_name?.split(' ')[0] || 'User';

  const statCards = [
    { label: 'Total Analyses', value: stats.total_analyses, icon: <FileText size={20} />, color: '#7c3aed' },
    { label: 'Avg ATS Score', value: `${stats.avg_ats_score}%`, icon: <Target size={20} />, color: '#06b6d4' },
    { label: 'Highest Score', value: '—', icon: <Award size={20} />, color: '#10b981' },
    { label: 'Last Upload', value: 'Today', icon: <Clock size={20} />, color: '#f59e0b' },
  ];

  return (
    <div className="flex flex-col gap-8 text-foreground">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold mb-1">Welcome back, {firstName}! 👋</h1>
        <p className="text-sm text-muted-foreground">Here&apos;s an overview of your resume performance.</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((s, i) => (
          <div key={i} className="bg-card border border-border rounded-lg p-4 flex items-center gap-4 transition-colors">
            <div style={{ background: `${s.color}18`, border: `1px solid ${s.color}30` }} className="w-11 h-11 rounded-lg flex items-center justify-center text-lg text-primary flex-shrink-0">
              {s.icon}
            </div>
            <div>
              <div className="text-xs text-muted-foreground mb-1">{s.label}</div>
              <div className="text-2xl font-extrabold">{s.value}</div>
            </div>
          </div>
        ))}
      </div>

      {/* CTA Card */}
      <div className="bg-card border border-primary/20 rounded-2xl p-6 text-center relative overflow-hidden">
        <div className="absolute inset-0" style={{ background: 'radial-gradient(ellipse at center top, rgba(124,58,237,0.08) 0%, transparent 60%)', pointerEvents: 'none' }} />
        <div className="w-16 h-16 rounded-lg mx-auto mb-4 flex items-center justify-center text-primary bg-primary/10 border border-primary/20">
          <UploadCloud size={28} />
        </div>
        <h2 className="text-xl font-bold mb-2">Ready to land your next job?</h2>
        <p className="text-sm text-muted-foreground mx-auto max-w-lg leading-relaxed mb-6">Upload your resume and paste a job description to get an instant ATS score, skill gap analysis, and AI-powered rewrite.</p>
        <Link href="/upload" className="inline-flex items-center gap-2 px-5 py-3 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold shadow-lg">
          Start New Analysis
          <ArrowRight size={16} />
        </Link>
      </div>

      {/* Tips Card */}
      <div className="bg-card border border-accent/20 rounded-2xl p-4">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp size={18} color="#22d3ee" />
          <h3 className="font-bold text-base">Quick Tips to Boost Your Score</h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {[
            { tip: 'Use exact keywords from the job description', icon: '🎯' },
            { tip: 'Quantify achievements with numbers', icon: '📊' },
            { tip: 'Keep formatting clean and ATS-friendly', icon: '📄' },
            { tip: 'Match your title to the role applied for', icon: '✅' },
          ].map((t, i) => (
            <div key={i} className="flex items-start gap-3 p-3 rounded-md bg-accent/5 border border-accent/10">
              <span className="text-lg flex-shrink-0">{t.icon}</span>
              <p className="text-sm text-muted-foreground leading-relaxed">{t.tip}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
