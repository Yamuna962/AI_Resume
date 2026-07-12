'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ChevronRight, Clock, FileText } from 'lucide-react';
import api from '@/lib/axios';
import type { HistoryItem } from '@/types';

interface HistoryResponse {
  items: HistoryItem[];
  total: number;
  page: number;
  limit: number;
}

export default function HistoryPage() {
  const [analyses, setAnalyses] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<HistoryResponse>('/history')
      .then((response) => setAnalyses(response.data.items || []))
      .catch(() => {
        setAnalyses([]);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', color: '#f0f0ff' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '0.375rem' }}>
          Analysis History
        </h1>
        <p style={{ color: '#8888aa', fontSize: '0.95rem' }}>All your past resume analyses and scores.</p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem', color: '#8888aa' }}>Loading...</div>
      ) : analyses.length === 0 ? (
        <div
          style={{
            background: 'rgba(15,15,26,0.9)',
            border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: '1.25rem',
            padding: '4rem',
            textAlign: 'center',
          }}
        >
          <Clock size={48} color="#5a5a7a" style={{ margin: '0 auto 1rem' }} />
          <h3 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>No analyses yet</h3>
          <p style={{ color: '#8888aa', marginBottom: '1.5rem' }}>Upload your first resume to see results here.</p>
          <Link
            href="/upload"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.625rem 1.25rem',
              borderRadius: '0.625rem',
              background: 'linear-gradient(135deg, #7c3aed, #4f46e5)',
              color: 'white',
              textDecoration: 'none',
              fontWeight: 600,
              fontSize: '0.875rem',
            }}
          >
            Start New Analysis
          </Link>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {analyses.map((analysis) => {
            const matchScore = analysis.skill_match_percentage || 0;
            const atsScore = analysis.ats_score || 0;
            const scoreColor = (score: number) =>
              score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444';

            return (
              <Link key={analysis.id} href={`/history/${analysis.id}`} style={{ textDecoration: 'none' }}>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    padding: '1.25rem 1.5rem',
                    background: 'rgba(15,15,26,0.9)',
                    border: '1px solid rgba(255,255,255,0.06)',
                    borderRadius: '1rem',
                    transition: 'border-color 0.2s',
                    cursor: 'pointer',
                  }}
                >
                  <div
                    style={{
                      width: '2.5rem',
                      height: '2.5rem',
                      borderRadius: '0.625rem',
                      flexShrink: 0,
                      background: 'rgba(124,58,237,0.12)',
                      border: '1px solid rgba(124,58,237,0.2)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#a78bfa',
                    }}
                  >
                    <FileText size={18} />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div
                      style={{
                        fontWeight: 600,
                        marginBottom: '0.25rem',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}
                    >
                      {analysis.resume_filename || 'Resume Analysis'}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#8888aa' }}>
                      {new Date(analysis.created_at).toLocaleDateString('en-IN', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric',
                      })}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '0.7rem', color: '#8888aa', marginBottom: '0.2rem' }}>Match</div>
                      <div style={{ fontWeight: 700, color: scoreColor(matchScore) }}>{matchScore}%</div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '0.7rem', color: '#8888aa', marginBottom: '0.2rem' }}>ATS</div>
                      <div style={{ fontWeight: 700, color: scoreColor(atsScore) }}>{atsScore}</div>
                    </div>
                    <ChevronRight size={18} color="#5a5a7a" />
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
