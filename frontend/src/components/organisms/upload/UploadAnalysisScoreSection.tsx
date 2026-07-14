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
    <div className="bg-card border border-border rounded-2xl p-4">
      <h3 className="font-semibold mb-4">{title}</h3>
      <div className="flex flex-col gap-3">
        {items.map((item) => (
          <div key={item.label}>
            <div className="flex justify-between mb-1 text-sm">
              <span className="text-muted-foreground">
                {item.label} <span className="text-muted-foreground/70">({item.weight})</span>
              </span>
              <span className="font-bold" style={{ color: scoreColor(item.value) }}>{Math.round(item.value)}%</span>
            </div>
            <div className="h-1.5 rounded-full bg-muted overflow-hidden">
              <div style={{ width: `${Math.min(100, item.value)}%`, background: scoreColor(item.value), transition: 'width 0.4s ease' }} className="h-full" />
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
      <div className="bg-card border border-border rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <CheckCircle2 size={22} color="#10b981" />
          <h2 className="font-bold text-lg">Analysis Complete</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {[
            { label: 'Match Score', value: `${matchScore}%`, score: matchScore },
            { label: 'ATS Score', value: atsScore, score: atsScore },
          ].map((item) => (
            <div key={item.label} className="p-6 rounded-lg text-center" style={{ background: `${scoreColor(item.score)}12`, border: `1px solid ${scoreColor(item.score)}25` }}>
              <div className="text-4xl font-extrabold" style={{ color: scoreColor(item.score), lineHeight: 1 }}>{item.value}</div>
              <div className="text-sm text-muted-foreground mt-1">{item.label}</div>
            </div>
          ))}
        </div>
        <p className="mt-4 text-sm text-muted-foreground leading-relaxed">
          <strong className="text-muted-foreground/90">Match Score</strong> — how well your resume fits this specific job
          (skills + responsibilities weighted heavily).{' '}
          <strong className="text-muted-foreground/90">ATS Score</strong> — overall resume quality for applicant tracking
          systems.
        </p>
      </div>

      <BreakdownBars title="Where Match Score Comes From" items={matchBreakdown} />
      <BreakdownBars title="Where ATS Score Comes From" items={atsBreakdown} />
    </>
  );
}
