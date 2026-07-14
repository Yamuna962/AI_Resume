'use client';

import { ChevronDown, ChevronUp } from 'lucide-react';
import type { AtsAnalysisResult } from '@/types/analysis';

interface UploadAnalysisResultsSectionProps {
  result: AtsAnalysisResult;
  showRewrite: boolean;
  onToggleRewrite: () => void;
  onReset: () => void;
}

export function UploadAnalysisResultsSection({
  result,
  showRewrite,
  onToggleRewrite,
  onReset,
}: UploadAnalysisResultsSectionProps) {
  const matchedSkills = result.matched_skills ?? [];
  const missingSkills = result.missing_skills ?? [];
  const suggestions = result.suggestions ?? [];
  const reasoning = result.reasoning;
  const rewrittenResume = result.rewritten_resume;

  return (
    <>
      {matchedSkills.length > 0 && (
        <div className="bg-card border border-border rounded-2xl p-6">
          <h3 className="font-bold mb-4">Matched Keywords</h3>
          <div className="flex flex-wrap gap-2">
            {matchedSkills.map((keyword, index) => (
              <span
                key={`${keyword}-${index}`}
                className="px-3 py-1 rounded-full text-sm bg-green-500/10 border border-green-500/25 text-green-400"
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}

      {reasoning && (
        <div className="bg-card border border-primary/20 rounded-2xl p-6">
          <h3 className="font-bold mb-3">Recruiter Analysis</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">{reasoning}</p>
        </div>
      )}

      {missingSkills.length > 0 && (
        <div className="bg-card border border-border rounded-2xl p-6">
          <h3 className="font-bold mb-4">Missing Keywords</h3>
          <div className="flex flex-wrap gap-2">
            {missingSkills.map((keyword, index) => (
              <span
                key={`${keyword}-${index}`}
                className="px-3 py-1 rounded-full text-sm bg-red-500/10 border border-red-500/25 text-red-400"
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}

      {suggestions.length > 0 && (
        <div className="bg-card border border-border rounded-2xl p-6 flex flex-col gap-3">
          <h3 className="font-bold">AI Suggestions</h3>
          {suggestions.map((suggestion, index) => (
            <div
              key={`${suggestion.title}-${index}`}
              className="p-4 rounded-lg bg-primary/5 border border-primary/10"
            >
              <div className="font-semibold text-primary text-sm mb-1">{suggestion.title}</div>
              <div className="text-sm text-muted-foreground leading-relaxed">{suggestion.description}</div>
            </div>
          ))}
        </div>
      )}

      {rewrittenResume && (
        <div className="bg-card border border-primary/15 rounded-2xl overflow-hidden">
          <button
            onClick={onToggleRewrite}
            className="w-full px-6 py-4 bg-transparent text-foreground flex items-center justify-between font-semibold"
          >
            <span>✨ AI-Rewritten Resume</span>
            {showRewrite ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </button>
          {showRewrite && (
            <div className="px-6 pb-6">
              <pre className="whitespace-pre-wrap break-words text-sm text-muted-foreground leading-relaxed bg-muted/20 rounded-lg p-4 max-h-[500px] overflow-y-auto">
                {rewrittenResume}
              </pre>
            </div>
          )}
        </div>
      )}

      <button
        onClick={onReset}
        className="px-4 py-3 rounded-lg bg-muted/50 border border-border text-foreground font-semibold text-sm hover:bg-muted transition-colors"
      >
        ← Analyze Another Resume
      </button>
    </>
  );
}
