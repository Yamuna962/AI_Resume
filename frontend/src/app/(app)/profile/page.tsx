'use client';

import { useAuthStore } from '@/stores/auth.store';
import { useEffect, useState } from 'react';
import api from '@/lib/axios';
import { CheckCircle, Mail, Award, FileText, Calendar } from 'lucide-react';

export default function ProfilePage() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState({ total_analyses: 0, avg_ats_score: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get('/profile')
      .then((r) =>
        setStats({
          total_analyses: r.data.total_analyses || 0,
          avg_ats_score: r.data.avg_ats_score || 0,
        })
      )
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const initials = user?.full_name
    ? user.full_name
        .split(' ')
        .map((n: string) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : 'U';

  const statItems = [
    {
      label: 'Total Analyses',
      value: loading ? '—' : stats.total_analyses,
      icon: <FileText size={20} />,
      color: '#7c3aed',
    },
    {
      label: 'Avg ATS Score',
      value: loading ? '—' : `${stats.avg_ats_score}%`,
      icon: <Award size={20} />,
      color: '#06b6d4',
    },
    {
      label: 'Account Status',
      value: user?.is_active ? 'Active' : 'Inactive',
      icon: <CheckCircle size={20} />,
      color: '#10b981',
    },
  ];

  return (
    <div className="flex flex-col gap-6 text-foreground max-w-3xl mx-auto">
      {/* Page header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight mb-1">Profile</h1>
        <p className="text-sm text-muted-foreground">Your account information and statistics.</p>
      </div>

      {/* Profile card */}
      <div className="bg-card border border-border rounded-2xl p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-5">
          {/* Avatar */}
          <div className="relative flex-shrink-0">
            <div className="w-20 h-20 rounded-2xl flex items-center justify-center text-white font-extrabold text-2xl bg-gradient-to-br from-violet-600 to-cyan-500 shadow-lg select-none">
              {initials}
            </div>
            {user?.is_active && (
              <span
                className="absolute -bottom-1 -right-1 w-5 h-5 bg-emerald-500 border-2 border-card rounded-full"
                title="Active"
              />
            )}
          </div>

          {/* Info — min-w-0 prevents long emails overflowing the flex row */}
          <div className="flex flex-col gap-2 min-w-0">
            <h2 className="text-xl font-extrabold tracking-tight truncate">
              {user?.full_name || 'User'}
            </h2>
            <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
              <Mail size={14} className="flex-shrink-0" />
              <span className="truncate">{user?.email}</span>
            </div>
            {user?.created_at && (
              <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                <Calendar size={14} className="flex-shrink-0" />
                <span>
                  Member since{' '}
                  {new Date(user.created_at).toLocaleDateString('en-IN', {
                    month: 'long',
                    year: 'numeric',
                  })}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {statItems.map((s, i) => (
          <div
            key={i}
            className="bg-card border border-border rounded-xl p-4 flex items-center gap-3"
          >
            {/* Icon: color from per-card style, not text-primary */}
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{
                background: `${s.color}18`,
                border: `1px solid ${s.color}30`,
                color: s.color,
              }}
            >
              {s.icon}
            </div>
            {/* min-w-0 lets truncate work inside a flex child */}
            <div className="min-w-0">
              <div className="text-xs text-muted-foreground mb-0.5 truncate">{s.label}</div>
              <div className="text-xl font-extrabold leading-tight truncate">{s.value}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Account details table */}
      <div className="bg-card border border-border rounded-2xl p-5">
        <h3 className="font-bold text-sm mb-4">Account Details</h3>
        <div className="divide-y divide-border">
          {[
            { label: 'Full Name', value: user?.full_name || '—' },
            { label: 'Email Address', value: user?.email || '—' },
            { label: 'Account Status', value: user?.is_active ? 'Active' : 'Inactive' },
          ].map((row) => (
            <div
              key={row.label}
              className="flex justify-between items-center py-3 first:pt-0 last:pb-0 gap-4"
            >
              <span className="text-sm text-muted-foreground flex-shrink-0">{row.label}</span>
              <span className="text-sm font-medium text-right truncate">{row.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}