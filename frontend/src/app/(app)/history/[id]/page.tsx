'use client';

import { use, useEffect, useState } from 'react';
import Link from 'next/link';
import { AlertCircle, ChevronDown, ChevronLeft, ChevronUp } from 'lucide-react';
import api from '@/lib/axios';
import type { AnalysisSuggestion, AtsAnalysisResult } from '@/types/analysis';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function HistoryDetailPage({ params }: PageProps) {
  const resolvedParams = use(params);
  const id = resolvedParams.id;
  const [result, setResult] = useState<AtsAnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [showRewrite, setShowRewrite] = useState(false);

  useEffect(() => {
    api
      .get<AtsAnalysisResult>(`/analysis/${id}`)
      .then((response) => setResult(response.data))
      .catch(() => {
        setResult(null);
      })
      .finally(() => setLoading(false));
  }, [id]);

  const scoreColor = (score: number) =>
    score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444';

  if (loading) {
    return <div style={{ color: '#8888aa', textAlign: 'center', padding: '4rem' }}>Loading analysis details...</div>;
  }

  if (!result) {
    return (
      <div style={{ color: '#f0f0ff', textAlign: 'center', padding: '4rem' }}>
        <AlertCircle size={48} color="#ef4444" style={{ margin: '0 auto 1rem' }} />
        <h2 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>Analysis Not Found</h2>
        <p style={{ color: '#8888aa', marginBottom: '1.5rem' }}>
          This analysis record does not exist or you do not have permission to view it.
        </p>
        <Link
          href="/history"
          style={{
            padding: '0.625rem 1.25rem',
            borderRadius: '0.625rem',
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.1)',
            color: '#c4c4e0',
            textDecoration: 'none',
            fontWeight: 600,
            fontSize: '0.875rem',
          }}
        >
          ← Back to History
        </Link>
      </div>
    );
  }

  const matchScore = result.match_score ?? result.skill_match_percentage ?? 0;
  const atsScore = result.ats_score ?? 0;
  const missingSkills = result.missing_skills ?? [];
  const suggestions = result.suggestions ?? [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', color: '#f0f0ff', maxWidth: '800px' }}>
      <div>
        <Link
          href="/history"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.375rem',
            color: '#a78bfa',
            textDecoration: 'none',
            fontSize: '0.875rem',
            fontWeight: 500,
            marginBottom: '1rem',
          }}
        >
          <ChevronLeft size={16} /> Back to History
        </Link>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '0.375rem' }}>
          Analysis Results
        </h1>
        <p style={{ color: '#8888aa', fontSize: '0.95rem' }}>Detailed breakdown of your resume match.</p>
      </div>

      <div
        style={{
          background: 'rgba(15,15,26,0.9)',
          border: '1px solid rgba(255,255,255,0.06)',
          borderRadius: '1.25rem',
          padding: '2rem',
        }}
      >
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          {[
            { label: 'Match Score', value: `${matchScore}%`, score: matchScore },
            { label: 'ATS Score', value: atsScore, score: atsScore },
          ].map((scoreCard) => (
            <div
              key={scoreCard.label}
              style={{
                padding: '1.5rem',
                borderRadius: '1rem',
                textAlign: 'center',
                background: `${scoreColor(scoreCard.score)}12`,
                border: `1px solid ${scoreColor(scoreCard.score)}25`,
              }}
            >
              <div
                style={{
                  fontSize: '2.5rem',
                  fontWeight: 900,
                  color: scoreColor(scoreCard.score),
                  lineHeight: 1,
                }}
              >
                {scoreCard.value}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#8888aa', marginTop: '0.375rem' }}>{scoreCard.label}</div>
            </div>
          ))}
        </div>
      </div>

      {result.reasoning && (
        <div
          style={{
            background: 'rgba(15,15,26,0.9)',
            border: '1px solid rgba(124,58,237,0.15)',
            borderRadius: '1.25rem',
            padding: '1.5rem',
          }}
        >
          <h3 style={{ fontWeight: 700, marginBottom: '0.75rem', fontSize: '1rem' }}>Recruiter Analysis</h3>
          <p style={{ color: '#a0a0c0', fontSize: '0.875rem', lineHeight: 1.6 }}>{result.reasoning}</p>
        </div>
      )}

      {missingSkills.length > 0 && (
        <div
          style={{
            background: 'rgba(15,15,26,0.9)',
            border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: '1.25rem',
            padding: '1.5rem',
          }}
        >
          <h3 style={{ fontWeight: 700, marginBottom: '1rem', fontSize: '1rem' }}>Missing Keywords</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {missingSkills.map((keyword, index) => (
              <span
                key={`${keyword}-${index}`}
                style={{
                  padding: '0.25rem 0.75rem',
                  borderRadius: '99px',
                  fontSize: '0.8rem',
                  background: 'rgba(239,68,68,0.1)',
                  border: '1px solid rgba(239,68,68,0.25)',
                  color: '#f87171',
                }}
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}

      {suggestions.length > 0 && (
        <div
          style={{
            background: 'rgba(15,15,26,0.9)',
            border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: '1.25rem',
            padding: '1.5rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
          }}
        >
          <h3 style={{ fontWeight: 700, fontSize: '1rem' }}>AI Actionable Suggestions</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {suggestions.map((suggestion: AnalysisSuggestion, index) => (
              <div
                key={`${suggestion.title}-${index}`}
                style={{
                  padding: '1rem',
                  borderRadius: '0.75rem',
                  background: 'rgba(124,58,237,0.04)',
                  border: '1px solid rgba(124,58,237,0.1)',
                }}
              >
                <div style={{ fontWeight: 600, color: '#c4b5fd', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                  {suggestion.title}
                </div>
                <div style={{ color: '#a0a0c0', fontSize: '0.825rem', lineHeight: 1.5 }}>{suggestion.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.rewritten_resume && (
        <div
          style={{
            background: 'rgba(15,15,26,0.9)',
            border: '1px solid rgba(124,58,237,0.15)',
            borderRadius: '1.25rem',
            overflow: 'hidden',
          }}
        >
          <button
            onClick={() => setShowRewrite((current) => !current)}
            style={{
              width: '100%',
              padding: '1.25rem 1.5rem',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              color: '#f0f0ff',
              fontWeight: 700,
              fontSize: '1rem',
            }}
          >
            <span>✨ AI-Rewritten Resume Preview</span>
            {showRewrite ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </button>
          {showRewrite && (
            <div style={{ padding: '0 1.5rem 1.5rem' }}>
              <pre
                style={{
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  fontSize: '0.825rem',
                  color: '#c4c4e0',
                  lineHeight: 1.6,
                  background: 'rgba(0,0,0,0.3)',
                  borderRadius: '0.75rem',
                  padding: '1.25rem',
                  maxHeight: '500px',
                  overflowY: 'auto',
                }}
              >
                {result.rewritten_resume}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
