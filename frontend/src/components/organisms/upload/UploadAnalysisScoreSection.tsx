'use client';

import { CheckCircle2 } from 'lucide-react';
import type { AtsAnalysisResult } from '@/types/analysis';

interface BreakdownBarItem {
  label: string;
  weight: string;
  value: number;
  hidden?: boolean;
}

const scoreColor = (score: number) =>
  score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444';

const formatWeight = (weight?: number) =>
  weight != null ? `${Math.round(weight * 100)}%` : '';

function BreakdownBars({ title, items }: { title: string; items: BreakdownBarItem[] }) {
  return (
    <div
      style={{
        background: 'rgba(15,15,26,0.9)',
        border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: '1.25rem',
        padding: '1.5rem',
      }}
    >
      <h3 style={{ fontWeight: 700, marginBottom: '1rem', fontSize: '1rem' }}>{title}</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
        {items.map((item) => (
          <div key={item.label}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '0.35rem',
                fontSize: '0.825rem',
              }}
            >
              <span style={{ color: '#c4c4e0' }}>
                {item.label} <span style={{ color: '#666688' }}>({item.weight})</span>
              </span>
              <span style={{ fontWeight: 700, color: scoreColor(item.value) }}>{Math.round(item.value)}%</span>
            </div>
            <div
              style={{
                height: '6px',
                borderRadius: '99px',
                background: 'rgba(255,255,255,0.06)',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  width: `${Math.min(100, item.value)}%`,
                  height: '100%',
                  borderRadius: '99px',
                  background: scoreColor(item.value),
                  transition: 'width 0.4s ease',
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function UploadAnalysisScoreSection({ result }: { result: AtsAnalysisResult }) {
  const matchWeights = result.score_weights?.match_weights ?? {};
  const atsWeights = result.score_weights?.ats_weights ?? {};
  const applicable = result.score_weights?.applicable_sections ?? {};
  const matchScores = result.match_breakdown ?? {};
  const atsScores = result.breakdown ?? {};
  const matchScore = result.match_score ?? result.skill_match_percentage ?? 0;
  const atsScore = result.ats_score ?? 0;

  const matchBreakdown: BreakdownBarItem[] = [
    {
      label: 'Required Skills',
      weight: formatWeight(matchWeights.required_skills) || '30%',
      value: matchScores.required_skills ?? result.keyword_score ?? 0,
    },
    {
      label: 'Responsibilities',
      weight: formatWeight(matchWeights.responsibilities) || '20%',
      value: matchScores.responsibilities ?? 0,
      hidden: applicable.responsibilities === false,
    },
    {
      label: 'Experience',
      weight: formatWeight(matchWeights.experience) || '25%',
      value: matchScores.experience ?? result.experience_score ?? 0,
    },
    {
      label: 'Projects',
      weight: formatWeight(matchWeights.projects) || '15%',
      value: matchScores.projects ?? result.project_score ?? 0,
      hidden: applicable.projects === false,
    },
    {
      label: 'Preferred Skills',
      weight: formatWeight(matchWeights.preferred_skills) || '10%',
      value: matchScores.preferred_skills ?? 0,
      hidden: applicable.preferred_skills === false,
    },
  ].filter((item) => !item.hidden);

  const atsBreakdown: BreakdownBarItem[] = [
    {
      label: 'Keywords',
      weight: formatWeight(atsWeights.required_skills) || '20%',
      value: atsScores.keyword ?? result.keyword_score ?? 0,
    },
    {
      label: 'Semantic Fit',
      weight: formatWeight(atsWeights.semantic) || '25%',
      value: atsScores.semantic ?? result.semantic_score ?? 0,
    },
    {
      label: 'Experience',
      weight: formatWeight(atsWeights.experience) || '20%',
      value: atsScores.experience ?? result.experience_score ?? 0,
    },
    {
      label: 'Projects',
      weight: formatWeight(atsWeights.projects) || '10%',
      value: atsScores.projects ?? result.project_score ?? 0,
      hidden: applicable.projects === false,
    },
    {
      label: 'Formatting',
      weight: formatWeight(atsWeights.formatting) || '20%',
      value: atsScores.formatting ?? result.formatting_score ?? 0,
    },
    {
      label: 'Education',
      weight: formatWeight(atsWeights.education) || '5%',
      value: atsScores.education ?? result.education_score ?? 0,
      hidden: applicable.education === false && applicable.certifications === false,
    },
  ].filter((item) => !item.hidden);

  return (
    <>
      <div
        style={{
          background: 'rgba(15,15,26,0.9)',
          border: '1px solid rgba(255,255,255,0.06)',
          borderRadius: '1.25rem',
          padding: '2rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <CheckCircle2 size={22} color="#10b981" />
          <h2 style={{ fontWeight: 700, fontSize: '1.1rem' }}>Analysis Complete</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          {[
            { label: 'Match Score', value: `${matchScore}%`, score: matchScore },
            { label: 'ATS Score', value: atsScore, score: atsScore },
          ].map((item) => (
            <div
              key={item.label}
              style={{
                padding: '1.5rem',
                borderRadius: '1rem',
                textAlign: 'center',
                background: `${scoreColor(item.score)}12`,
                border: `1px solid ${scoreColor(item.score)}25`,
              }}
            >
              <div style={{ fontSize: '2.5rem', fontWeight: 900, color: scoreColor(item.score), lineHeight: 1 }}>
                {item.value}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#8888aa', marginTop: '0.375rem' }}>{item.label}</div>
            </div>
          ))}
        </div>
        <p style={{ marginTop: '1rem', fontSize: '0.8rem', color: '#8888aa', lineHeight: 1.5 }}>
          <strong style={{ color: '#c4c4e0' }}>Match Score</strong> — how well your resume fits this specific job
          (skills + responsibilities weighted heavily).{' '}
          <strong style={{ color: '#c4c4e0' }}>ATS Score</strong> — overall resume quality for applicant tracking
          systems.
        </p>
      </div>

      <BreakdownBars title="Where Match Score Comes From" items={matchBreakdown} />
      <BreakdownBars title="Where ATS Score Comes From" items={atsBreakdown} />
    </>
  );
}
