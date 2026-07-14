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
    return <div className="text-muted-foreground text-center py-16">Loading analysis details...</div>;
  }

  if (!result) {
    return (
      <div className="text-foreground text-center py-16 px-6">
        <AlertCircle size={48} className="mx-auto text-red-500" />
        <h2 className="font-semibold mt-4 mb-2">Analysis Not Found</h2>
        <p className="text-sm text-muted-foreground mb-4">
          This analysis record does not exist or you do not have permission to view it.
        </p>
        <Link href="/history" className="inline-flex items-center px-4 py-2 rounded-md border border-border text-muted-foreground hover:bg-muted">← Back to History</Link>
      </div>
    );
  }

  const matchScore = result.match_score ?? result.skill_match_percentage ?? 0;
  const atsScore = result.ats_score ?? 0;
  const missingSkills = result.missing_skills ?? [];
  const suggestions = result.suggestions ?? [];

  return (
    <div className="max-w-3xl w-full mx-auto text-foreground flex flex-col gap-6">
      <div>
        <Link href="/history" className="inline-flex items-center gap-2 text-primary text-sm font-medium mb-2"><ChevronLeft size={16} /> Back to History</Link>
        <h1 className="text-2xl sm:text-3xl font-extrabold mb-1">Analysis Results</h1>
        <p className="text-sm text-muted-foreground">Detailed breakdown of your resume match.</p>
      </div>

      <div className="bg-card border border-border rounded-2xl p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {[
            { label: 'Match Score', value: `${matchScore}%`, score: matchScore },
            { label: 'ATS Score', value: atsScore, score: atsScore },
          ].map((scoreCard) => (
            <div key={scoreCard.label} className="p-4 rounded-lg text-center bg-muted/5 border">
              <div className={`text-3xl font-extrabold ${scoreCard.score >= 75 ? 'text-green-500' : scoreCard.score >= 50 ? 'text-yellow-500' : 'text-red-500'}`}>{scoreCard.value}</div>
              <div className="text-sm text-muted-foreground mt-1">{scoreCard.label}</div>
            </div>
          ))}
        </div>
      </div>

      {result.reasoning && (
        <div className="bg-card border border-primary/20 rounded-2xl p-4">
          <h3 className="font-semibold mb-2">Recruiter Analysis</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">{result.reasoning}</p>
        </div>
      )}

      {missingSkills.length > 0 && (
        <div className="bg-card border border-border rounded-2xl p-4">
          <h3 className="font-semibold mb-4">Missing Keywords</h3>
          <div className="flex flex-wrap gap-2">
            {missingSkills.map((keyword, index) => (
              <span key={`${keyword}-${index}`} className="px-3 py-1 rounded-full text-sm bg-red-900/10 border border-red-900/20 text-red-400">{keyword}</span>
            ))}
          </div>
        </div>
      )}

      {suggestions.length > 0 && (
        <div className="bg-card border border-border rounded-2xl p-4 flex flex-col gap-4">
          <h3 className="font-semibold">AI Actionable Suggestions</h3>
          <div className="flex flex-col gap-3">
            {suggestions.map((suggestion: AnalysisSuggestion, index) => (
              <div key={`${suggestion.title}-${index}`} className="p-4 rounded-lg bg-primary/5 border border-primary/10">
                <div className="font-medium text-primary mb-1">{suggestion.title}</div>
                <div className="text-sm text-muted-foreground">{suggestion.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.rewritten_resume && (
        <div className="bg-card border border-primary/10 rounded-2xl overflow-hidden">
          <button
            onClick={() => setShowRewrite((current) => !current)}
            className="w-full px-6 py-4 bg-transparent text-foreground flex items-center justify-between font-semibold"
          >
            <span>✨ AI-Rewritten Resume Preview</span>
            {showRewrite ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </button>
          {showRewrite && (
            <div className="p-4">
              <pre className="whitespace-pre-wrap break-words text-sm text-muted-foreground leading-relaxed bg-muted/20 rounded-lg p-4 max-h-[500px] overflow-y-auto">{result.rewritten_resume}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
