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

  const firstName = user?.full_name?.split(' ')[0] || 'there';

  const statCards = [
    { label: 'Total Analyses', value: stats.total_analyses, icon: <FileText size={20} />, color: '#7c3aed' },
    { label: 'Avg ATS Score', value: `${stats.avg_ats_score}%`, icon: <Target size={20} />, color: '#06b6d4' },
    { label: 'Highest Score', value: '—', icon: <Award size={20} />, color: '#10b981' },
    { label: 'Last Upload', value: 'Today', icon: <Clock size={20} />, color: '#f59e0b' },
  ];

  return (
    <div className="flex flex-col gap-6 text-foreground animate-fade-in-up">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight mb-1">
          Welcome back, {firstName}! 👋
        </h1>
        <p className="text-sm text-muted-foreground">Here&apos;s an overview of your resume performance.</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {statCards.map((s, i) => (
          <div
            key={i}
            className="bg-card border border-border rounded-xl p-4 flex items-center gap-3 sm:gap-4 hover:border-border/80 hover:shadow-sm transition-all"
          >
            {/* Icon badge — color comes from per-card style, not text-primary */}
            <div
              className="w-10 h-10 sm:w-11 sm:h-11 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ background: `${s.color}18`, border: `1px solid ${s.color}30`, color: s.color }}
            >
              {s.icon}
            </div>
            {/* Text block: min-w-0 prevents overflow pushing the icon out */}
            <div className="min-w-0">
              <div className="text-xs text-muted-foreground mb-0.5 truncate">{s.label}</div>
              <div className="text-xl sm:text-2xl font-extrabold leading-tight">{s.value}</div>
            </div>
          </div>
        ))}
      </div>

      {/* CTA Card */}
      <div className="bg-card border border-primary/20 rounded-2xl p-6 sm:p-8 text-center relative overflow-hidden">
        <div
          className="absolute inset-0 pointer-events-none"
          style={{ background: 'radial-gradient(ellipse at center top, rgba(124,58,237,0.09) 0%, transparent 65%)' }}
        />
        <div className="w-14 h-14 rounded-xl mx-auto mb-4 flex items-center justify-center text-primary bg-primary/10 border border-primary/20">
          <UploadCloud size={28} />
        </div>
        <h2 className="text-xl font-bold mb-2">Ready to land your next job?</h2>
        <p className="text-sm text-muted-foreground mx-auto max-w-lg leading-relaxed mb-6">
          Upload your resume and paste a job description to get an instant ATS score, skill gap analysis, and AI-powered rewrite.
        </p>
        <Link
          href="/upload"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 text-white text-sm font-semibold shadow-md hover:shadow-lg hover:from-violet-500 hover:to-indigo-500 transition-all"
        >
          Start New Analysis
          <ArrowRight size={16} />
        </Link>
      </div>

      {/* Tips Card */}
      <div className="bg-card border border-accent/20 rounded-2xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp size={18} className="text-accent flex-shrink-0" />
          <h3 className="font-bold text-sm">Quick Tips to Boost Your Score</h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {[
            { tip: 'Use exact keywords from the job description', icon: '🎯' },
            { tip: 'Quantify achievements with numbers', icon: '📊' },
            { tip: 'Keep formatting clean and ATS-friendly', icon: '📄' },
            { tip: 'Match your job title to the role applied for', icon: '✅' },
          ].map((t, i) => (
            <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-accent/5 border border-accent/10">
              {/* mt-0.5 aligns emoji cap-height to text's first baseline */}
              <span className="text-base flex-shrink-0 mt-0.5">{t.icon}</span>
              <p className="text-sm text-muted-foreground leading-relaxed">{t.tip}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}