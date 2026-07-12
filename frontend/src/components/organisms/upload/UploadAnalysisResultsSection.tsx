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
        <div
          style={{
            background: 'rgba(15,15,26,0.9)',
            border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: '1.25rem',
            padding: '1.5rem',
          }}
        >
          <h3 style={{ fontWeight: 700, marginBottom: '1rem', fontSize: '1rem' }}>Matched Keywords</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {matchedSkills.map((keyword, index) => (
              <span
                key={`${keyword}-${index}`}
                style={{
                  padding: '0.25rem 0.75rem',
                  borderRadius: '99px',
                  fontSize: '0.8rem',
                  background: 'rgba(16,185,129,0.1)',
                  border: '1px solid rgba(16,185,129,0.25)',
                  color: '#34d399',
                }}
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}

      {reasoning && (
        <div
          style={{
            background: 'rgba(15,15,26,0.9)',
            border: '1px solid rgba(124,58,237,0.15)',
            borderRadius: '1.25rem',
            padding: '1.5rem',
          }}
        >
          <h3 style={{ fontWeight: 700, marginBottom: '0.75rem', fontSize: '1rem' }}>Recruiter Analysis</h3>
          <p style={{ color: '#a0a0c0', fontSize: '0.875rem', lineHeight: 1.6 }}>{reasoning}</p>
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
            gap: '0.75rem',
          }}
        >
          <h3 style={{ fontWeight: 700, marginBottom: '0.25rem', fontSize: '1rem' }}>AI Suggestions</h3>
          {suggestions.map((suggestion, index) => (
            <div
              key={`${suggestion.title}-${index}`}
              style={{
                padding: '0.875rem',
                borderRadius: '0.75rem',
                background: 'rgba(124,58,237,0.04)',
                border: '1px solid rgba(124,58,237,0.1)',
              }}
            >
              <div style={{ fontWeight: 600, color: '#c4b5fd', fontSize: '0.875rem', marginBottom: '0.2rem' }}>
                {suggestion.title}
              </div>
              <div style={{ color: '#a0a0c0', fontSize: '0.825rem', lineHeight: 1.5 }}>{suggestion.description}</div>
            </div>
          ))}
        </div>
      )}

      {rewrittenResume && (
        <div
          style={{
            background: 'rgba(15,15,26,0.9)',
            border: '1px solid rgba(124,58,237,0.15)',
            borderRadius: '1.25rem',
            overflow: 'hidden',
          }}
        >
          <button
            onClick={onToggleRewrite}
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
            <span>✨ AI-Rewritten Resume</span>
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
                {rewrittenResume}
              </pre>
            </div>
          )}
        </div>
      )}

      <button
        onClick={onReset}
        style={{
          padding: '0.75rem',
          borderRadius: '0.75rem',
          background: 'rgba(255,255,255,0.05)',
          border: '1px solid rgba(255,255,255,0.1)',
          color: '#c4c4e0',
          fontWeight: 600,
          cursor: 'pointer',
          fontSize: '0.9rem',
        }}
      >
        ← Analyze Another Resume
      </button>
    </>
  );
}
