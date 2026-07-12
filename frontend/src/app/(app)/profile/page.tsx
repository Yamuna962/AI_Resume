'use client';

import { useAuthStore } from '@/stores/auth.store';
import { useEffect, useState } from 'react';
import api from '@/lib/axios';
import { User, Mail, Award, FileText, Calendar } from 'lucide-react';

export default function ProfilePage() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState({ total_analyses: 0, avg_ats_score: 0 });

  useEffect(() => {
    api.get('/profile').then(r => setStats({ total_analyses: r.data.total_analyses || 0, avg_ats_score: r.data.avg_ats_score || 0 })).catch(() => {});
  }, []);

  const initials = user?.full_name?.split(' ').map((n: string) => n[0]).join('').toUpperCase() || 'U';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', color: '#f0f0ff' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '0.375rem' }}>Profile</h1>
        <p style={{ color: '#8888aa', fontSize: '0.95rem' }}>Your account information and statistics.</p>
      </div>

      {/* Profile Card */}
      <div style={{
        background: 'rgba(15,15,26,0.9)', border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: '1.25rem', padding: '2rem',
        display: 'flex', alignItems: 'center', gap: '2rem',
      }}>
        <div style={{
          width: '5rem', height: '5rem', borderRadius: '50%', flexShrink: 0,
          background: 'linear-gradient(135deg, #7c3aed, #06b6d4)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'white', fontWeight: 800, fontSize: '1.5rem',
          boxShadow: '0 8px 30px rgba(124,58,237,0.3)',
        }}>
          {initials}
        </div>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.25rem' }}>{user?.full_name || 'User'}</h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#8888aa', fontSize: '0.875rem' }}>
            <Mail size={14} />
            <span>{user?.email}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#8888aa', fontSize: '0.8rem', marginTop: '0.375rem' }}>
            <Calendar size={14} />
            <span>Member since {user?.created_at ? new Date(user.created_at).toLocaleDateString('en-IN', { month: 'long', year: 'numeric' }) : '—'}</span>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        {[
          { label: 'Total Analyses', value: stats.total_analyses, icon: <FileText size={20} />, color: '#7c3aed' },
          { label: 'Avg ATS Score', value: `${stats.avg_ats_score}%`, icon: <Award size={20} />, color: '#06b6d4' },
          { label: 'Account Status', value: user?.is_active ? 'Active' : 'Inactive', icon: <User size={20} />, color: '#10b981' },
        ].map((s, i) => (
          <div key={i} style={{
            background: 'rgba(15,15,26,0.9)', border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: '1rem', padding: '1.25rem',
            display: 'flex', alignItems: 'center', gap: '1rem',
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
              <div style={{ fontSize: '1.35rem', fontWeight: 800 }}>{s.value}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
