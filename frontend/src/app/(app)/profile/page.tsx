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
    <div className="flex flex-col gap-8 text-foreground">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold mb-1">Profile</h1>
        <p className="text-sm text-muted-foreground">Your account information and statistics.</p>
      </div>

      {/* Profile Card */}
      <div className="bg-card border border-border rounded-2xl p-6 flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-6">
        <div className="w-20 h-20 rounded-full flex items-center justify-center text-white font-extrabold text-xl bg-gradient-to-br from-indigo-600 to-cyan-400 shadow-lg">
          {initials}
        </div>
        <div>
          <h2 className="text-lg font-bold mb-1">{user?.full_name || 'User'}</h2>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Mail size={14} />
            <span>{user?.email}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground mt-2">
            <Calendar size={14} />
            <span>Member since {user?.created_at ? new Date(user.created_at).toLocaleDateString('en-IN', { month: 'long', year: 'numeric' }) : '—'}</span>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { label: 'Total Analyses', value: stats.total_analyses, icon: <FileText size={20} />, color: '#7c3aed' },
          { label: 'Avg ATS Score', value: `${stats.avg_ats_score}%`, icon: <Award size={20} />, color: '#06b6d4' },
          { label: 'Account Status', value: user?.is_active ? 'Active' : 'Inactive', icon: <User size={20} />, color: '#10b981' },
        ].map((s, i) => (
          <div key={i} className="bg-card border border-border rounded-lg p-4 flex items-center gap-4">
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
    </div>
  );
}
