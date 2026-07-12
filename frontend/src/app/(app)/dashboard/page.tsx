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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', color: '#f0f0ff' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '0.375rem' }}>
          Welcome back, {firstName}! 👋
        </h1>
        <p style={{ color: '#8888aa', fontSize: '0.95rem' }}>
          Here&apos;s an overview of your resume performance.
        </p>
      </div>

      {/* Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        {statCards.map((s, i) => (
          <div key={i} style={{
            background: 'rgba(15,15,26,0.9)',
            border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: '1rem',
            padding: '1.25rem',
            display: 'flex', alignItems: 'center', gap: '1rem',
            transition: 'border-color 0.2s',
          }}>
            <div style={{
              width: '2.75rem', height: '2.75rem', borderRadius: '0.75rem', flexShrink: 0,
              background: `${s.color}18`, border: `1px solid ${s.color}30`,
              display: 'flex', alignItems: 'center', justifyContent: 'center', color: s.color,
            }}>
              {s.icon}
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: '#8888aa', marginBottom: '0.25rem' }}>{s.label}</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f0f0ff', lineHeight: 1 }}>{s.value}</div>
            </div>
          </div>
        ))}
      </div>

      {/* CTA Card */}
      <div style={{
        background: 'rgba(15,15,26,0.9)',
        border: '1px solid rgba(124,58,237,0.15)',
        borderRadius: '1.25rem',
        padding: '2.5rem',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute', inset: 0,
          background: 'radial-gradient(ellipse at center top, rgba(124,58,237,0.08) 0%, transparent 60%)',
          pointerEvents: 'none',
        }} />
        <div style={{
          width: '4rem', height: '4rem', borderRadius: '1rem',
          background: 'rgba(124,58,237,0.12)', border: '1px solid rgba(124,58,237,0.25)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          margin: '0 auto 1.5rem', color: '#a78bfa',
        }}>
          <UploadCloud size={28} />
        </div>
        <h2 style={{ fontSize: '1.35rem', fontWeight: 700, marginBottom: '0.75rem', position: 'relative' }}>
          Ready to land your next job?
        </h2>
        <p style={{ color: '#8888aa', maxWidth: '420px', margin: '0 auto 2rem', lineHeight: 1.7, fontSize: '0.9rem', position: 'relative' }}>
          Upload your resume and paste a job description to get an instant ATS score, skill gap analysis, and AI-powered rewrite.
        </p>
        <Link href="/upload" style={{
          display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
          padding: '0.75rem 1.75rem', borderRadius: '0.75rem',
          background: 'linear-gradient(135deg, #7c3aed, #4f46e5)',
          color: 'white', textDecoration: 'none', fontWeight: 600, fontSize: '0.9rem',
          boxShadow: '0 4px 20px rgba(124,58,237,0.3)', position: 'relative',
          transition: 'all 0.2s',
        }}>
          Start New Analysis
          <ArrowRight size={16} />
        </Link>
      </div>

      {/* Tips Card */}
      <div style={{
        background: 'rgba(15,15,26,0.9)',
        border: '1px solid rgba(6,182,212,0.12)',
        borderRadius: '1.25rem',
        padding: '1.5rem 2rem',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', marginBottom: '1.25rem' }}>
          <TrendingUp size={18} color="#22d3ee" />
          <h3 style={{ fontWeight: 700, fontSize: '1rem', color: '#f0f0ff' }}>Quick Tips to Boost Your Score</h3>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
          {[
            { tip: 'Use exact keywords from the job description', icon: '🎯' },
            { tip: 'Quantify achievements with numbers', icon: '📊' },
            { tip: 'Keep formatting clean and ATS-friendly', icon: '📄' },
            { tip: 'Match your title to the role applied for', icon: '✅' },
          ].map((t, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'flex-start', gap: '0.75rem',
              padding: '0.875rem', borderRadius: '0.75rem',
              background: 'rgba(6,182,212,0.05)', border: '1px solid rgba(6,182,212,0.1)',
            }}>
              <span style={{ fontSize: '1.25rem', flexShrink: 0 }}>{t.icon}</span>
              <p style={{ fontSize: '0.8rem', color: '#a0a0c0', lineHeight: 1.5 }}>{t.tip}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
